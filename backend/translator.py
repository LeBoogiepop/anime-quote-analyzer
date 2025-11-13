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
import os
from pathlib import Path
from typing import Dict, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DeepL API configuration
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "")
DEEPL_API_URL = os.getenv("DEEPL_API_URL", "https://api-free.deepl.com/v2/translate")

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

    # CRITICAL N5 verbs and common words
    "できる": "pouvoir faire, être capable de",
    "出来る": "pouvoir faire, être capable de",
    "見る": "voir, regarder",
    "来る": "venir",
    "居る": "être, se trouver (êtres vivants)",
    "いる": "être, se trouver (êtres vivants)",
    "買う": "acheter",
    "分かる": "comprendre, savoir",
    "わかる": "comprendre, savoir",
    "欲しい": "vouloir, désirer",
    "優しい": "gentil, doux, tendre",
    "やる": "faire",
    "遣る": "faire",
    "ある": "exister, avoir (objets inanimés)",
    "有る": "exister, avoir",
    "なる": "devenir",
    "成る": "devenir",
    "思う": "penser, croire",
    "おもう": "penser",
    "行く": "aller",
    "いく": "aller",
    "こと": "chose, fait, affaire",
    "次": "prochain, suivant",
    "回": "fois (compteur)",
    "西": "ouest",
    "ひと": "personne",
    "とき": "moment",
    "ところ": "endroit, lieu",

    # N4 critical words
    "まあ": "eh bien, bon",
    "色々": "divers, varié, toutes sortes de",
    "いろいろ": "divers, varié",
    "足りる": "suffire, être suffisant",
    "過ぎる": "dépasser, passer",
    "侭": "tel quel, comme c'est",
    "まま": "tel quel, comme c'est",
    "攻める": "attaquer, assaillir",
    "受ける": "recevoir, subir",
    "確か": "certain, sûr",
    "たしか": "si je me souviens bien",

    # N3 critical words
    "我慢": "patience, endurance",
    "がまん": "patience, endurance",
    "勝負": "match, compétition, victoire ou défaite",
    "しょうぶ": "match, compétition",
    "伝わる": "se transmettre, se propager",
    "つたわる": "se transmettre",
    "全て": "tout, tous",
    "すべて": "tout, tous",
    "現状": "situation actuelle, état actuel",
    "げんじょう": "situation actuelle",

    # Katakana loanwords & beverages
    "メッセージ": "message",
    "ショック": "choc",
    "コーヒー": "café (boisson amère)",
    "ジュース": "jus (boisson sucrée)",
    "ブラック": "noir, sans sucre ni lait",
    "ミルク": "lait",
    "テスト": "test, examen",
    "レベル": "niveau",
    "スタイル": "style",
    "サンド": "sandwich (abréviation)",
    "ハンバーガー": "hamburger",
    "パン": "pain",
    "ケーキ": "gâteau",

    # Adjectives for taste and preferences
    "苦い": "amer (goût)",
    "にがい": "amer (goût)",
    "苦手": "pas doué, ne pas aimer",
    "にがて": "pas doué, ne pas aimer",

    # Common verbs and expressions
    "逸れる": "s'écarter, dévier",
    "それる": "s'écarter, dévier",
    "散々": "terriblement, complètement",
    "さんざん": "terriblement, complètement",
    "返る": "retourner, revenir",
    "かえる": "retourner, revenir",
    "帰る": "rentrer (chez soi), retourner",
    "やつ": "type, personne (familier)",
    "奴": "type, personne (familier)",
    "チャリ": "vélo (argot)",
    "見せ合う": "se montrer l'un à l'autre, se montrer mutuellement",
    "みせあう": "se montrer l'un à l'autre",
    "見せる": "montrer, faire voir",
    "みせる": "montrer",

    # Particules courantes
    "ね": "n'est-ce pas",
    "よ": "particule d'emphase",
    "な": "ne... pas, hein",
    "わ": "particule (féminin)",
    "ぞ": "particule (masculin)",
    "ぜ": "particule (masculin familier)",
    "ほど": "environ, autant que",
    "だけ": "seulement",
    "ばかり": "seulement, toujours",
    "など": "et cetera",
    "って": "dit-on",
    "ため": "pour, afin de",
    "訳": "raison",
    "わけ": "raison",
    "筈": "devrait",
    "はず": "devrait",
    "つもり": "intention",
    "よう": "manière, semble",
    "ふう": "style",
    "気味": "tendance",
    "ぎみ": "tendance",
    "らしい": "semble, typique",
    "みたい": "comme, semble",
    "なんて": "comme, quel",
    "とか": "et cetera, ou",
    "のに": "bien que",
    "けど": "mais",
    "でも": "mais, même",
    "しかし": "cependant",
    "それでも": "malgré tout",
    "だから": "donc",
    "なので": "donc, parce que",
    "よね": "n'est-ce pas",
    "でしょ": "n'est-ce pas",
    "だろう": "probablement",
    "んだ": "c'est que",
    "べき": "devrait",

    # Émotions
    "恥ずかしい": "embarrassant",
    "はずかしい": "embarrassant",
    "悔しい": "frustrant",
    "くやしい": "frustrant",
    "寂しい": "seul, triste",
    "さびしい": "seul",
    "懐かしい": "nostalgique",
    "なつかしい": "nostalgique",
    "羨ましい": "envieux",
    "うらやましい": "envieux",
    "恐ろしい": "effrayant",
    "おそろしい": "effrayant",
    "凄い": "incroyable",
    "すごい": "incroyable",
    "素晴らしい": "merveilleux",
    "すばらしい": "merveilleux",
    "可愛い": "mignon",
    "かわいい": "mignon",
    "格好いい": "cool, classe",
    "かっこいい": "cool",
    "汚い": "sale",
    "きたない": "sale",
    "臭い": "puant",
    "くさい": "puant",

    # Verbes supplémentaires
    "見せる": "montrer",
    "みせる": "montrer",
    "聞かせる": "faire écouter",
    "きかせる": "faire écouter",
    "教わる": "apprendre de",
    "おそわる": "apprendre de",
    "感じる": "sentir, ressentir",
    "かんじる": "sentir",
    "頼む": "demander",
    "たのむ": "demander",
    "褒める": "féliciter",
    "ほめる": "féliciter",
    "叱る": "gronder",
    "しかる": "gronder",
    "怖がる": "avoir peur",
    "こわがる": "avoir peur",

    # N3 expressions
    "急ぐ": "se dépêcher",
    "いそぐ": "se dépêcher",
    "焦る": "être pressé",
    "あせる": "être pressé",
    "慌てる": "paniquer",
    "あわてる": "paniquer",
    "恐れる": "craindre",
    "おそれる": "craindre",
    "不安": "inquiétude",
    "ふあん": "inquiétude",
    "緊張": "tension",
    "きんちょう": "tension",
    "満足": "satisfaction",
    "まんぞく": "satisfaction",
    "納得": "compréhension",
    "なっとく": "compréhension",
    "了解": "compris",
    "りょうかい": "compris",
    "承知": "accord",
    "しょうち": "accord",
    "感謝": "gratitude",
    "かんしゃ": "gratitude",
    "お礼": "remerciement",
    "おれい": "remerciement",
    "謝罪": "excuses",
    "しゃざい": "excuses",
    "後悔": "regret",
    "こうかい": "regret",
    "諦め": "abandon",
    "あきらめ": "abandon",
    "辛抱": "patience",
    "しんぼう": "patience",
    "耐える": "endurer",
    "たえる": "endurer",
    "無駄": "inutile",
    "むだ": "inutile",
    "無意味": "sans sens",
    "むいみ": "sans sens",
    "意義": "signification",
    "いぎ": "signification",
    "大事": "important",
    "だいじ": "important",
    "重要": "important",
    "じゅうよう": "important",
    "不可欠": "indispensable",
    "ふかけつ": "indispensable",
    "当然": "naturel",
    "とうぜん": "naturel",
    "当たり前": "normal",
    "あたりまえ": "normal",
    "通常": "habituel",
    "つうじょう": "habituel",
    "珍しい": "rare",
    "めずらしい": "rare",
    "変": "étrange",
    "へん": "étrange",
    "奇妙": "étrange",
    "きみょう": "étrange",
    "不思議": "mystérieux",
    "ふしぎ": "mystérieux",
    "謎": "énigme",
    "なぞ": "énigme",
    "内緒": "secret",
    "ないしょ": "secret",
    "隠す": "cacher",
    "かくす": "cacher",
    "隠れる": "se cacher",
    "かくれる": "se cacher",
    "バレる": "être découvert",
    "ばれる": "être découvert",
    "明らか": "clair",
    "あきらか": "clair",
    "明白": "évident",
    "めいはく": "évident",
    "確実": "certain",
    "かくじつ": "certain",

    # NEW ADDITIONS - Directions
    "さっきまで": "jusqu'à il y a un instant",
    "東": "est",
    "ひがし": "est",
    "南": "sud",
    "みなみ": "sud",
    "北": "nord",
    "きた": "nord",
    "むん": "chose (dialecte)",

    # NEW ADDITIONS - Verbs
    "呼ぶ": "appeler",
    "よぶ": "appeler",
    "答える": "répondre",
    "こたえる": "répondre",
    "質問": "question",
    "しつもん": "question",
    "借りる": "emprunter",
    "かりる": "emprunter",
    "貸す": "prêter",
    "かす": "prêter",
    "飲める": "pouvoir boire",
    "のめる": "pouvoir boire",
    "食べられる": "pouvoir manger",
    "たべられる": "pouvoir manger",
    "見られる": "pouvoir voir",
    "みられる": "pouvoir voir",
    "起こす": "réveiller, causer",
    "おこす": "réveiller",
    "育てる": "élever, cultiver",
    "そだてる": "élever",
    "比べる": "comparer",
    "くらべる": "comparer",
    "調べる": "vérifier, rechercher",
    "しらべる": "vérifier",
    "確かめる": "confirmer, vérifier",
    "たしかめる": "confirmer",
    "試す": "essayer, tester",
    "ためす": "essayer",
    "努める": "s'efforcer, faire des efforts",
    "つとめる": "s'efforcer",
    "励む": "s'appliquer, travailler dur",
    "はげむ": "s'appliquer",
    "挑む": "défier, relever un défi",
    "いどむ": "défier",
    "競う": "rivaliser, concourir",
    "きそう": "rivaliser",
    "争う": "se disputer, lutter",
    "あらそう": "se disputer",
    "戦う": "se battre, combattre",
    "たたかう": "se battre",

    # NEW ADDITIONS - Body parts and locations
    "側": "côté",
    "そば": "à côté de, près de",
    "辺り": "environs, alentours",
    "あたり": "environs, alentours",
    "向こう": "là-bas, de l'autre côté",
    "むこう": "là-bas",
    "背": "dos, taille",
    "せ": "dos, taille",
    "腹": "ventre, estomac",
    "はら": "ventre",
    "指": "doigt",
    "ゆび": "doigt",

    # NEW ADDITIONS - Time expressions
    "今から": "à partir de maintenant",
    "いまから": "à partir de maintenant",
    "さっき": "il y a un instant",
    "これから": "désormais, à partir de maintenant",
    "もしもし": "allô (au téléphone)",

    # NEW ADDITIONS - Counters
    "枚": "compteur (feuilles, papier)",
    "まい": "compteur (feuilles)",
    "冊": "compteur (livres)",
    "さつ": "compteur (livres)",
    "台": "compteur (machines, véhicules)",
    "だい": "compteur (machines)",
    "匹": "compteur (petits animaux)",
    "ひき": "compteur (animaux)",
    "杯": "compteur (boissons, bols)",
    "個": "compteur (objets)",
    "こ": "compteur (objets)",

    # NEW ADDITIONS - Adjectives
    "若い": "jeune",
    "わかい": "jeune",
    "太い": "gros, épais",
    "ふとい": "gros",
    "細い": "fin, mince",
    "ほそい": "fin",

    # NEW ADDITIONS - Katakana loanwords
    "テスト": "test, examen",
    "ノート": "cahier, carnet",
    "ページ": "page",
    "メートル": "mètre",
    "キロ": "kilo, kilomètre",
    "グラム": "gramme",
    "リットル": "litre",
    "センチ": "centimètre",
    "ミリ": "millimètre",

    # NEW ADDITIONS - N4 words
    "説得": "persuasion",
    "せっとく": "persuasion",
    "文句": "plainte, réclamation",
    "もんく": "plainte",
    "皆": "tout le monde, tous",
    "みんな": "tout le monde",
    "皆さん": "mesdames et messieurs, tout le monde (poli)",
    "みなさん": "tout le monde (poli)",

    # NEW ADDITIONS - N3 words
    "覚悟": "résolution, préparation mentale",
    "かくご": "résolution",
    "決意": "détermination, résolution",
    "けつい": "détermination",
    "意志": "volonté",
    "いし": "volonté",
    "勇気": "courage",
    "ゆうき": "courage",
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


