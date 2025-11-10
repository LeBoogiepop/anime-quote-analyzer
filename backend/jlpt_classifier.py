"""
JLPT (Japanese Language Proficiency Test) level classifier.

This module classifies Japanese words and sentences by JLPT level (N5 to N1).
N5 is beginner level, N1 is advanced.

The classification is based on official JLPT vocabulary lists and common word frequencies.

Author: Maxime
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Literal

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JLPT level type
JLPTLevel = Literal["N5", "N4", "N3", "N2", "N1", "Unknown"]

# Global vocabulary data
_jlpt_vocab: Dict[str, List[str]] = {}


def load_jlpt_data() -> Dict[str, List[str]]:
    """
    Load JLPT vocabulary data from JSON file.

    The data file contains word lists for each JLPT level:
    {
        "N5": ["私", "日本語", "勉強", ...],
        "N4": ["授業", "宿題", "毎日", ...],
        ...
    }

    Returns:
        Dictionary mapping JLPT levels to word lists

    Raises:
        FileNotFoundError: If data file doesn't exist
        json.JSONDecodeError: If data file is malformed
    """
    global _jlpt_vocab

    # Return cached data if already loaded
    if _jlpt_vocab:
        return _jlpt_vocab

    data_path = Path(__file__).parent / "data" / "jlpt_vocab.json"

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            _jlpt_vocab = json.load(f)

        # Count total words
        total_words = sum(len(words) for words in _jlpt_vocab.values())
        logger.info(f"Loaded JLPT vocabulary data: {total_words} words across {len(_jlpt_vocab)} levels")

        return _jlpt_vocab

    except FileNotFoundError:
        logger.error(f"JLPT data file not found at {data_path}")
        # Return empty dict as fallback
        return {"N5": [], "N4": [], "N3": [], "N2": [], "N1": []}

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JLPT data file: {e}")
        return {"N5": [], "N4": [], "N3": [], "N2": [], "N1": []}


def classify_word(word: str) -> JLPTLevel:
    """
    Classify a single word by JLPT level.

    Searches through JLPT vocabulary lists from N5 (easiest) to N1 (hardest).
    Returns the lowest (easiest) level where the word is found.

    Args:
        word: Japanese word to classify

    Returns:
        JLPT level string: "N5", "N4", "N3", "N2", "N1", or "Unknown"

    Example:
        >>> classify_word("私")
        "N5"
        >>> classify_word("授業")
        "N4"
        >>> classify_word("未知の言葉")
        "Unknown"
    """
    vocab_data = load_jlpt_data()

    # Check levels in order from easiest to hardest
    # If a word appears in multiple levels, we want the lowest (easiest) one
    for level in ["N5", "N4", "N3", "N2", "N1"]:
        if word in vocab_data.get(level, []):
            return level

    # Word not found in any JLPT level
    return "Unknown"


def classify_sentence(tokens: List[Dict], vocabulary: List[Dict]) -> JLPTLevel:
    """
    Classify the overall JLPT level of a sentence.

    The sentence level is determined by:
    1. The JLPT levels of content words (from vocabulary)
    2. Sentence length and complexity
    3. Weighted average favoring harder words

    Classification rules:
    - If any N1/N2 words → likely N2-N1
    - Mostly N3 words → N3
    - Mostly N4 words → N4
    - Simple, short sentences with N5 words → N5

    Args:
        tokens: List of token dictionaries from tokenization
        vocabulary: List of vocabulary entries with JLPT levels

    Returns:
        Overall JLPT level for the sentence

    Example:
        >>> classify_sentence(tokens, [{"jlptLevel": "N5"}, {"jlptLevel": "N5"}])
        "N5"
        >>> classify_sentence(tokens, [{"jlptLevel": "N2"}, {"jlptLevel": "N3"}])
        "N2"
    """
    # Count words at each level
    level_counts = {
        "N5": 0,
        "N4": 0,
        "N3": 0,
        "N2": 0,
        "N1": 0,
        "Unknown": 0
    }

    for vocab_entry in vocabulary:
        level = vocab_entry.get("jlptLevel", "Unknown")
        level_counts[level] += 1

    # Sentence length affects difficulty
    sentence_length = len(tokens)

    # Calculate weighted score (higher = more difficult)
    # N1=5, N2=4, N3=3, N4=2, N5=1, Unknown=0
    level_weights = {"N1": 5, "N2": 4, "N3": 3, "N4": 2, "N5": 1, "Unknown": 0}

    total_weight = sum(level_counts[level] * level_weights[level] for level in level_counts)
    total_words = sum(level_counts.values())

    if total_words == 0:
        # No vocabulary detected, classify by length
        if sentence_length <= 8:
            return "N5"
        elif sentence_length <= 15:
            return "N4"
        else:
            return "N3"

    average_weight = total_weight / total_words

    # Classify based on average weight and presence of hard words
    # If any N1 words present → N1
    if level_counts["N1"] > 0:
        return "N1"

    # If multiple N2 words or high average → N2
    if level_counts["N2"] >= 2 or average_weight >= 4.0:
        return "N2"

    # If N2 word present or decent average → N3
    if level_counts["N2"] >= 1 or average_weight >= 3.0:
        return "N3"

    # If mostly N4 words → N4
    if average_weight >= 2.0:
        return "N4"

    # Default to N5 for simple sentences
    return "N5"


# Test function
if __name__ == "__main__":
    print("Testing JLPT Classifier")
    print("=" * 50)

    # Test word classification
    test_words = [
        "私",      # N5
        "日本語",  # N5
        "勉強",    # N5
        "授業",    # N4
        "宿題",    # N4
        "未知",    # Should be Unknown if not in data
    ]

    print("\nWord Classification:")
    for word in test_words:
        level = classify_word(word)
        print(f"  {word:10s} → {level}")

    # Test sentence classification
    print("\nSentence Classification:")

    # N5 sentence
    vocab_n5 = [
        {"word": "私", "jlptLevel": "N5"},
        {"word": "日本語", "jlptLevel": "N5"},
    ]
    tokens_n5 = [{"surface": c} for c in "私は日本語"]
    level = classify_sentence(tokens_n5, vocab_n5)
    print(f"  N5 vocab → {level}")

    # N4 sentence
    vocab_n4 = [
        {"word": "授業", "jlptLevel": "N4"},
        {"word": "宿題", "jlptLevel": "N4"},
    ]
    tokens_n4 = [{"surface": c} for c in "授業と宿題"]
    level = classify_sentence(tokens_n4, vocab_n4)
    print(f"  N4 vocab → {level}")
