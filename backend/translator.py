"""
Translation service with fallback strategies.

This module provides Japanese-to-French translation using multiple sources:
1. Local cache (fastest, previously translated)
2. Static vocabulary dictionary (common words)
3. Jisho API (online Japanese-English dictionary)
4. Helpful fallback message (when all else fails)

The cache is persisted to disk to improve performance across sessions.

Author: Maxime
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional
import requests

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global cache for translations
_translation_cache: Dict[str, str] = {}
_cache_modified = False

# Cache file path
CACHE_FILE = Path(__file__).parent / "data" / "translation_cache.json"

# Common Japanese words with proper French translations
# These take priority over Jisho API to ensure quality
COMMON_WORDS_FR = {
    # Common expressions and particles
    "そう": "ainsi, comme ça, de cette manière",
    "もう": "déjà, maintenant, encore",
    "よし": "bien, d'accord, allez",
    "いや": "non, eh bien",
    "ええ": "oui, eh bien",
    "はい": "oui",
    "いいえ": "non",
    "ううん": "non (familier)",
    "うん": "oui (familier)",
    "ああ": "ah, oh",
    "えっ": "hein, quoi",
    "へえ": "oh, vraiment",

    # Common verbs and adjectives
    "いい": "bon, bien",
    "良い": "bon, bien",
    "言う": "dire, parler",
    "為る": "faire",
    "する": "faire",
    "やる": "faire",
    "なる": "devenir",
    "ある": "être, avoir, exister",
    "いる": "être (animé)",
    "見る": "voir, regarder",
    "聞く": "écouter, entendre, demander",
    "話す": "parler",
    "書く": "écrire",
    "読む": "lire",

    # Relational and contextual words
    "互い": "mutuellement, l'un l'autre, réciproquement",
    "相手": "partenaire, adversaire, l'autre personne",
    "求める": "demander, chercher, désirer, exiger",
    "物": "chose, objet, article",
    "事": "chose, affaire, fait",
    "決まる": "être décidé, être fixé, être réglé",
    "全然": "pas du tout, complètement (avec négation)",
    "逆": "inverse, contraire, opposé",
    "気": "esprit, sentiment, humeur, envie, attention",
    "からかう": "taquiner, se moquer gentiment",
    "却って": "au contraire, plutôt, inversement",
    "挑発": "provocation, défi",
    "反省": "réflexion, introspection, remords",

    # Pronouns
    "私": "je, moi",
    "僕": "je (masculin, poli)",
    "俺": "je (masculin, familier)",
    "あなた": "tu, vous",
    "君": "tu (familier)",
    "彼": "il, lui",
    "彼女": "elle",
    "これ": "ceci, ça",
    "それ": "cela, ça",
    "あれ": "ça là-bas",

    # Question words
    "何": "quoi, que",
    "誰": "qui",
    "どこ": "où",
    "いつ": "quand",
    "なぜ": "pourquoi",
    "どう": "comment",
    "どの": "quel, lequel",
    "どれ": "lequel",

    # Common adjectives and adverbs
    "大きい": "grand",
    "小さい": "petit",
    "新しい": "nouveau",
    "古い": "vieux, ancien",
    "高い": "haut, cher",
    "安い": "bon marché, pas cher",
    "早い": "tôt, rapide",
    "遅い": "tard, lent",
    "多い": "nombreux, beaucoup",
    "少ない": "peu, peu nombreux",

    # Time expressions
    "今": "maintenant, présent",
    "昨日": "hier",
    "明日": "demain",
    "今日": "aujourd'hui",
    "毎日": "chaque jour, tous les jours",
    "いつも": "toujours, constamment",
    "時々": "parfois, quelquefois",
    "たまに": "de temps en temps, rarement",

    # Common nouns
    "人": "personne, gens",
    "時": "temps, moment, heure",
    "日": "jour, soleil",
    "年": "année",
    "月": "mois, lune",
    "週": "semaine",
    "朝": "matin",
    "昼": "midi, journée",
    "夜": "nuit, soir",
    "家": "maison, famille",
    "学校": "école",
    "先生": "professeur, enseignant",
    "友達": "ami",
}


def load_cache() -> Dict[str, str]:
    """
    Load translation cache from disk.

    Returns:
        Dictionary mapping Japanese words to French translations
    """
    global _translation_cache

    # Return cached data if already loaded
    if _translation_cache:
        return _translation_cache

    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                _translation_cache = json.load(f)
            logger.info(f"Loaded translation cache with {len(_translation_cache)} entries")
        else:
            logger.info("No translation cache file found, starting fresh")
            _translation_cache = {}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse translation cache: {e}")
        _translation_cache = {}
    except Exception as e:
        logger.error(f"Error loading translation cache: {e}")
        _translation_cache = {}

    return _translation_cache


def save_cache() -> bool:
    """
    Save translation cache to disk.

    Returns:
        True if successful, False otherwise
    """
    global _cache_modified

    if not _cache_modified:
        return True  # No changes to save

    try:
        # Ensure data directory exists
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(_translation_cache, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved translation cache with {len(_translation_cache)} entries")
        _cache_modified = False
        return True
    except Exception as e:
        logger.error(f"Failed to save translation cache: {e}")
        return False


def get_jisho_translation(word: str, timeout: int = 5) -> Optional[Dict[str, str]]:
    """
    Fetch translation from Jisho.org API.

    Jisho provides Japanese-English dictionary data. We'll use the first
    English meaning and note that it needs manual French translation in future.

    Args:
        word: Japanese word to translate
        timeout: Request timeout in seconds

    Returns:
        Dictionary with 'english' key, or None if not found

    Example:
        >>> result = get_jisho_translation("勉強")
        >>> result
        {'english': 'study; diligence; experience'}
    """
    try:
        # Jisho API endpoint
        url = f"https://jisho.org/api/v1/search/words?keyword={word}"

        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        data = response.json()

        # Check if we got results
        if data.get('data') and len(data['data']) > 0:
            first_result = data['data'][0]

            # Extract first English definition
            if first_result.get('senses') and len(first_result['senses']) > 0:
                first_sense = first_result['senses'][0]
                english_glosses = first_sense.get('english_definitions', [])

                if english_glosses:
                    english_meaning = '; '.join(english_glosses)
                    logger.info(f"Found Jisho translation for '{word}': {english_meaning}")
                    return {'english': english_meaning}

        logger.warning(f"No Jisho results found for '{word}'")
        return None

    except requests.Timeout:
        logger.error(f"Jisho API timeout for word '{word}'")
        return None
    except requests.RequestException as e:
        logger.error(f"Jisho API request failed for '{word}': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching Jisho translation for '{word}': {e}")
        return None


def translate_to_french(word: str, use_jisho: bool = True) -> str:
    """
    Translate Japanese word to French using fallback strategy.

    Translation priority:
    1. Check common words dictionary (highest quality)
    2. Check local cache (fastest)
    3. Check static vocabulary dictionary
    4. Query Jisho API for English translation (if enabled)
    5. Return helpful fallback message

    Args:
        word: Japanese word to translate
        use_jisho: Whether to use Jisho API as fallback (default: True)

    Returns:
        French translation string

    Example:
        >>> translate_to_french("勉強")
        "étude, étudier"
        >>> translate_to_french("そう")
        "ainsi, comme ça, de cette manière"
    """
    global _cache_modified

    # Strategy 1: Check common words first (highest priority for quality)
    if word in COMMON_WORDS_FR:
        logger.debug(f"Common word hit for '{word}'")
        return COMMON_WORDS_FR[word]

    # Load cache and dictionary
    cache = load_cache()

    # Strategy 2: Check cache
    if word in cache:
        logger.debug(f"Cache hit for '{word}'")
        return cache[word]

    # Strategy 3: Check static dictionary
    try:
        from analyzer import load_vocabulary_dictionary
        vocab_dict = load_vocabulary_dictionary()

        if word in vocab_dict:
            translation = vocab_dict[word]

            # Add to cache for future use
            cache[word] = translation
            _translation_cache[word] = translation
            _cache_modified = True

            logger.info(f"Dictionary hit for '{word}': {translation}")
            return translation
    except Exception as e:
        logger.error(f"Failed to load vocabulary dictionary: {e}")

    # Strategy 4: Query Jisho API (if enabled)
    if use_jisho:
        jisho_result = get_jisho_translation(word)

        if jisho_result and 'english' in jisho_result:
            # For now, return English with a note
            # In future, integrate DeepL or manual French translations
            translation = f"{jisho_result['english']} (EN)"

            # Add to cache
            cache[word] = translation
            _translation_cache[word] = translation
            _cache_modified = True

            return translation

    # Strategy 5: Helpful fallback
    fallback = "[Traduction non disponible]"
    logger.warning(f"No translation found for '{word}', using fallback")

    return fallback


def translate_sentence(sentence: str) -> str:
    """
    Translate full Japanese sentence to French.

    NOTE: This is a placeholder for future integration with DeepL or Google Translate.
    For now, it returns a helpful message.

    Args:
        sentence: Japanese sentence to translate

    Returns:
        French translation of the sentence

    Example:
        >>> translate_sentence("私は日本語を勉強しています")
        "[Traduction de phrase complète - DeepL intégration à venir]"
    """
    # TODO: Integrate DeepL API for professional sentence translation
    # For now, return placeholder
    logger.info(f"Sentence translation requested for: {sentence[:50]}...")

    return "[Traduction de phrase complète - DeepL intégration à venir]"


def batch_translate(words: list[str], use_jisho: bool = True) -> Dict[str, str]:
    """
    Translate multiple words efficiently.

    Args:
        words: List of Japanese words to translate
        use_jisho: Whether to use Jisho API for missing translations

    Returns:
        Dictionary mapping words to their French translations

    Example:
        >>> batch_translate(["勉強", "学校", "先生"])
        {"勉強": "étude, étudier", "学校": "école", "先生": "professeur"}
    """
    translations = {}

    for word in words:
        translations[word] = translate_to_french(word, use_jisho=use_jisho)

    # Save cache after batch operation
    if _cache_modified:
        save_cache()

    logger.info(f"Batch translated {len(words)} words")
    return translations


# Cleanup function to save cache on module exit
def cleanup():
    """Save cache before module exit."""
    if _cache_modified:
        save_cache()


# Test function
if __name__ == "__main__":
    print("Testing Translation Service")
    print("=" * 50)

    # Test cases
    test_words = [
        "勉強",      # Should be in dictionary
        "学校",      # Should be in dictionary
        "食べる",    # Should be in dictionary
        "頑張る",    # Should be in dictionary
        "試験",      # May need Jisho
    ]

    print("\n1. Testing individual translations:")
    for word in test_words:
        translation = translate_to_french(word, use_jisho=True)
        print(f"  {word:10s} → {translation}")

    print("\n2. Testing batch translation:")
    batch_results = batch_translate(["日本語", "英語", "フランス語"])
    for word, translation in batch_results.items():
        print(f"  {word:10s} → {translation}")

    print("\n3. Testing sentence translation:")
    sentence = "私は日本語を勉強しています"
    sentence_translation = translate_sentence(sentence)
    print(f"  {sentence}")
    print(f"  → {sentence_translation}")

    print("\n4. Cache statistics:")
    print(f"  Total cached entries: {len(_translation_cache)}")
    print(f"  Cache file location: {CACHE_FILE}")

    # Save cache
    cleanup()
    print("\n✓ Translation service test complete")
