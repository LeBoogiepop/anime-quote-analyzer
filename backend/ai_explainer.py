"""
AI-powered explanation generator using OpenRouter (Perplexity Sonar) or Google Gemini.

This module provides intelligent, contextualized explanations for Japanese sentences
using OpenRouter/Perplexity Sonar Small or Gemini 1.5 Flash. Features include:
- LRU cache with 24h TTL to save API quota
- Robust error handling with retry logic
- Graceful degradation if API unavailable
- JSON response validation
- Support for multiple AI providers (OpenRouter, Gemini)

Author: Maxime
"""

import os
import json
import time
import logging
import hashlib
import re
from typing import Dict, List, Any, Optional
from functools import lru_cache
from datetime import datetime, timedelta
from pathlib import Path

import httpx
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "none")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "perplexity/sonar-small-chat")
CACHE_MAX_SIZE = 500
CACHE_TTL_HOURS = 24
API_TIMEOUT_SECONDS = 15  # 15s timeout for AI generation
MAX_RETRIES = 2  # 2 retries with exponential backoff

# Initialize Gemini (only if provider is gemini)
_gemini_model = None
_cache_data: Dict[str, Dict[str, Any]] = {}


def _initialize_gemini():
    """Initialize Gemini API with error handling."""
    global _gemini_model

    if AI_PROVIDER != "gemini":
        logger.info("AI provider not set to 'gemini', AI explanations disabled")
        return False

    if not GEMINI_API_KEY or GEMINI_API_KEY == "your-gemini-api-key-here":
        logger.warning("GEMINI_API_KEY not configured, AI explanations disabled")
        return False

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel(AI_MODEL)
        logger.info(f"✓ Gemini AI initialized successfully (model: {AI_MODEL})")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini: {e}")
        return False


def _get_cache_key(sentence: str, tokens: List[Dict], grammar: List[Dict], vocab: List[Dict]) -> str:
    """Generate a unique cache key for the analysis."""
    # Create a hash based on sentence and analysis data
    data_str = json.dumps({
        "sentence": sentence,
        "tokens": [t.get("surface", "") for t in tokens],
        "grammar": [g.get("pattern", "") for g in grammar],
        "vocab": [v.get("word", "") for v in vocab]
    }, ensure_ascii=False, sort_keys=True)

    return hashlib.md5(data_str.encode('utf-8')).hexdigest()


def _get_from_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """Retrieve explanation from cache if valid."""
    if cache_key not in _cache_data:
        return None

    cached = _cache_data[cache_key]

    # Check TTL
    cache_time = datetime.fromisoformat(cached["timestamp"])
    if datetime.now() - cache_time > timedelta(hours=CACHE_TTL_HOURS):
        # Cache expired
        del _cache_data[cache_key]
        return None

    logger.info(f"Cache hit for key: {cache_key[:8]}...")
    return cached["data"]


def _save_to_cache(cache_key: str, data: Dict[str, Any]):
    """Save explanation to cache."""
    global _cache_data

    # Implement simple LRU: remove oldest if at capacity
    if len(_cache_data) >= CACHE_MAX_SIZE:
        oldest_key = min(_cache_data.keys(),
                        key=lambda k: datetime.fromisoformat(_cache_data[k]["timestamp"]))
        del _cache_data[oldest_key]
        logger.debug(f"Cache full, removed oldest entry: {oldest_key[:8]}...")

    _cache_data[cache_key] = {
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"Cached explanation (total: {len(_cache_data)}/{CACHE_MAX_SIZE})")


def _format_tokens_for_prompt(tokens: List[Dict]) -> str:
    """Format tokens for the AI prompt."""
    formatted = []
    for token in tokens[:15]:  # Limit to first 15 tokens
        surface = token.get("surface", "")
        reading = token.get("reading", "")
        pos = token.get("partOfSpeech", "")
        formatted.append(f"{surface} ({reading}) [{pos}]")

    return ", ".join(formatted)


def _format_grammar_for_prompt(grammar_patterns: List[Dict]) -> str:
    """Format grammar patterns for the AI prompt."""
    formatted = []
    for pattern in grammar_patterns[:5]:  # Limit to first 5 patterns
        pat = pattern.get("pattern", "")
        desc = pattern.get("description", "")
        level = pattern.get("jlptLevel", "")
        formatted.append(f"- {pat} ({level}): {desc}")

    return "\n".join(formatted)


