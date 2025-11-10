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

from jlpt_classifier import classify_word, classify_sentence
from grammar_detector import detect_patterns

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def extract_vocabulary(tokens: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Extract important vocabulary words from tokens.

    Filters for content words (nouns, verbs, adjectives) and excludes
    grammatical particles, auxiliaries, and common function words.

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
        word = token["baseForm"]  # Use base form for vocabulary
        reading = token["reading"]

        # Skip if not a content word
        if pos not in content_pos:
            continue

        # Skip if already seen
        if word in seen_words:
            continue

        # Skip very short words (likely particles)
        if len(word) < 2 and pos != "名詞":
            continue

        seen_words.add(word)

        # Get JLPT level for this word
        jlpt_level = classify_word(word)

        vocabulary.append({
            "word": word,
            "reading": reading,
            "meaning": "Vocab demo - Traduction nécessaire",  # TODO: Add dictionary lookup
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
