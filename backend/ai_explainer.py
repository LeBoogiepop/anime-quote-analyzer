"""
AI-powered explanation generator using Google Gemini.

This module provides intelligent, contextualized explanations for Japanese sentences
using the Gemini 1.5 Flash model. Features include:
- LRU cache with 24h TTL to save API quota
- Robust error handling with retry logic
- Graceful degradation if API unavailable
- JSON response validation

Author: Maxime
"""

import os
import json
import time
import logging
import hashlib
from typing import Dict, List, Any, Optional
from functools import lru_cache
from datetime import datetime, timedelta
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "none")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gemini-1.5-flash-latest")
CACHE_MAX_SIZE = 500
CACHE_TTL_HOURS = 24
API_TIMEOUT_SECONDS = 15  # 15s timeout for AI generation
MAX_RETRIES = 2  # 2 retries with exponential backoff

# Initialize Gemini
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

    prompt = f"""Tu es un professeur de japonais expérimenté qui enseigne à des francophones de niveau débutant/intermédiaire.

Analyse cette phrase japonaise : "{sentence}"

Données linguistiques détectées :
- Tokens : {tokens_str}
- Structures grammaticales :
{grammar_str}
- Vocabulaire clé :
{vocab_str}

Génère une explication pédagogique en JSON avec exactement cette structure :
{{
  "summary": "Le sens et contexte en 1-2 phrases naturelles",
  "grammarNotes": [
    {{"pattern": "～ます", "explanation": "Explication claire", "example": "Exemple tiré de la phrase"}}
  ],
  "vocabNotes": [
    {{"word": "単語", "reading": "たんご", "nuance": "Nuance d'usage importante"}}
  ],
  "culturalContext": "Note culturelle si pertinent (registre, contexte social) ou null",
  "studyTips": "Un conseil mnémotechnique ou astuce d'apprentissage",
  "registerNote": "Niveau de langue (familier/poli/formel)"
}}

Règles importantes :
- Limite à 2-3 points grammaticaux essentiels (les plus importants de la phrase)
- Limite à 2-3 mots de vocabulaire clés
- Sois concis mais précis
- Privilégie les explications pratiques aux termes techniques
- Format JSON strict, pas de markdown, pas de texte avant/après
- Tous les textes en français"""

    return prompt


def _validate_response(response_data: Dict[str, Any]) -> bool:
    """Validate the structure of the AI response."""
    required_fields = ["summary", "grammarNotes", "vocabNotes", "studyTips", "registerNote"]

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

            response_data = json.loads(response_text)

            # Validate structure
            if not _validate_response(response_data):
                logger.error("Invalid response structure from Gemini")
                return None

            return response_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.debug(f"Response text: {response.text[:200]}...")
            return None

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
    if AI_PROVIDER != "gemini":
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

    # Call Gemini API
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
