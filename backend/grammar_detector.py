"""
Japanese grammar pattern detector.

This module detects common Japanese grammar patterns in text and provides
French explanations for each pattern.

Patterns are detected using regex matching and token analysis.

Author: Maxime
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global grammar patterns data
_grammar_patterns: List[Dict[str, Any]] = []


def load_grammar_patterns() -> List[Dict[str, Any]]:
    """
    Load grammar pattern definitions from JSON file.

    The data file contains pattern definitions:
    [
        {
            "pattern": "～ています",
            "regex": "ています$",
            "description": "Forme progressive/continue...",
            "jlptLevel": "N5",
            "example": "勉強しています"
        },
        ...
    ]

    Returns:
        List of grammar pattern dictionaries

    Raises:
        FileNotFoundError: If data file doesn't exist
        json.JSONDecodeError: If data file is malformed
    """
    global _grammar_patterns

    # Return cached data if already loaded
    if _grammar_patterns:
        return _grammar_patterns

    data_path = Path(__file__).parent / "data" / "grammar_patterns.json"

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            _grammar_patterns = json.load(f)

        logger.info(f"Loaded {len(_grammar_patterns)} grammar patterns")
        return _grammar_patterns

    except FileNotFoundError:
        logger.error(f"Grammar patterns file not found at {data_path}")
        return []

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse grammar patterns file: {e}")
        return []


def detect_particles(tokens: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
    """
    Detect Japanese particles (助詞) from tokens and return pedagogical explanations.

    Args:
        tokens: List of token dictionaries with 'surface' and 'partOfSpeech' keys
        text: Original Japanese text for context extraction

    Returns:
        List of particle pattern dictionaries with descriptions and pedagogical notes
    """
    particles_found = []
    seen_particles = set()

    # Particle definitions with French explanations
    particle_info = {
        "は": {
            "description": "Marqueur de thème. Introduit le sujet principal dont on parle.",
            "jlptLevel": "N5",
            "example": "私は学生です (Quant à moi, je suis étudiant)",
            "pedagogicalNote": "Indique le thème général de la phrase. Différent de が qui marque le sujet grammatical."
        },
        "が": {
            "description": "Marqueur de sujet grammatical. Identifie qui/quoi fait l'action.",
            "jlptLevel": "N5",
            "example": "雨が降る (La pluie tombe)",
            "pedagogicalNote": "Insiste sur le sujet spécifique. Utilisé pour contraster ou répondre à 'qui/quoi?'"
        },
        "を": {
            "description": "Marqueur d'objet direct. Indique ce qui subit l'action du verbe.",
            "jlptLevel": "N5",
            "example": "本を読む (Lire un livre)",
            "pedagogicalNote": "Toujours placé après l'objet direct et avant le verbe."
        },
        "に": {
            "description": "Marqueur de destination, temps, cible ou existence.",
            "jlptLevel": "N5",
            "example": "学校に行く (Aller à l'école), 3時に (À 3h)",
            "pedagogicalNote": "Usages multiples: direction (vers), temps (à), cible (à/pour), existence (se trouver à)."
        },
        "で": {
            "description": "Marqueur de moyen, lieu d'action, cause ou limite.",
            "jlptLevel": "N5",
            "example": "車で行く (Y aller en voiture), 図書館で (À la bibliothèque)",
            "pedagogicalNote": "Indique le moyen (avec/en), le lieu de l'action (à/dans), ou la cause (à cause de)."
        },
        "も": {
            "description": "Particule d'inclusion. Signifie 'aussi' ou 'même'.",
            "jlptLevel": "N5",
            "example": "私も学生です (Moi aussi je suis étudiant)",
            "pedagogicalNote": "Remplace は, が, を pour ajouter la nuance 'aussi'. Peut marquer l'emphase avec des nombres."
        },
        "の": {
            "description": "Marqueur de possession, appartenance ou nominalisation.",
            "jlptLevel": "N5",
            "example": "私の本 (Mon livre), 食べるの (Le fait de manger)",
            "pedagogicalNote": "Relie deux noms (possession) ou transforme une proposition en nom (nominalisation)."
        },
        "から": {
            "description": "Indique le point de départ (spatial/temporel) ou la cause.",
            "jlptLevel": "N5",
            "example": "東京から (Depuis Tokyo), 忙しいから (Parce que je suis occupé)",
            "pedagogicalNote": "Origine dans l'espace/temps ('depuis'), ou raison/cause ('parce que', 'car')."
        },
        "まで": {
            "description": "Indique la limite ou le point d'arrivée (spatial/temporel).",
            "jlptLevel": "N5",
            "example": "駅まで (Jusqu'à la gare), 5時まで (Jusqu'à 5h)",
            "pedagogicalNote": "Souvent combiné avec から pour exprimer 'de...à'. Marque la fin d'une période/distance."
        },
        "と": {
            "description": "Conjonction de coordination ('et') ou citation ('que').",
            "jlptLevel": "N5",
            "example": "猫と犬 (Chats et chiens), 彼は行くと言った (Il a dit qu'il irait)",
            "pedagogicalNote": "Relie des noms ('et'), introduit une citation directe, ou marque l'accompagnement ('avec')."
        },
        "や": {
            "description": "Conjonction d'énumération partielle. 'Et', 'ou' (liste non exhaustive).",
            "jlptLevel": "N4",
            "example": "りんごやバナナ (Pommes, bananes, etc.)",
            "pedagogicalNote": "Énumération ouverte (implique qu'il y a d'autres éléments). Moins formel que と."
        },
        "か": {
            "description": "Marqueur interrogatif ou de choix.",
            "jlptLevel": "N5",
            "example": "行きますか (Allez-vous?), コーヒーかお茶 (Café ou thé)",
            "pedagogicalNote": "En fin de phrase: question. Entre noms: choix ('ou'). Ton monte à l'oral."
        },
        "ね": {
            "description": "Particule finale de confirmation ou accord.",
            "jlptLevel": "N5",
            "example": "いい天気ですね (Beau temps, n'est-ce pas?)",
            "pedagogicalNote": "Cherche l'accord de l'interlocuteur. Adoucit la phrase. Ton chaleureux."
        },
        "よ": {
            "description": "Particule finale d'affirmation ou nouvelle information.",
            "jlptLevel": "N5",
            "example": "雨が降るよ (Il va pleuvoir, tu sais)",
            "pedagogicalNote": "Insiste sur l'information donnée. Ton assertif. Informe l'interlocuteur de quelque chose."
        },
        "よね": {
            "description": "Combinaison de よ + ね. Confirmation avec attente d'accord.",
            "jlptLevel": "N4",
            "example": "美味しいよね (C'est bon, hein?)",
            "pedagogicalNote": "Affirme tout en cherchant la confirmation. Plus doux que よ seul. Très courant à l'oral."
        },
        "って": {
            "description": "Particule de citation informelle ou de reformulation.",
            "jlptLevel": "N4",
            "example": "田中さんって誰? (Tanaka, c'est qui?), 行くって言った (J'ai dit que j'irais)",
            "pedagogicalNote": "Contraction informelle de という. Citation indirecte, définition, ou reformulation. Ton décontracté."
        },
        "だけ": {
            "description": "Particule restrictive. Signifie 'seulement', 'uniquement'.",
            "jlptLevel": "N4",
            "example": "これだけ (Seulement ça)",
            "pedagogicalNote": "Limite à un élément spécifique. Peut exprimer une limite minimale ou un sentiment d'insuffisance."
        },
        "しか": {
            "description": "Particule restrictive négative. 'Seulement' (avec négation obligatoire).",
            "jlptLevel": "N4",
            "example": "100円しかない (Je n'ai que 100 yens)",
            "pedagogicalNote": "Toujours suivi d'une forme négative. Nuance de regret ou d'insuffisance. Plus fort que だけ."
        },
        "など": {
            "description": "Particule d'énumération exemplative. 'Etc.', 'et cetera', 'par exemple'.",
            "jlptLevel": "N4",
            "example": "本など (Des livres et autres choses)",
            "pedagogicalNote": "Suggère que les éléments mentionnés sont des exemples. Liste non exhaustive. Ton modeste."
        },
        "さ": {
            "description": "Particule finale de remplissage ou d'affirmation décontractée.",
            "jlptLevel": "N3",
            "example": "そうだよさ (C'est comme ça, tu vois)",
            "pedagogicalNote": "Marque un ton décontracté, familier. Remplissage conversationnel. Surtout utilisé par les hommes."
        },
        "ねえ": {
            "description": "Particule d'interpellation ou d'insistance.",
            "jlptLevel": "N4",
            "example": "ねえ、聞いて (Hé, écoute)",
            "pedagogicalNote": "Attire l'attention de l'interlocuteur. Ton amical ou insistant selon le contexte."
        },
        "わ": {
            "description": "Particule finale d'affirmation douce (surtout féminin).",
            "jlptLevel": "N3",
            "example": "行くわ (J'y vais)",
            "pedagogicalNote": "Marque un ton doux, souvent associé au langage féminin (Kansai ou Tokyo ancien). Affirmation légère."
        },
        "ぞ": {
            "description": "Particule finale d'affirmation forte (masculin).",
            "jlptLevel": "N3",
            "example": "行くぞ (On y va!)",
            "pedagogicalNote": "Ton viril, assertif. Utilisé principalement par les hommes. Marque détermination ou avertissement."
        },
        "ぜ": {
            "description": "Particule finale d'affirmation informelle (masculin).",
            "jlptLevel": "N3",
            "example": "いいぜ (C'est bon)",
            "pedagogicalNote": "Ton décontracté, masculin. Affirmation avec confiance. Plus doux que ぞ."
        }
    }

    # Extract particles from tokens
    for token in tokens:
        surface = token.get("surface", "")
        pos = token.get("partOfSpeech", "")

        # Check if this is a particle (助詞)
        if "助詞" in pos or "particle" in pos.lower():
            # Check if we have info for this particle
            if surface in particle_info and surface not in seen_particles:
                info = particle_info[surface]
                particles_found.append({
                    "pattern": surface,
                    "description": info["description"],
                    "jlptLevel": info["jlptLevel"],
                    "example": info["example"],
                    "exampleInSentence": f"...{surface}..." if surface in text else "",
                    "pedagogicalNote": info["pedagogicalNote"]
                })
                seen_particles.add(surface)

    # Special handling for combined particles like よね
    if "よね" in text and "よね" not in seen_particles:
        info = particle_info["よね"]
        particles_found.append({
            "pattern": "よね",
            "description": info["description"],
            "jlptLevel": info["jlptLevel"],
            "example": info["example"],
            "exampleInSentence": "よね",
            "pedagogicalNote": info["pedagogicalNote"]
        })
        seen_particles.add("よね")
        # Remove individual よ and ね if they were added
        particles_found = [p for p in particles_found if p["pattern"] not in ["よ", "ね"]]

    return particles_found


def detect_patterns(text: str, tokens: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Detect grammar patterns in Japanese text with contextual examples.

    Searches for common grammatical constructions and returns enriched explanations
    with real examples extracted from the sentence and pedagogical notes.

    Args:
        text: Original Japanese text
        tokens: List of token dictionaries from tokenization

    Returns:
        List of detected pattern dictionaries:
        [
            {
                "pattern": "～ています",
                "description": "Forme progressive/continue. Utilisée pour les actions en cours.",
                "jlptLevel": "N5",
                "example": "勉強しています (étudier)",
                "exampleInSentence": "勉強しています",
                "pedagogicalNote": "Forme polie. Pour l'informel, utilisez ～ている ou ～てる."
            },
            ...
        ]

    Example:
        >>> detect_patterns("勉強しています", tokens)
        [{"pattern": "～ています", "description": "...", "exampleInSentence": "勉強しています", ...}]
    """
    detected = []

    # Helper function to extract example from sentence
    def extract_example(regex_pattern: str, text: str) -> str:
        """Extract the actual match from the text."""
        match = re.search(regex_pattern, text)
        if match:
            # Try to get a bit of context (up to 10 chars before the match)
            start = max(0, match.start() - 10)
            end = min(len(text), match.end() + 2)
            excerpt = text[start:end].strip()
            return excerpt if len(excerpt) <= 20 else match.group(0)
        return ""

    # Pattern matching rules
    # Check patterns from MOST specific to LEAST specific to avoid double-counting
    # Use regex for flexible matching

    # Track which patterns we've already detected to avoid overlaps
    detected_patterns = set()

    # ～ませんか (Polite invitation) - Check BEFORE ～ません
    if re.search(r'ませんか', text):
        detected.append({
            "pattern": "～ませんか",
            "description": "Forme interrogative négative. Utilisée pour faire des invitations polies.",
            "jlptLevel": "N5",
            "example": "行きませんか (voulez-vous aller?)"
        })
        detected_patterns.add("ませんか")

    # ～なければならない (Must/have to) - Check BEFORE ～ない
    if re.search(r'なければならない|なきゃ', text):
        detected.append({
            "pattern": "～なければならない",
            "description": "Exprime l'obligation. 'Doit' ou 'il faut'.",
            "jlptLevel": "N4",
            "example": "行かなければならない (je dois aller)"
        })
        detected_patterns.add("obligation")

    # ～てもいい (Permission) - Check BEFORE ～て
    if re.search(r'[てで]もいい', text):
        detected.append({
            "pattern": "～てもいい",
            "description": "Exprime la permission. 'Peut' ou 'il est permis de'.",
            "jlptLevel": "N4",
            "example": "食べてもいい (tu peux manger)"
        })
        detected_patterns.add("permission")

    # ～てください (Please do) - Check BEFORE ～て
    if re.search(r'[てで]ください', text):
        detected.append({
            "pattern": "～てください",
            "description": "Forme de requête polie. 'Veuillez faire' ou 's'il vous plaît'.",
            "jlptLevel": "N5",
            "example": "見てください (veuillez regarder)"
        })
        detected_patterns.add("request")

    # ～ています (Present progressive/continuous) - Check FIRST (most specific)
    if re.search(r'ています', text):
        detected.append({
            "pattern": "～ています",
            "description": "Forme progressive/continue polie. Actions en cours ou états.",
            "jlptLevel": "N5",
            "example": "勉強しています (étudier)",
            "exampleInSentence": extract_example(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+ています', text),
            "pedagogicalNote": "Forme polie. Pour l'informel, utilisez ～ている ou la contraction ～てる."
        })
        detected_patterns.add("ています")

    # ～てる (Contracted progressive) - Check BEFORE ～ている
    # This catches contracted forms like 悩んでる, 食べてる, etc.
    elif re.search(r'[てで]る', text) and not re.search(r'[てで]ます', text):
        detected.append({
            "pattern": "～てる",
            "description": "Forme progressive contractée (informel). Même sens que ～ている.",
            "jlptLevel": "N5",
            "example": "食べてる (en train de manger), 悩んでる (être préoccupé)",
            "exampleInSentence": extract_example(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+[てで]る', text),
            "pedagogicalNote": "Contraction orale de ～ている. Utilisée entre amis/famille. Ton décontracté."
        })
        detected_patterns.add("てる")

    # ～ている (Resultant state) - Check AFTER ～ています and ～てる
    elif re.search(r'ている', text):
        detected.append({
            "pattern": "～ている",
            "description": "Exprime un état résultant ou une action en cours (forme informelle).",
            "jlptLevel": "N5",
            "example": "知っている (savoir / connaître)"
        })
        detected_patterns.add("ている")

    # ～ました (Past polite) - Check BEFORE ～ます
    if re.search(r'ました', text):
        detected.append({
            "pattern": "～ました",
            "description": "Forme polie du passé des verbes.",
            "jlptLevel": "N5",
            "example": "行きました (suis allé)"
        })
        detected_patterns.add("ました")

    # ～ません (Polite negative) - Check BEFORE ～ます (but AFTER ～ませんか)
    elif re.search(r'ません', text) and "ませんか" not in detected_patterns:
        detected.append({
            "pattern": "～ません",
            "description": "Forme négative polie des verbes.",
            "jlptLevel": "N5",
            "example": "行きません (ne vais pas)"
        })
        detected_patterns.add("ません")

    # ～ます (Polite present/future) - Check AFTER more specific ～ます patterns
    elif re.search(r'ます', text) and "ました" not in detected_patterns and "ません" not in detected_patterns:
        detected.append({
            "pattern": "～ます",
            "description": "Forme polie présent/futur des verbes.",
            "jlptLevel": "N5",
            "example": "行きます (aller)"
        })
        detected_patterns.add("ます")

    # ～でした (Past copula) - Check BEFORE ～です
    if re.search(r'でした', text):
        detected.append({
            "pattern": "～でした",
            "description": "Copule polie au passé.",
            "jlptLevel": "N5",
            "example": "学生でした (étais étudiant)"
        })
        detected_patterns.add("でした")

    # ～です (Copula - "to be") - Check AFTER ～でした
    elif re.search(r'です', text):
        detected.append({
            "pattern": "～です",
            "description": "Copule polie. Utilisée pour exprimer 'être'.",
            "jlptLevel": "N5",
            "example": "学生です (être étudiant)"
        })
        detected_patterns.add("です")

    # ～たい (Want to do) - Check BEFORE ～た
    if re.search(r'たい', text):
        detected.append({
            "pattern": "～たい",
            "description": "Forme du désir. Exprime 'vouloir faire quelque chose'.",
            "jlptLevel": "N5",
            "example": "食べたい (vouloir manger)"
        })
        detected_patterns.add("たい")

    # ～た (Past tense plain form) - Check AFTER ～たい and other た-patterns
    elif re.search(r'た', text) and "ました" not in detected_patterns and "たい" not in detected_patterns:
        detected.append({
            "pattern": "～た",
            "description": "Forme passée informelle des verbes.",
            "jlptLevel": "N5",
            "example": "食べた (j'ai mangé)",
            "exampleInSentence": extract_example(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+た', text),
            "pedagogicalNote": "Marque le passé ou un état accompli. Ton neutre/informel. Pour la politesse, utilisez ～ました."
        })
        detected_patterns.add("た")

    # ～ない (Negative) - Check AFTER obligation pattern
    if re.search(r'ない', text) and "obligation" not in detected_patterns:
        detected.append({
            "pattern": "～ない",
            "description": "Forme négative des verbes.",
            "jlptLevel": "N5",
            "example": "行かない (ne pas aller)",
            "exampleInSentence": extract_example(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+ない', text),
            "pedagogicalNote": "Négation informelle. Pour la politesse, utilisez ～ません. Souvent en fin de phrase."
        })
        detected_patterns.add("ない")

    # ～でしょう (Probably/conjecture)
    if re.search(r'でしょう', text):
        detected.append({
            "pattern": "～でしょう",
            "description": "Marqueur de probabilité/conjecture. Exprime 'probablement' ou 'je pense'.",
            "jlptLevel": "N4",
            "example": "雨でしょう (probablement de la pluie)"
        })
        detected_patterns.add("でしょう")

    # ～そうです (Hearsay/It seems)
    if re.search(r'そうです', text):
        detected.append({
            "pattern": "～そうです",
            "description": "Exprime l'ouï-dire ou l'apparence. 'On dit que' ou 'Il semble que'.",
            "jlptLevel": "N4",
            "example": "美味しそうです (ça a l'air délicieux)"
        })
        detected_patterns.add("そうです")

    # ～まで / ～までに (Until/by the time)
    if re.search(r'まで', text):
        detected.append({
            "pattern": "～まで / ～までに",
            "description": "Exprime une limite temporelle. 'Jusqu'à' ou 'd'ici'.",
            "jlptLevel": "N5",
            "example": "授業が終わるまでに (d'ici la fin du cours)"
        })
        detected_patterns.add("まで")

    # ～ように (In order to/so that)
    if re.search(r'ように', text):
        detected.append({
            "pattern": "～ように",
            "description": "Exprime le but ou la manière. 'Afin que' ou 'de manière à'.",
            "jlptLevel": "N3",
            "example": "忘れないように (afin de ne pas oublier)",
            "exampleInSentence": extract_example(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+ように', text),
            "pedagogicalNote": "Exprime le but ('pour que') ou la manière ('de manière à'). Souvent suivi d'un verbe."
        })
        detected_patterns.add("ように")

    # ～て form (Conjunctive/sequence) - Check AFTER more specific て patterns
    # Also skip if てる was detected (it's a contraction containing て)
    if re.search(r'て', text) and "request" not in detected_patterns and "permission" not in detected_patterns and "ています" not in detected_patterns and "ている" not in detected_patterns and "てる" not in detected_patterns:
        detected.append({
            "pattern": "～て",
            "description": "Forme conjonctive. Utilisée pour relier des actions ou des états.",
            "jlptLevel": "N5",
            "example": "食べて寝る (manger et dormir)",
            "exampleInSentence": extract_example(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+て', text),
            "pedagogicalNote": "Forme de liaison. Connecte des phrases, exprime la succession d'actions, ou précède des auxiliaires."
        })
        detected_patterns.add("て")

    # ～する (Verbal noun + する) - Common pattern
    if re.search(r'する', text):
        detected.append({
            "pattern": "～する",
            "description": "Verbe 'faire'. Souvent utilisé avec des noms verbaux (勉強する, 提出する).",
            "jlptLevel": "N5",
            "example": "勉強する (étudier)"
        })
        detected_patterns.add("する")

    # Detect particles (助詞) from tokens
    particle_patterns = detect_particles(tokens, text)
    for particle in particle_patterns:
        # Avoid duplicates
        if particle["pattern"] not in detected_patterns:
            detected.append(particle)
            detected_patterns.add(particle["pattern"])

    # If no substantial patterns detected, add basic default
    # Only add if we haven't found any verb/copula patterns
    if not detected or len(detected) == 0:
        detected.append({
            "pattern": "Phrase simple",
            "description": "Structure de phrase déclarative simple.",
            "jlptLevel": "N5",
            "example": "これは本です (Ceci est un livre)"
        })

    logger.info(f"Detected {len(detected)} grammar patterns")
    return detected


# Test function
if __name__ == "__main__":
    print("Testing Grammar Pattern Detector")
    print("=" * 50)

    test_cases = [
        "私は日本語を勉強しています",
        "学校に行きます",
        "これは本です",
        "昨日映画を見ました",
        "寿司が食べたい",
        "明日は雨でしょう",
    ]

    for text in test_cases:
        print(f"\nText: {text}")
        patterns = detect_patterns(text, [])  # Empty tokens for simple test
        for p in patterns:
            print(f"  - {p['pattern']:20s} ({p['jlptLevel']}) - {p['description'][:60]}...")
