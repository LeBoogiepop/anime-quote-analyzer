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

            # Capture full POS details for proper noun detection
            # MeCab provides: [pos1, pos2, pos3, pos4, inflection, conjugation, lemma, reading, pronunciation]
            rawPos = str(word.feature.feature) if hasattr(word.feature, 'feature') else pos
            posDetails = []
            if hasattr(word.feature, 'pos1') and word.feature.pos1:
                posDetails.append(word.feature.pos1)
            if hasattr(word.feature, 'pos2') and word.feature.pos2:
                posDetails.append(word.feature.pos2)
            if hasattr(word.feature, 'pos3') and word.feature.pos3:
                posDetails.append(word.feature.pos3)
            if hasattr(word.feature, 'pos4') and word.feature.pos4:
                posDetails.append(word.feature.pos4)

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
                logger.info(f"[TOKENIZE] surface='{surface}' → baseForm='{base_form}', pos='{pos}', posDetails={posDetails}")

            tokens.append({
                "surface": surface,
                "reading": reading,
                "partOfSpeech": pos,
                "baseForm": base_form,
                "rawPos": rawPos,
                "posDetails": posDetails
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

    Returns True for character names like タカギ, ニシカタ, etc.
    Proper nouns should not be added to vocabulary lists since they are
    names, not words to study.

    Detection heuristics:
    1. MeCab part-of-speech tag indicating proper noun (固有名詞, 人名, 地名)
    2. All-katakana words >= 2 chars (likely foreign names or character names)
       - Whitelist excludes common katakana loanwords

    Args:
        token: Token dictionary with surface, reading, partOfSpeech, posDetails

    Returns:
        True if token is likely a proper noun, False otherwise

    Example:
        >>> is_proper_noun({"surface": "タカギ", "partOfSpeech": "名詞", "posDetails": ["名詞", "固有名詞", "人名", "姓"]})
        True
        >>> is_proper_noun({"surface": "テレビ", "partOfSpeech": "名詞", "posDetails": ["名詞", "一般"]})
        False
    """
    surface = token.get("surface", "")
    pos = token.get("partOfSpeech", "")
    posDetails = token.get("posDetails", [])
    rawPos = token.get("rawPos", "")

    # ALWAYS log ALL katakana words for debugging
    if surface and len(surface) >= 2:
        is_all_katakana = all('\u30A0' <= char <= '\u30FF' or char == 'ー' for char in surface)
        if is_all_katakana:
            logger.warning(f"[KATAKANA DETECTED] '{surface}' | POS: {pos} | Details: {posDetails}")

    # Check posDetails array for proper noun indicators
    proper_noun_indicators = ["固有名詞", "人名", "地名", "組織名"]
    for indicator in proper_noun_indicators:
        if any(indicator in detail for detail in posDetails):
            logger.warning(f"  → PROPER NOUN (posDetails): {surface}")
            return True

    # Fallback: Check main POS tag and rawPos
    if "固有名詞" in pos or "人名" in pos or "地名" in pos:
        logger.warning(f"  → PROPER NOUN (POS tag): {surface}")
        return True

    if "固有名詞" in rawPos or "人名" in rawPos or "地名" in rawPos:
        logger.warning(f"  → PROPER NOUN (rawPos): {surface}")
        return True

    # All-katakana heuristic (character names in anime)
    if surface and len(surface) >= 2:
        # Check if ALL characters are katakana (allowing 'ー')
        is_all_katakana = all('\u30A0' <= char <= '\u30FF' or char == 'ー' for char in surface)

        if is_all_katakana:
            # Whitelist: common katakana loanwords to KEEP as vocabulary
            # This includes all katakana words from JLPT N5/N4/N3 levels
            common_loanwords = {
                # Communication & Technology
                'メッセージ', 'パソコン', 'テレビ', 'メール', 'データ', 'システム',
                'プログラム', 'コンピューター', 'スマホ', 'インターネット', 'アプリ',
                'ニュース', 'メモ', 'ページ', 'ノート',
                # Places & Transportation
                'ホテル', 'レストラン', 'コンビニ', 'バス', 'タクシー',
                # Food & Drink (expanded as per requirements)
                'コーヒー', 'ジュース', 'ブラック', 'パン', 'デザート', 'ミルク',
                'ティー', 'ケーキ', 'サラダ', 'スープ', 'カレー', 'ラーメン',
                'ハンバーガー', 'サンドイッチ', 'ビール', 'ワイン', 'ウイスキー',
                # School & Work
                'テスト', 'ペン', 'チョーク', 'アルバイト', 'クラス', 'ノート',
                # Entertainment
                'アニメ', 'ゲーム', 'スポーツ', 'ドラマ', 'ミュージック', 'コンサート',
                # Measurements
                'メートル', 'センチ', 'ミリ', 'キロ', 'グラム', 'リットル',
                # Other Common Words
                'ショック', 'ドア', 'ピンク', 'チャンス', 'チーム', 'バランス',
                'エネルギー', 'ストレス', 'リスク', 'サービス', 'プレゼント',
                'カード', 'セット', 'グループ', 'レベル', 'タイプ', 'ポイント',
                'プラン', 'ルール', 'マナー', 'スタイル', 'イメージ', 'センス'
            }

            if surface in common_loanwords:
                logger.debug(f"  → NOT proper noun (katakana but whitelisted): {surface}")
                return False
            else:
                # Everything else that's all-katakana is a proper noun (character name)
                logger.warning(f"  → PROPER NOUN (all-katakana, not in whitelist): {surface}")
                return True

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

        # DEBUG: Log ALL katakana words to see if they reach this point
        if surface and len(surface) >= 2:
            is_all_katakana = all('\u30A0' <= char <= '\u30FF' or char == 'ー' for char in surface)
            if is_all_katakana:
                logger.warning(f"[VOCAB EXTRACTION] Katakana word: '{surface}', pos='{pos}', in content_pos={pos in content_pos}")

        # Skip if not a content word
        if pos not in content_pos:
            continue

        # Skip proper nouns (names, places, etc.)
        if is_proper_noun(token):
            logger.warning(f"✓ SKIPPED proper noun: {surface} (not added to vocabulary)")
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
            "baseForm": word,  # Base form for dictionary lookups and WaniKani links
            "reading": reading,
            "meaning": meaning,
            "jlptLevel": jlpt_level
        })

    # Limit to top 10 most important words
    # TODO: Add importance scoring (frequency, JLPT level, etc.)
    vocabulary = vocabulary[:10]

    logger.info(f"Extracted {len(vocabulary)} vocabulary entries")
    return vocabulary


def generate_explanation(
    original_text: str,
    tokens: List[Dict[str, str]],
    vocabulary: List[Dict[str, Any]],
    patterns: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate a pedagogical explanation for a Japanese sentence.

    Creates a structured, educational explanation with:
    - summary: Concise French explanation of what the sentence means/does
    - grammar_focus: One main grammatical point with usage notes
    - vocab_focus: 1-3 key vocabulary items with short explanations
    - culture_note: Optional sociolinguistic/cultural context
    - translation_hint: Message if DeepL unavailable (empty string otherwise)

    Args:
        original_text: The original Japanese sentence
        tokens: List of token dictionaries from tokenize()
        vocabulary: List of vocabulary entries
        patterns: List of detected grammar patterns

    Returns:
        Dictionary with pedagogical explanation structure

    Example:
        >>> generate_explanation("コーヒー飲める？", tokens, vocab, patterns)
        {
            "summary": "Proposition informelle de boire du café ensemble",
            "grammar_focus": "Forme potentielle 飲める exprime la capacité ou possibilité",
            "vocab_focus": [
                {"term": "コーヒー", "detail": "café, boisson amère populaire"},
                {"term": "飲める", "detail": "pouvoir boire (forme potentielle)"}
            ],
            "culture_note": "Le café est souvent associé au monde adulte au Japon",
            "translation_hint": ""
        }
    """
    from translator import translate_sentence

    # Cultural context keywords mapping
    CULTURE_NOTES = {
        "コーヒー": "Le café est souvent perçu comme une boisson sophistiquée, associée au monde adulte et au travail au Japon.",
        "お茶": "Le thé joue un rôle central dans la culture japonaise, symbolisant l'hospitalité et la convivialité.",
        "さん": "Suffixe honorifique poli, utilisé pour marquer le respect envers l'interlocuteur.",
        "ちゃん": "Suffixe affectueux utilisé pour les enfants, proches amis, ou membres de la famille.",
        "君": "Suffixe familier utilisé principalement entre garçons ou envers des subordonnés.",
        "先輩": "Désigne une personne plus âgée ou avec plus d'ancienneté, reflet de la hiérarchie sociale japonaise.",
        "後輩": "Personne plus jeune ou avec moins d'ancienneté, complément du système senpai-kōhai.",
    }

    # Get translation for summary construction
    translation = translate_sentence(original_text)
    has_deepl = translation and not translation.startswith("[Traduction")

    # Build summary
    summary = ""
    if has_deepl:
        # Use translation to create a pedagogical summary
        summary = f"Cette phrase exprime : {translation}"
    else:
        # Construct fallback summary from vocabulary
        if vocabulary:
            key_words = [v.get("meaning", v.get("word", "")) for v in vocabulary[:2]]
            summary = f"Phrase utilisant : {', '.join(key_words)}"
        else:
            summary = "Phrase en japonais nécessitant une traduction."

    # Build grammar focus (select most important pattern)
    grammar_focus = ""
    if patterns:
        main_pattern = patterns[0]
        pattern_name = main_pattern.get("pattern", "")
        pattern_desc = main_pattern.get("description", "")

        # Create pedagogical grammar explanation
        if pattern_name:
            grammar_focus = f"Structure {pattern_name} : {pattern_desc}"

    # Build vocab focus (1-3 key items)
    vocab_focus = []
    if vocabulary:
        for v in vocabulary[:3]:  # Top 3 vocabulary items
            word = v.get("word", "")
            meaning = v.get("meaning", "")

            # Only include French translations
            if meaning and not meaning.endswith("(EN)") and not meaning.startswith("[Traduction"):
                # Create short pedagogical explanation
                jlpt = v.get("jlptLevel", "")
                jlpt_note = f" ({jlpt})" if jlpt and jlpt != "Unknown" else ""
                vocab_focus.append({
                    "term": word,
                    "detail": f"{meaning}{jlpt_note}"
                })

    # Build culture note (check for cultural keywords)
    culture_note = None
    for word_obj in vocabulary:
        word = word_obj.get("word", "")
        if word in CULTURE_NOTES:
            culture_note = CULTURE_NOTES[word]
            break

    # Build translation hint
    translation_hint = ""
    if not has_deepl:
        translation_hint = "Configurez DeepL API pour obtenir des traductions automatiques de phrases complètes."

    return {
        "summary": summary,
        "grammar_focus": grammar_focus,
        "vocab_focus": vocab_focus,
        "culture_note": culture_note,
        "translation_hint": translation_hint
    }


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

        # Step 5: Generate automatic explanation
        explanation = generate_explanation(text, tokens, vocabulary, grammar_patterns)

        # Construct response
        result = {
            "originalText": text,
            "tokens": tokens,
            "grammarPatterns": grammar_patterns,
            "vocabulary": vocabulary,
            "jlptLevel": jlpt_level,
            "explanation": explanation
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
