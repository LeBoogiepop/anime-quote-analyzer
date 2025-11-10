"""
Japanese grammar pattern detector.

This module detects common Japanese grammar patterns in text and provides
French explanations for each pattern.

Patterns are detected using regex matching and token analysis.

Author: Maxime
"""

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


def detect_patterns(text: str, tokens: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Detect grammar patterns in Japanese text.

    Searches for common grammatical constructions and returns explanations
    in French for language learners.

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
                "example": "勉強しています (étudier)"
            },
            ...
        ]

    Example:
        >>> detect_patterns("勉強しています", tokens)
        [{"pattern": "～ています", "description": "...", ...}]
    """
    detected = []

    # Pattern matching rules
    # Each rule checks for specific patterns in the text

    # ～ています (Present progressive/continuous)
    if "ています" in text:
        detected.append({
            "pattern": "～ています",
            "description": "Forme progressive/continue. Utilisée pour les actions en cours ou les états.",
            "jlptLevel": "N5",
            "example": "勉強しています (étudier)"
        })

    # ～ます (Polite present/future)
    elif "ます" in text and "ています" not in text:  # Avoid double-counting
        detected.append({
            "pattern": "～ます",
            "description": "Forme polie présent/futur des verbes.",
            "jlptLevel": "N5",
            "example": "行きます (aller)"
        })

    # ～です (Copula - "to be")
    if "です" in text:
        detected.append({
            "pattern": "～です",
            "description": "Copule polie. Utilisée pour exprimer 'être'.",
            "jlptLevel": "N5",
            "example": "学生です (être étudiant)"
        })

    # ～ました (Past polite)
    if "ました" in text:
        detected.append({
            "pattern": "～ました",
            "description": "Forme polie du passé des verbes.",
            "jlptLevel": "N5",
            "example": "行きました (suis allé)"
        })

    # ～でした (Past copula)
    if "でした" in text:
        detected.append({
            "pattern": "～でした",
            "description": "Copule polie au passé.",
            "jlptLevel": "N5",
            "example": "学生でした (étais étudiant)"
        })

    # ～たい (Want to do)
    if "たい" in text:
        detected.append({
            "pattern": "～たい",
            "description": "Forme du désir. Exprime 'vouloir faire quelque chose'.",
            "jlptLevel": "N5",
            "example": "食べたい (vouloir manger)"
        })

    # ～ない (Negative)
    if "ない" in text:
        detected.append({
            "pattern": "～ない",
            "description": "Forme négative des verbes.",
            "jlptLevel": "N5",
            "example": "行かない (ne pas aller)"
        })

    # ～ません (Polite negative)
    if "ません" in text:
        detected.append({
            "pattern": "～ません",
            "description": "Forme négative polie des verbes.",
            "jlptLevel": "N5",
            "example": "行きません (ne vais pas)"
        })

    # ～ませんか (Polite invitation)
    if "ませんか" in text:
        detected.append({
            "pattern": "～ませんか",
            "description": "Forme interrogative négative. Utilisée pour faire des invitations polies.",
            "jlptLevel": "N5",
            "example": "行きませんか (voulez-vous aller?)"
        })

    # ～でしょう (Probably/conjecture)
    if "でしょう" in text:
        detected.append({
            "pattern": "～でしょう",
            "description": "Marqueur de probabilité/conjecture. Exprime 'probablement' ou 'je pense'.",
            "jlptLevel": "N4",
            "example": "雨でしょう (probablement de la pluie)"
        })

    # ～そうです (Hearsay/It seems)
    if "そうです" in text:
        detected.append({
            "pattern": "～そうです",
            "description": "Exprime l'ouï-dire ou l'apparence. 'On dit que' ou 'Il semble que'.",
            "jlptLevel": "N4",
            "example": "美味しそうです (ça a l'air délicieux)"
        })

    # ～てください (Please do)
    if "てください" in text or "でください" in text:
        detected.append({
            "pattern": "～てください",
            "description": "Forme de requête polie. 'Veuillez faire' ou 's'il vous plaît'.",
            "jlptLevel": "N5",
            "example": "見てください (veuillez regarder)"
        })

    # ～てもいい (Permission - may/can)
    if "てもいい" in text or "でもいい" in text:
        detected.append({
            "pattern": "～てもいい",
            "description": "Exprime la permission. 'Peut' ou 'il est permis de'.",
            "jlptLevel": "N4",
            "example": "食べてもいい (tu peux manger)"
        })

    # ～なければならない (Must/have to)
    if "なければならない" in text or "なきゃ" in text:
        detected.append({
            "pattern": "～なければならない",
            "description": "Exprime l'obligation. 'Doit' ou 'il faut'.",
            "jlptLevel": "N4",
            "example": "行かなければならない (je dois aller)"
        })

    # If no patterns detected, add basic default
    if not detected:
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