def _format_vocab_for_prompt(vocab_items: List[Dict]) -> str:
    """Format vocabulary for the AI prompt."""
    formatted = []
    for vocab in vocab_items[:8]:  # Limit to first 8 words
        word = vocab.get("word", "")
        reading = vocab.get("reading", "")
        meaning = vocab.get("meaning", "")
        level = vocab.get("jlptLevel", "")
        formatted.append(f"- {word} ({reading}): {meaning} [{level}]")

    return "\n".join(formatted)


def _build_prompt(sentence: str, tokens: List[Dict], grammar: List[Dict], vocab: List[Dict]) -> str:
    """Build the complete prompt for Gemini."""
    tokens_str = _format_tokens_for_prompt(tokens)
    grammar_str = _format_grammar_for_prompt(grammar)
    vocab_str = _format_vocab_for_prompt(vocab)
    
    # Detect JLPT level from grammar patterns or vocab (use highest level found)
    jlpt_level = "N5"  # Default
    if grammar:
        levels = [g.get("jlptLevel", "N5") for g in grammar]
        # N5 < N4 < N3 < N2 < N1, so find the "lowest" number
        level_order = {"N5": 5, "N4": 4, "N3": 3, "N2": 2, "N1": 1}
        jlpt_level = min(levels, key=lambda x: level_order.get(x, 5))
    elif vocab:
        levels = [v.get("jlptLevel", "N5") for v in vocab]
        level_order = {"N5": 5, "N4": 4, "N3": 3, "N2": 2, "N1": 1}
        jlpt_level = min(levels, key=lambda x: level_order.get(x, 5))
    
    # Adapt instructions based on JLPT level
    if jlpt_level in ["N5", "N4"]:
        level_instructions = """
ADAPTATION NIVEAU DÉBUTANT ({jlpt_level}) :
- Explique la PHRASE COMPLÈTE d'abord, puis seulement 2-3 points grammaticaux MAX
- Ne décompose PAS chaque particule séparément (は, を, が) sauf si vraiment nécessaire
- Utilise un vocabulaire simple et évite les termes techniques
- 1-2 phrases par explication, pas plus
- Focus sur "comment dire X" plutôt que "pourquoi la structure est comme ça"
"""
    elif jlpt_level in ["N3"]:
        level_instructions = """
ADAPTATION NIVEAU INTERMÉDIAIRE ({jlpt_level}) :
- Explique la phrase globale puis 3-4 points grammaticaux max
- Tu peux expliquer les particules importantes si elles apportent une nuance
- 2-3 phrases par explication
- Équilibre entre sens et structure
"""
    else:  # N2, N1
        level_instructions = """
ADAPTATION NIVEAU AVANCÉ ({jlpt_level}) :
- Tu peux être plus détaillé sur les nuances grammaticales
- Explique les subtilités et registres de langue
- 3-4 phrases par explication si nécessaire
- Focus sur les nuances et usages avancés
"""

    prompt = f"""Tu es un professeur de japonais professionnel qui enseigne à des francophones passionnés d'anime. Tu expliques de manière claire et pédagogique, comme un vrai enseignant, PAS comme un dictionnaire.

Phrase japonaise : "{sentence}"
Niveau JLPT détecté : {jlpt_level}

Données linguistiques :
{tokens_str}
{grammar_str}
{vocab_str}

MISSION : Explique cette phrase de manière PÉDAGOGIQUE et PROFESSIONNELLE. Ne traduis PAS la phrase complète - l'utilisateur a déjà accès à une traduction séparée.

REGLES ABSOLUES :
1. ZERO PARENTHESE nulle part
   - Écris "私" PAS "私(わたし)"
   - Écris "飲める" PAS "飲める(のめる)"

2. TON PROFESSIONNEL ET PÉDAGOGIQUE
   - Parle comme un professeur expérimenté qui explique à ses étudiants
   - Évite de commencer chaque phrase par "Tu" - varie les formulations
   - Utilise des formulations variées : "Cette structure exprime...", "On utilise...", "Cette particule marque...", "Le verbe indique..."
   - Évite le jargon technique inutile mais reste précis
   - Ton clair et pédagogique, pas trop familier

   ❌ Mauvais (trop familier): "Tu dis qu'avant c'était pas comme ça. Le 'ja' rend ça familier entre amis."
   ✅ Bon (professionnel): "Cette structure exprime une action passée dans un registre familier. La particule 'ja' indique un niveau de langue décontracté, utilisé entre amis."

3. NE TRADUIS PAS LA PHRASE COMPLÈTE
   - L'utilisateur a déjà un bouton de traduction séparé
   - Va directement aux explications grammaticales et de vocabulaire
   - Ne commence PAS par "Cette phrase signifie..." ou "Tu dis que..."

4. IDENTIFIE ET MENTIONNE LES FORMES GRAMMATICALES
   - Si un verbe est à une forme particulière (potentielle, passive, causative, etc.), MENTIONNE-LE explicitement
   - Format : "Forme potentielle du verbe 飲む" ou "Forme passive de..." ou "Forme causative..."
   - Ensuite explique ce que cette forme exprime
   - Exemples de formes à identifier : potentielle (飲める), passive (飲まれる), causative (飲ませる), causatif-passif (飲まされる), etc.

5. EXPLICATIONS COMPLETES MAIS CONCISES
   - Explique seulement les points grammaticaux IMPORTANTS (pas chaque particule)
   - 2-3 phrases par point grammatical max
   - Phrase 1: Identifie la forme grammaticale si présente, puis ce qu'elle exprime (le sens)
   - Phrase 2: Comment/quand l'utilise-t-on?
   - Phrase 3 (optionnelle): Pourquoi/nuance particulière?

6. ÉVITE LES RÉPÉTITIONS
   - Si tu expliques "～ています" une fois, ne le répète pas ailleurs
   - Si tu expliques une particule dans un contexte, ne la réexplique pas ailleurs
   - Regroupe les explications similaires

7. EXEMPLES SIMPLES
   - 3-5 mots maximum
   - PAS tirés de la phrase originale
   - Faciles à retenir

{level_instructions.format(jlpt_level=jlpt_level)}

Génère un JSON valide avec cette structure EXACTE :
{{
  "grammarNotes": [
    {{"pattern": "forme", "explanation": "Explication naturelle en 2-3 phrases max, commence par le sens/usage", "example": "Exemple simple"}}
  ],
  "vocabNotes": [
    {{"word": "mot", "nuance": "Explication conversationnelle de la nuance (1-2 phrases max)"}}
  ],
  "culturalContext": "Note culturelle naturelle si pertinent sinon null",
  "studyTips": "Conseil pratique conversationnel (1 phrase max)",
  "registerNote": "Niveau de langue expliqué naturellement (1 phrase max)"
}}

EXEMPLES DE BON TON :
- grammarNotes (avec forme identifiée): "Forme potentielle du verbe 飲む. Cette structure exprime la capacité ou la possibilité de boire, et non simplement l'action de boire. On l'utilise pour dire qu'une compétence est acquise ou qu'une condition permet enfin cette action."
- grammarNotes (sans forme spécifique): "Cette structure exprime une difficulté ou une aversion modérée. Plus doux que 'je déteste', elle indique plutôt une gêne ou un manque d'aisance. S'utilise pour la musique, les mathématiques, les personnes, etc."
- vocabNotes: "Exprime une gêne ou un inconfort modéré. Plus nuancé qu'une aversion totale, cette expression permet d'exprimer une difficulté sans être trop direct."
- culturalContext: "Au Japon, on préfère exprimer une difficulté plutôt que de critiquer directement. Cette approche indirecte est considérée comme plus polie."
- studyTips: "Comparable à 'I'm not good with' en anglais - exprime un inconfort sans hostilité."
- registerNote: "Utilisé dans des contextes décontractés ou entre amis. Trop familier pour un contexte professionnel formel."

IMPORTANT :
- Réponds uniquement avec du JSON valide
- ZERO parenthèse nulle part
- Ton professionnel et pédagogique, pas encyclopédique
- NE TRADUIS PAS la phrase complète - va directement aux explications
- Pour {jlpt_level}: MAX 3-4 points grammaticaux, pas plus
- Évite de répéter la même explication plusieurs fois
- Varie les formulations, évite de commencer chaque phrase par "Tu" """

    return prompt


