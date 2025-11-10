"""
Japanese text analyzer using MeCab/fugashi.

This module handles tokenization, vocabulary extraction, and linguistic analysis
of Japanese text using the fugashi library (Python wrapper for MeCab).

MeCab is a morphological analyzer that segments Japanese text into tokens and
provides detailed linguistic information for each token.

Author: Maxime
"""

from typing import List, Dict, Any
import fugashi
import jaconv
import logging
import json
from pathlib import Path

from jlpt_classifier import classify_word, classify_sentence
from grammar_detector import detect_patterns
from translator import translate_to_french

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global vocabulary dictionary
_vocab_dictionary: Dict[str, str] = {}


def load_vocabulary_dictionary() -> Dict[str, str]:
    """
    Load French translations for Japanese words from JSON file.

    Returns:
        Dictionary mapping Japanese words to French translations

    Raises:
        FileNotFoundError: If dictionary file doesn't exist
        json.JSONDecodeError: If dictionary file is malformed
    """
    global _vocab_dictionary

    # Return cached data if already loaded
    if _vocab_dictionary:
        return _vocab_dictionary

    data_path = Path(__file__).parent / "data" / "vocab_dictionary.json"

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            _vocab_dictionary = json.load(f)

        logger.info(f"Loaded vocabulary dictionary with {len(_vocab_dictionary)} entries")
        return _vocab_dictionary

    except FileNotFoundError:
        logger.warning(f"Vocabulary dictionary not found at {data_path}")
        return {}

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse vocabulary dictionary: {e}")
        return {}


# Initialize MeCab tagger
# Using unidic-lite by default (smaller, faster)
# For better accuracy, install full UniDic: pip install unidic
try:
    tagger = fugashi.Tagger()
    logger.info("MeCab tagger initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MeCab tagger: {e}")
    raise


def tokenize(text: str) -> List[Dict[str, str]]:
    """
    Tokenize Japanese text using MeCab/fugashi.

    MeCab segments text into morphemes (smallest meaningful units) and provides
    linguistic features for each token.

    Args:
        text: Japanese text to tokenize

    Returns:
        List of token dictionaries with keys:
        - surface: The word as it appears in text (表層形)
        - reading: Pronunciation in hiragana (読み)
        - partOfSpeech: Grammatical category (品詞)
        - baseForm: Dictionary form of the word (基本形)

    Example:
        >>> tokenize("私は日本語を勉強しています")
        [
            {"surface": "私", "reading": "わたし", "partOfSpeech": "代名詞", "baseForm": "私"},
            {"surface": "は", "reading": "は", "partOfSpeech": "助詞", "baseForm": "は"},
            ...
        ]
    """
    tokens = []

    try:
        # Parse text with MeCab
        for word in tagger(text):
            # Extract features from MeCab output
            # word.feature contains: [pos1, pos2, pos3, pos4, inflection, conjugation, lemma, reading, pronunciation]

            surface = word.surface  # The actual word/character
            pos = word.feature.pos1 if word.feature.pos1 else "Unknown"  # Part of speech (品詞)

            # Get reading (読み) - MeCab returns katakana, convert to hiragana
            if word.feature.kana:
                reading = jaconv.kata2hira(word.feature.kana)  # Convert カタカナ → ひらがな
            else:
                # Fallback for words without reading (usually punctuation or unknown)
                reading = surface

            # Get base form (基本形) - the dictionary form
            if word.feature.lemma:
                base_form = word.feature.lemma
            else:
                base_form = surface

            # DEBUG: Log base form extraction for key words
            if surface in ["そう", "互い", "相手", "求める", "物", "タカギ", "悩む", "決まる"]:
                logger.info(f"[TOKENIZE] surface='{surface}' → baseForm='{base_form}', pos='{pos}'")

            tokens.append({
                "surface": surface,
                "reading": reading,
                "partOfSpeech": pos,
                "baseForm": base_form
            })

        logger.info(f"Tokenized into {len(tokens)} tokens")
        return tokens

    except Exception as e:
        logger.error(f"Tokenization failed: {e}")
        # Return basic fallback
        return [{
            "surface": text,
            "reading": text,
            "partOfSpeech": "Unknown",
            "baseForm": text
        }]


def is_proper_noun(token: Dict[str, str]) -> bool:
    """
    Detect if a token is a proper noun (name, place, etc.).

    Proper nouns should not be added to vocabulary lists since they are
    names, not words to study.

    Detection heuristics:
    1. All-katakana words (likely foreign names or loanwords)
    2. MeCab part-of-speech tag indicating proper noun
    3. Capitalized single words

    Args:
        token: Token dictionary with surface, reading, partOfSpeech

    Returns:
        True if token is likely a proper noun, False otherwise

    Example:
        >>> is_proper_noun({"surface": "タカギ", "partOfSpeech": "名詞"})
        True
        >>> is_proper_noun({"surface": "勉強", "partOfSpeech": "名詞"})
        False
    """
    surface = token.get("surface", "")
    pos = token.get("partOfSpeech", "")
    base_form = token.get("baseForm", "")

    # DEBUG: Log token details for analysis
    logger.info(f"[PROPER NOUN CHECK] surface='{surface}', pos='{pos}', baseForm='{base_form}'")

    # Check for proper noun POS tag from MeCab
    # MeCab marks proper nouns as 固有名詞 or includes it in the POS details
    if "固有名詞" in pos or pos == "名詞-固有名詞":
        logger.info(f"  → Detected as proper noun via POS tag: {surface}")
        return True

    # Check if all katakana (common for foreign names)
    # Allow some exceptions for common katakana words
    if surface and all('\u30A0' <= char <= '\u30FF' for char in surface):
        # All katakana - likely a proper noun or loanword
        # Could refine this by checking against common katakana word dictionary
        # For now, consider all-katakana as potential proper nouns to filter
        if len(surface) >= 2:  # At least 2 characters
            logger.info(f"  → Detected as proper noun via all-katakana heuristic: {surface}")
            return True

    logger.debug(f"  → Not a proper noun: {surface}")
    return False


