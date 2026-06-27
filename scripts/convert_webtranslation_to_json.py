#!/usr/bin/env python3
"""Convert WEB per-book JSON files to bible-translation.schema.json format."""

# example usage:
# python3 scripts/convert_webtranslation_to_json.py

import argparse
import json
import os
import re
import sys

ROMAN_NUMERALS = {1: "I", 2: "II", 3: "III"}

# Protestant canon book order; filenames match json/*.json stems.
BOOK_FILES = [
    "genesis",
    "exodus",
    "leviticus",
    "numbers",
    "deuteronomy",
    "joshua",
    "judges",
    "ruth",
    "1samuel",
    "2samuel",
    "1kings",
    "2kings",
    "1chronicles",
    "2chronicles",
    "ezra",
    "nehemiah",
    "esther",
    "job",
    "psalms",
    "proverbs",
    "ecclesiastes",
    "songofsolomon",
    "isaiah",
    "jeremiah",
    "lamentations",
    "ezekiel",
    "daniel",
    "hosea",
    "joel",
    "amos",
    "obadiah",
    "jonah",
    "micah",
    "nahum",
    "habakkuk",
    "zephaniah",
    "haggai",
    "zechariah",
    "malachi",
    "matthew",
    "mark",
    "luke",
    "john",
    "acts",
    "romans",
    "1corinthians",
    "2corinthians",
    "galatians",
    "ephesians",
    "philippians",
    "colossians",
    "1thessalonians",
    "2thessalonians",
    "1timothy",
    "2timothy",
    "titus",
    "philemon",
    "hebrews",
    "james",
    "1peter",
    "2peter",
    "1john",
    "2john",
    "3john",
    "jude",
    "revelation",
]

MULTI_WORD_BOOKS = {
    "songofsolomon": "Song Of Solomon",
}

TEXT_TYPES = frozenset({"paragraph text", "line text"})


def filename_to_book_name(stem: str) -> str:
    """Map a json/*.json filename stem to a display name."""
    if stem in MULTI_WORD_BOOKS:
        return MULTI_WORD_BOOKS[stem]

    # For consistency, map "revelation" to "Revelation of John"
    if stem == "revelation":
        return "Revelation of John"

    match = re.match(r"^(\d+)(.+)$", stem)
    if match:
        number = int(match.group(1))
        remainder = match.group(2)
        if number not in ROMAN_NUMERALS:
            raise ValueError(f"Unsupported book number prefix in '{stem}'")
        return f"{ROMAN_NUMERALS[number]} {remainder.title()}"

    return stem.title()


def convert_book_items(items: list) -> list:
    """Convert a WEB book file (array of typed elements) to schema chapters."""
    chapter_verses: dict[int, dict[int, list[str]]] = {}

    for item in items:
        if item.get("type") not in TEXT_TYPES:
            continue

        chapter_number = item["chapterNumber"]
        verse_number = item["verseNumber"]
        chapter_verses.setdefault(chapter_number, {}).setdefault(verse_number, []).append(
            item["value"]
        )

    chapters = []
    for chapter_number in sorted(chapter_verses):
        verses = []
        for verse_number in sorted(chapter_verses[chapter_number]):
            verses.append(
                {
                    "verse": verse_number,
                    "text": "".join(chapter_verses[chapter_number][verse_number]),
                }
            )
        chapters.append({"chapter": chapter_number, "verses": verses})

    return chapters


def convert_web_translation(
    input_dir: str,
    translation: str = "WEB: World English Bible",
) -> dict:
    books = []

    for stem in BOOK_FILES:
        path = os.path.join(input_dir, f"{stem}.json")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Missing expected book file: {path}")

        with open(path, encoding="utf-8") as handle:
            items = json.load(handle)

        books.append(
            {
                "name": filename_to_book_name(stem),
                "chapters": convert_book_items(items),
            }
        )

    return {"translation": translation, "books": books}


def main() -> int:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    web_dir = os.path.join(repo_root, "sources", "en", "WEB")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        default=os.path.join(web_dir, "json"),
        help="Directory containing per-book WEB JSON files",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(web_dir, "WEB.json"),
        help="Output path for the combined translation JSON",
    )
    parser.add_argument(
        "--translation",
        default="WEB: World English Bible",
        help="Translation label written to the output file",
    )
    args = parser.parse_args()

    data = convert_web_translation(args.input_dir, args.translation)

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=4)

    print(f"Wrote {len(data['books'])} books to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