def _get_fallback_explanation() -> Dict[str, Any]:
    """
    Return a generic fallback explanation when AI response parsing fails.
    This prevents 503 errors and provides basic functionality.
    """
    return {
        "grammarNotes": [],
        "vocabNotes": [],
        "culturalContext": None,
        "studyTips": "L'IA n'a pas pu générer une explication détaillée. Utilisez les informations de grammaire et de vocabulaire ci-dessus, et décomposez la phrase en parties plus petites.",
        "registerNote": None
    }


def _sanitize_json_string(content: str) -> str:
    """
    Sanitize JSON string to fix common issues from AI responses.
    Handles unescaped quotes, newlines, and other problematic characters.
    Multiple passes for aggressive cleaning.
    """
    try:
        # Try parsing as-is first
        json.loads(content)
        return content
    except json.JSONDecodeError as e:
        logger.warning(f"JSON needs sanitization: {e}")

        sanitized = content

        logger.info("Attempting aggressive JSON sanitization...")

        # Pass 1: Fix literal newlines and tabs
        # Replace any literal newlines (not \n) with \\n
        sanitized = re.sub(r'(?<!\\)\n', r'\\n', sanitized)
        # Replace any literal tabs with \\t
        sanitized = re.sub(r'(?<!\\)\t', r'\\t', sanitized)

        # Pass 2: Remove trailing commas before closing brackets/braces
        # This is a common issue with AI-generated JSON
        sanitized = re.sub(r',(\s*[}\]])', r'\1', sanitized)

        # Pass 3: Fix control characters
        # Remove or escape common control characters
        sanitized = sanitized.replace('\r', '')
        sanitized = sanitized.replace('\b', '')
        sanitized = sanitized.replace('\f', '')

        # Pass 4: Try to fix unescaped quotes in string values (heuristic)
        # This is tricky - we look for patterns like: "text "quoted" text"
        # and try to escape the inner quotes
        # Pattern: Find strings with unescaped quotes between key-value strings
        def escape_inner_quotes(match):
            # Get the full string value
            full_str = match.group(0)
            # If it has more than 2 quotes, we have a problem
            if full_str.count('"') > 2:
                # Escape all quotes except the first and last
                parts = full_str.split('"')
                if len(parts) > 2:
                    # Keep first empty part, last empty part, escape middle
                    result = '"' + '\\"'.join(parts[1:-1]) + '"'
                    return result
            return full_str

        # This regex is risky, but we'll try it as a last resort
        # Match string values: "key": "value with possible "quotes" inside"
        # sanitized = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', escape_inner_quotes, sanitized)

        # Try parsing after basic sanitization
        try:
            json.loads(sanitized)
            logger.info("JSON sanitization successful (basic pass)")
            return sanitized
        except json.JSONDecodeError as e2:
            logger.warning(f"Basic sanitization failed: {e2}")

            # Pass 5: More aggressive - try to fix common patterns
            # Remove any null bytes
            sanitized = sanitized.replace('\x00', '')

            # Try one more time
            try:
                json.loads(sanitized)
                logger.info("JSON sanitization successful (aggressive pass)")
                return sanitized
            except json.JSONDecodeError as e3:
                logger.error(f"All sanitization attempts failed: {e3}")
                # Return original and let fallback handle it
                return content


