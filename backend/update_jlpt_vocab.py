#!/usr/bin/env python3
"""Update JLPT vocabulary with missing words."""

import json
from pathlib import Path

# Words to add with their JLPT levels
NEW_VOCAB = {
    "N5": [
        "コーヒー",  # café
        "ジュース",  # jus
        "ミルク",    # lait
        "パン",      # pain
        "苦い",      # amer
        "にがい",    # amer
        "やつ",      # type/personne
        "奴",        # type/personne
        "返る",      # retourner
        "かえる",    # retourner (already might exist, check)
        "見せる",    # montrer
        "みせる",    # montrer
    ],
    "N4": [
        "ブラック",  # noir (café)
        "苦手",      # pas doué
        "にがて",    # pas doué
        "逸れる",    # s'écarter
        "それる",    # s'écarter
        "散々",      # terriblement
        "さんざん",  # terriblement
        "チャリ",    # vélo (argot)
        "テスト",    # test
        "レベル",    # niveau
        "スタイル",  # style
        "サンド",    # sandwich
        "ハンバーガー", # hamburger
        "ケーキ",    # gâteau
        "見せ合う",  # se montrer mutuellement
        "みせあう",  # se montrer mutuellement
    ]
}

def main():
    # Load existing vocab
    vocab_file = Path(__file__).parent / "data" / "jlpt_vocab.json"

    with open(vocab_file, 'r', encoding='utf-8') as f:
        vocab = json.load(f)

    # Add new words (avoid duplicates)
    added_count = 0
    for level, words in NEW_VOCAB.items():
        if level not in vocab:
            vocab[level] = []

        for word in words:
            if word not in vocab[level]:
                vocab[level].append(word)
                added_count += 1
                print(f"Added '{word}' to {level}")
            else:
                print(f"'{word}' already exists in {level}")

    # Save updated vocab
    with open(vocab_file, 'w', encoding='utf-8') as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Added {added_count} new words to jlpt_vocab.json")
    print(f"  N5: {len(vocab['N5'])} words")
    print(f"  N4: {len(vocab['N4'])} words")
    print(f"  N3: {len(vocab['N3'])} words")

if __name__ == "__main__":
    main()