def translate_with_deepl(text: str, source: str = "JA", target: str = "FR", timeout: int = 10) -> Optional[str]:
    """
    Translate text using DeepL API.

    DeepL provides high-quality machine translation. This function handles both
    word-level and sentence-level translations with robust error handling.

    Args:
        text: Japanese text to translate
        source: Source language code (default: "JA" for Japanese)
        target: Target language code (default: "FR" for French)
        timeout: Request timeout in seconds

    Returns:
        Translated French text, or None if translation fails

    Example:
        >>> translate_with_deepl("勉強")
        "étude"
        >>> translate_with_deepl("私は日本語を勉強しています")
        "J'étudie le japonais"
    """
    # Check if API key is configured
    if not DEEPL_API_KEY or DEEPL_API_KEY == "your-deepl-api-key-here":
        logger.debug("DeepL API key not configured, skipping DeepL translation")
        return None

    try:
        # DeepL API request
        headers = {
            "Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "text": [text],
            "source_lang": source,
            "target_lang": target
        }

        response = requests.post(
            DEEPL_API_URL,
            headers=headers,
            json=data,
            timeout=timeout
        )

        # Handle specific error codes
        if response.status_code == 403:
            logger.error("DeepL API authentication failed (403) - check your API key")
            return None
        elif response.status_code == 456:
            logger.error("DeepL API quota exceeded (456) - upgrade your plan or wait")
            return None
        elif response.status_code == 429:
            logger.warning("DeepL API rate limit hit (429) - too many requests")
            return None

        response.raise_for_status()

        result = response.json()

        # Extract translation from response
        if result.get("translations") and len(result["translations"]) > 0:
            translation = result["translations"][0]["text"]
            logger.info(f"DeepL translation for '{text[:30]}...': {translation[:50]}...")
            return translation

        logger.warning(f"No DeepL translation found for '{text[:30]}...'")
        return None

    except requests.Timeout:
        logger.error(f"DeepL API timeout for text '{text[:30]}...'")
        return None
    except requests.RequestException as e:
        logger.error(f"DeepL API request failed for '{text[:30]}...': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in DeepL translation for '{text[:30]}...': {e}")
        return None


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

    # Strategy 4: Try DeepL translation (if API key is configured)
    if DEEPL_API_KEY and DEEPL_API_KEY != "your-deepl-api-key-here":
        deepl_translation = translate_with_deepl(word)

        if deepl_translation:
            # Add to cache for future use
            cache[word] = deepl_translation
            _translation_cache[word] = deepl_translation
            _cache_modified = True

            logger.info(f"DeepL word translation for '{word}': {deepl_translation}")
            return deepl_translation

    # Strategy 5: Query Jisho API (if enabled) - now returns English only as last resort
    if use_jisho:
        jisho_result = get_jisho_translation(word)

        if jisho_result and 'english' in jisho_result:
            # Return English with a note (last resort when DeepL unavailable)
            translation = f"{jisho_result['english']} (EN)"

            # Add to cache
            cache[word] = translation
            _translation_cache[word] = translation
            _cache_modified = True

            return translation

    # Strategy 6: Helpful fallback
    fallback = "[Traduction manquante]"
    logger.warning(f"No translation found for '{word}', using fallback")

    return fallback


def translate_sentence(sentence: str) -> str:
    """
    Translate full Japanese sentence to French using DeepL.

    Uses DeepL API for professional-quality sentence translation.
    Falls back to a helpful message if DeepL is unavailable.

    Args:
        sentence: Japanese sentence to translate

    Returns:
        French translation of the sentence

    Example:
        >>> translate_sentence("私は日本語を勉強しています")
        "J'étudie le japonais"
    """
    logger.info(f"Sentence translation requested for: {sentence[:50]}...")

    # Try DeepL translation first
    if DEEPL_API_KEY and DEEPL_API_KEY != "your-deepl-api-key-here":
        deepl_translation = translate_with_deepl(sentence)

        if deepl_translation:
            logger.info(f"DeepL sentence translation successful")
            return deepl_translation

    # Fallback if DeepL unavailable or failed
    fallback = "[Traduction de phrase complète indisponible - configurez DeepL API]"
    logger.warning("DeepL API not configured or failed, using fallback message")

    return fallback


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