def extract_vocabulary(tokens: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Extract important vocabulary words from tokens.

    Filters for content words (nouns, verbs, adjectives) and excludes
    grammatical particles, auxiliaries, common function words, and proper nouns.

    Args:
        tokens: List of token dictionaries from tokenize()

    Returns:
        List of vocabulary entries with JLPT levels and meanings

    Example:
        >>> tokens = tokenize("私は日本語を勉強しています")
        >>> extract_vocabulary(tokens)
        [
            {"word": "私", "reading": "わたし", "meaning": "Demo vocab", "jlptLevel": "N5"},
            {"word": "日本語", "reading": "にほんご", "meaning": "Demo vocab", "jlptLevel": "N5"},
            ...
        ]
    """
    vocabulary = []
    seen_words = set()  # Track seen words to avoid duplicates

    # Content word categories we want to extract
    content_pos = [
        "名詞",      # Noun
        "動詞",      # Verb
        "形容詞",    # Adjective
        "形状詞",    # Adjectival noun (na-adjective)
        "副詞",      # Adverb
    ]

    # Skip these subcategories
    skip_subcategories = [
        "助詞",      # Particle
        "助動詞",    # Auxiliary verb
        "接続詞",    # Conjunction
        "感動詞",    # Interjection
        "記号",      # Symbol
    ]

    for token in tokens:
        pos = token["partOfSpeech"]
        surface = token["surface"]    # Surface form (as appears in text)
        word = token["baseForm"]       # Use base form for vocabulary
        reading = token["reading"]

        # Skip if not a content word
        if pos not in content_pos:
            continue

        # Skip proper nouns (names, places, etc.)
        if is_proper_noun(token):
            logger.debug(f"Skipping proper noun: {surface}")
            continue

        # Skip if already seen
        if word in seen_words:
            continue

        # Skip very short words (likely particles)
        if len(word) < 2 and pos != "名詞":
            continue

        seen_words.add(word)

        # Get JLPT level for this word (pass base_form for better matching)
        jlpt_level = classify_word(word, base_form=word)

        # Get French translation using translator service
        # This uses fallback strategy: cache → dictionary → Jisho API → fallback
        meaning = translate_to_french(word, use_jisho=True)

        vocabulary.append({
            "word": word,
            "reading": reading,
            "meaning": meaning,
            "jlptLevel": jlpt_level
        })

    # Limit to top 10 most important words
    # TODO: Add importance scoring (frequency, JLPT level, etc.)
    vocabulary = vocabulary[:10]

    logger.info(f"Extracted {len(vocabulary)} vocabulary entries")
    return vocabulary


def analyze_text(text: str) -> Dict[str, Any]:
    """
    Perform complete linguistic analysis of Japanese text.

    This is the main entry point that coordinates all analysis steps:
    1. Tokenization with MeCab
    2. Vocabulary extraction
    3. Grammar pattern detection
    4. JLPT level classification

    Args:
        text: Japanese text to analyze

    Returns:
        Dictionary with complete analysis matching TypeScript types:
        {
            "originalText": str,
            "tokens": List[Token],
            "grammarPatterns": List[Pattern],
            "vocabulary": List[Vocab],
            "jlptLevel": str
        }

    Example:
        >>> analyze_text("私は日本語を勉強しています")
        {
            "originalText": "私は日本語を勉強しています",
            "tokens": [...],
            "grammarPatterns": [...],
            "vocabulary": [...],
            "jlptLevel": "N5"
        }
    """
    try:
        # Step 1: Tokenize the text
        tokens = tokenize(text)

        # Step 2: Extract vocabulary
        vocabulary = extract_vocabulary(tokens)

        # Step 3: Detect grammar patterns
        grammar_patterns = detect_patterns(text, tokens)

        # Step 4: Classify overall JLPT level
        jlpt_level = classify_sentence(tokens, vocabulary)

        # Construct response
        result = {
            "originalText": text,
            "tokens": tokens,
            "grammarPatterns": grammar_patterns,
            "vocabulary": vocabulary,
            "jlptLevel": jlpt_level
        }

        return result

    except Exception as e:
        logger.error(f"Analysis failed for text '{text[:50]}...': {e}")
        raise


# Test function for development
if __name__ == "__main__":
    # Test with sample Japanese text
    test_text = "私は日本語を勉強しています"

    print(f"Analyzing: {test_text}")
    print("=" * 50)

    result = analyze_text(test_text)

    print(f"\nOriginal: {result['originalText']}")
    print(f"JLPT Level: {result['jlptLevel']}")

    print(f"\nTokens ({len(result['tokens'])}):")
    for token in result['tokens']:
        print(f"  {token['surface']:8s} | {token['reading']:10s} | {token['partOfSpeech']}")

    print(f"\nVocabulary ({len(result['vocabulary'])}):")
    for vocab in result['vocabulary']:
        print(f"  {vocab['word']:10s} ({vocab['reading']}) - {vocab['jlptLevel']}")

    print(f"\nGrammar Patterns ({len(result['grammarPatterns'])}):")
    for pattern in result['grammarPatterns']:
        print(f"  {pattern['pattern']:15s} - {pattern['description'][:50]}...")