def _validate_response(response_data: Dict[str, Any]) -> bool:
    """Validate the structure of the AI response."""
    required_fields = ["grammarNotes", "vocabNotes", "studyTips"]

    for field in required_fields:
        if field not in response_data:
            logger.error(f"Missing required field in AI response: {field}")
            return False

    # Validate grammarNotes structure
    if not isinstance(response_data["grammarNotes"], list):
        logger.error("grammarNotes must be a list")
        return False

    for note in response_data["grammarNotes"]:
        if not all(k in note for k in ["pattern", "explanation"]):
            logger.error("Invalid grammarNote structure")
            return False

    # Validate vocabNotes structure
    if not isinstance(response_data["vocabNotes"], list):
        logger.error("vocabNotes must be a list")
        return False

    for note in response_data["vocabNotes"]:
        if not all(k in note for k in ["word", "nuance"]):
            logger.error("Invalid vocabNote structure")
            return False

    return True


def _call_openrouter_api(prompt: str) -> Optional[Dict[str, Any]]:
    """Call OpenRouter API (Perplexity Sonar Small) with error handling."""
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-api-key-here":
        logger.warning("OPENROUTER_API_KEY not configured, AI explanations disabled")
        return None

    try:
        logger.info("Calling OpenRouter API (Perplexity Sonar Small)...")
        start_time = time.time()

        # Prepare headers required by OpenRouter
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/LeBoogiepop/anime-quote-analyzer",
            "X-Title": "Anime Quote Analyzer"
        }

        # Prepare payload
        payload = {
            "model": AI_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.6,
            "max_tokens": 800
        }

        # Make request with httpx
        with httpx.Client(timeout=API_TIMEOUT_SECONDS) as client:
            response = client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()

        duration = time.time() - start_time
        logger.info(f"✓ OpenRouter API responded in {duration:.2f}s")

        # Extract response
        result = response.json()

        if "choices" not in result or len(result["choices"]) == 0:
            logger.error("Invalid response from OpenRouter: no choices")
            return None

        content = result["choices"][0]["message"]["content"]

        # Clean response text (remove markdown code blocks if present)
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        if content.startswith("```"):
            content = content[3:]  # Remove ```
        if content.endswith("```"):
            content = content[:-3]  # Remove ```
        content = content.strip()

        # Sanitize JSON to fix common issues
        content = _sanitize_json_string(content)

        # Parse JSON
        try:
            response_data = json.loads(content)

            # Validate structure
            if not _validate_response(response_data):
                logger.error("Invalid response structure from OpenRouter")
                logger.error(f"Response data: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                return None

            return response_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenRouter response as JSON: {e}")
            logger.error(f"Full response content (first 500 chars): {content[:500]}")
            logger.error(f"Response length: {len(content)} characters")
            # Print full content to console for debugging
            print("\n" + "="*60)
            print("FULL API RESPONSE CONTENT:")
            print("="*60)
            print(content)
            print("="*60 + "\n")

            # Return fallback explanation instead of None
            logger.warning("Returning fallback explanation due to JSON parse error")
            return _get_fallback_explanation()

    except json.JSONDecodeError as parse_error:
        logger.error(f"Failed to parse API response JSON: {parse_error}")
        return _get_fallback_explanation()

    except httpx.HTTPError as e:
        logger.error(f"OpenRouter API HTTP error: {e}")
        return None
    except Exception as e:
        logger.error(f"OpenRouter API call failed: {e}")
        return None


def _call_gemini_api(prompt: str, retry_count: int = 0) -> Optional[Dict[str, Any]]:
    """Call Gemini API with timeout and retry logic."""
    global _gemini_model

    if _gemini_model is None:
        if not _initialize_gemini():
            return None

    try:
        logger.info(f"Calling Gemini API (attempt {retry_count + 1}/{MAX_RETRIES + 1})...")
        start_time = time.time()

        # Generate content with timeout
        response = _gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1000,
            )
        )

        duration = time.time() - start_time
        logger.info(f"✓ Gemini API responded in {duration:.2f}s")

        # Extract text from response
        if not response.text:
            logger.error("Empty response from Gemini")
            return None

        # Parse JSON response
        try:
            # Clean response text (remove markdown code blocks if present)
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()

            # Sanitize JSON to fix common issues
            response_text = _sanitize_json_string(response_text)

            response_data = json.loads(response_text)

            # Validate structure
            if not _validate_response(response_data):
                logger.error("Invalid response structure from Gemini")
                logger.error(f"Response data: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                return None

            return response_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Full response text (first 500 chars): {response_text[:500]}")
            logger.error(f"Response length: {len(response_text)} characters")
            # Print full content to console for debugging
            print("\n" + "="*60)
            print("FULL API RESPONSE CONTENT:")
            print("="*60)
            print(response_text)
            print("="*60 + "\n")

            # Return fallback explanation instead of None
            logger.warning("Returning fallback explanation due to JSON parse error")
            return _get_fallback_explanation()

    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")

        # Retry logic with exponential backoff
        if retry_count < MAX_RETRIES:
            backoff_seconds = 2 ** (retry_count + 1)  # 2s, 4s
            logger.info(f"Retrying in {backoff_seconds} seconds (attempt {retry_count + 2}/{MAX_RETRIES + 1})...")
            time.sleep(backoff_seconds)
            return _call_gemini_api(prompt, retry_count + 1)

        logger.error(f"Max retries ({MAX_RETRIES}) reached, giving up")
        return None


def generate_ai_explanation(
    sentence: str,
    tokens: List[Dict],
    grammar_patterns: List[Dict],
    vocab_items: List[Dict]
) -> Optional[Dict[str, Any]]:
    """
    Generate AI-powered pedagogical explanation for a Japanese sentence.

    Args:
        sentence: Original Japanese text
        tokens: List of token dictionaries from MeCab
        grammar_patterns: List of detected grammar patterns
        vocab_items: List of vocabulary entries

    Returns:
        Dictionary with AI explanation or None if unavailable:
        {
            "summary": str,
            "grammarNotes": [{"pattern": str, "explanation": str, "example": str}],
            "vocabNotes": [{"word": str, "reading": str, "nuance": str}],
            "culturalContext": str | None,
            "studyTips": str,
            "registerNote": str
        }

    Example:
        >>> generate_ai_explanation("今日は天気がいいですね", tokens, grammar, vocab)
        {"summary": "Cette phrase exprime...", ...}
    """
    # Check if AI is enabled
    if AI_PROVIDER not in ["gemini", "openrouter"]:
        logger.debug("AI provider not enabled")
        return None

    # Generate cache key
    cache_key = _get_cache_key(sentence, tokens, grammar_patterns, vocab_items)

    # Check cache first
    cached_result = _get_from_cache(cache_key)
    if cached_result:
        return cached_result

    # Build prompt
    prompt = _build_prompt(sentence, tokens, grammar_patterns, vocab_items)

    # Call appropriate AI provider
    result = None
    if AI_PROVIDER == "openrouter":
        logger.info("Using OpenRouter/Perplexity for AI explanation")
        result = _call_openrouter_api(prompt)
    elif AI_PROVIDER == "gemini":
        logger.info("Using Gemini for AI explanation")
        result = _call_gemini_api(prompt)

    if result:
        # Save to cache
        _save_to_cache(cache_key, result)
        return result

    # Graceful degradation
    logger.warning("AI explanation unavailable, returning None")
    return None


# Initialize on module import
if AI_PROVIDER == "gemini":
    _initialize_gemini()


# Test function
if __name__ == "__main__":
    print("Testing AI Explainer")
    print("=" * 50)

    # Test with a simple sentence
    test_sentence = "今日は天気がいいですね"
    test_tokens = [
        {"surface": "今日", "reading": "きょう", "partOfSpeech": "名詞"},
        {"surface": "は", "reading": "は", "partOfSpeech": "助詞"},
        {"surface": "天気", "reading": "てんき", "partOfSpeech": "名詞"},
        {"surface": "が", "reading": "が", "partOfSpeech": "助詞"},
        {"surface": "いい", "reading": "いい", "partOfSpeech": "形容詞"},
        {"surface": "です", "reading": "です", "partOfSpeech": "助動詞"},
        {"surface": "ね", "reading": "ね", "partOfSpeech": "助詞"},
    ]
    test_grammar = [
        {"pattern": "は", "description": "Marqueur de thème", "jlptLevel": "N5"},
        {"pattern": "が", "description": "Marqueur de sujet", "jlptLevel": "N5"},
        {"pattern": "～です", "description": "Copule polie", "jlptLevel": "N5"},
    ]
    test_vocab = [
        {"word": "今日", "reading": "きょう", "meaning": "aujourd'hui", "jlptLevel": "N5"},
        {"word": "天気", "reading": "てんき", "meaning": "temps (météo)", "jlptLevel": "N5"},
        {"word": "いい", "reading": "いい", "meaning": "bon, bien", "jlptLevel": "N5"},
    ]

    result = generate_ai_explanation(test_sentence, test_tokens, test_grammar, test_vocab)

    if result:
        print("\n✓ AI Explanation generated successfully:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n✗ Failed to generate AI explanation")
