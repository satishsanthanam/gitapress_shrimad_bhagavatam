import json
import logging
import os
import re

# Configure logging
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("run.log", mode="w", encoding="utf-8")
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

DEVA_TO_ASCII = str.maketrans("०१२३४५६७८९", "0123456789")


def deva_to_int(num_str: str) -> int:
    """Converts a Devanagari numeral string to an integer."""
    clean_num = num_str.translate(DEVA_TO_ASCII)
    return int(clean_num)


def parse_sanskrit_mahatmya(san_file="san_00.txt"):
    """Parses san_00.txt into chapters and verse numbers using regex finditer."""
    if not os.path.exists(san_file):
        logging.error(f"Sanskrit file '{san_file}' does not exist.")
        return {}

    logging.info(f"Parsing Sanskrit baseline file: '{san_file}'")
    with open(san_file, "r", encoding="utf-8") as f:
        content = f.read()

    chapters = {}

    # Match chapter headers like '॥ प्रथमोऽध्यायः - १ ॥' or '॥ द्वितीयोऽध्यायः - २ ॥'
    header_matches = list(
        re.finditer(r"॥\s*[^॥]*?अध्यायः\s*[-–—]?\s*([०-९\d]+)\s*॥", content)
    )

    if not header_matches:
        logging.warning("Failed to split chapters using chapter header regex.")
        return {}

    for i in range(len(header_matches)):
        match = header_matches[i]
        ch_num = deva_to_int(match.group(1))

        start_pos = match.end()
        end_pos = (
            header_matches[i + 1].start()
            if i + 1 < len(header_matches)
            else len(content)
        )

        ch_body = content[start_pos:end_pos].strip()

        verses = {}
        # Split verses by numbers like ॥ १॥, ॥ २॥
        v_blocks = re.split(r"॥\s*([०-९\d]+)\s*॥", ch_body)

        for v_idx in range(1, len(v_blocks), 2):
            v_num = deva_to_int(v_blocks[v_idx])
            v_text = v_blocks[v_idx - 1].strip()
            v_text_clean = "\n".join(
                [line.strip() for line in v_text.split("\n") if line.strip()]
            )
            verses[v_num] = v_text_clean

        chapters[ch_num] = verses
        logging.info(
            f"Extracted Chapter {ch_num}: Found {len(verses)} Sanskrit verses."
        )

    return chapters


def parse_english_mahatmya(md_file="markdown_clean_00.md"):
    """Parses markdown_clean_00.md to extract English translations by Discourse."""
    if not os.path.exists(md_file):
        logging.error(f"Markdown file '{md_file}' does not exist.")
        return {}

    logging.info(f"Parsing English Markdown file: '{md_file}'")
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Strip out all <sanskrit>...</sanskrit> tags
    english_only = re.sub(
        r"<sanskrit>.*?</sanskrit>", "", content, flags=re.DOTALL
    )

    discourses = {}
    disc_blocks = re.split(
        r"(?:Discourse|Dis\.)\s+([I|V|X\d]+)", english_only, flags=re.IGNORECASE
    )

    for i in range(1, len(disc_blocks), 2):
        disc_num = i // 2 + 1
        disc_body = disc_blocks[i + 1].strip()

        verse_ranges = []
        matches = re.findall(
            r"(.*?)\((\d+(?:\s*[\-—–]\s*\d+)?)\)", disc_body, re.DOTALL
        )

        for text_block, v_range in matches:
            clean_text = re.sub(r"\s+", " ", text_block).strip()
            clean_text = re.sub(
                r"^\*\*(.*?)\*\*\s*:\s*", "", clean_text, flags=re.IGNORECASE
            )

            range_clean = re.sub(r"\s*", "", v_range)
            if any(sep in range_clean for sep in ["-", "—", "–"]):
                parts = re.split(r"[\-—–]", range_clean)
                start, end = int(parts[0]), int(parts[1])
            else:
                start = end = int(range_clean)

            verse_ranges.append(
                {
                    "start_verse": start,
                    "end_verse": end,
                    "range_str": v_range.strip(),
                    "english_text": clean_text,
                }
            )

        discourses[disc_num] = verse_ranges
        logging.info(
            f"Extracted Discourse {disc_num}: Found {len(verse_ranges)} translation blocks."
        )

    return discourses


def align_and_build_json():
    san_chapters = parse_sanskrit_mahatmya("san_00.txt")
    eng_discourses = parse_english_mahatmya("markdown_clean_00.md")

    if not san_chapters:
        logging.error("No Sanskrit chapters parsed. Halting JSON generation.")
        return

    output_dir = "mahatmya_json"
    os.makedirs(output_dir, exist_ok=True)

    for ch_num, san_verses in san_chapters.items():
        eng_ranges = eng_discourses.get(ch_num, [])
        aligned_chapter = []

        unmapped_verses = 0
        for v_num in sorted(san_verses.keys()):
            san_text = san_verses[v_num]
            eng_text = ""
            range_str = str(v_num)

            matched = False
            for item in eng_ranges:
                if item["start_verse"] <= v_num <= item["end_verse"]:
                    range_str = item["range_str"]
                    if v_num == item["start_verse"]:
                        eng_text = item["english_text"]
                    else:
                        eng_text = f"[Combined translation with Verse {item['start_verse']}]"
                    matched = True
                    break

            if not matched:
                unmapped_verses += 1
                logging.warning(
                    f"Chapter {ch_num}, Verse {v_num} has no matching English translation."
                )

            aligned_chapter.append(
                {
                    "verse_number": v_num,
                    "verse_range": range_str,
                    "sanskrit": san_text,
                    "english": eng_text,
                }
            )

        out_file = os.path.join(output_dir, f"mahatmya_ch{ch_num:02d}.json")
        with open(out_file, "w", encoding="utf-8") as out:
            json.dump(aligned_chapter, out, ensure_ascii=False, indent=2)

        logging.info(
            f"Saved '{out_file}' ({len(aligned_chapter)} verses, {unmapped_verses} unmapped)."
        )


if __name__ == "__main__":
    align_and_build_json()