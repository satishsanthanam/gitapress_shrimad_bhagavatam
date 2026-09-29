import json
import logging
import os
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("run.log", mode="w", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

DEVA_TO_ASCII = str.maketrans("०१२३४५६७८९", "0123456789")


def deva_to_int(num_str: str) -> int:
    return int(num_str.translate(DEVA_TO_ASCII))


def is_devanagari_line(text: str) -> bool:
    devanagari_chars = len(re.findall(r"[\u0900-\u097F]", text))
    latin_chars = len(re.findall(r"[a-zA-Z]", text))
    return devanagari_chars > latin_chars


def parse_aligned_markdown(md_file="markdown_aligned.md", output_dir="mahatmya_json"):
    if not os.path.exists(md_file):
        logging.error(f"File '{md_file}' not found.")
        return

    logging.info(f"📖 Reading '{md_file}' split by '^^^^$$$$'...")
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    os.makedirs(output_dir, exist_ok=True)

    # Split document by chapter delimiter
    raw_chapters = [
        ch.strip() for ch in content.split("^^^^$$$$") if ch.strip()
    ]

    for ch_idx, ch_content in enumerate(raw_chapters, start=1):
        chapter_entries = parse_single_chapter(ch_content)

        if chapter_entries:
            out_file = os.path.join(output_dir, f"mahatmya_ch{ch_idx:02d}.json")
            with open(out_file, "w", encoding="utf-8") as out:
                json.dump(chapter_entries, out, ensure_ascii=False, indent=2)
            logging.info(
                f"✅ Saved Chapter {ch_idx} JSON ({len(chapter_entries)} entries) -> '{out_file}'"
            )


def parse_single_chapter(ch_content):
    lines = ch_content.splitlines()

    entries = []
    san_lines = []
    eng_lines = []
    current_lang = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        line_lang = "SAN" if is_devanagari_line(line) else "ENG"

        if current_lang == "ENG" and line_lang == "SAN":
            entry = process_buffers(san_lines, eng_lines)
            if entry:
                entries.append(entry)
            san_lines = []
            eng_lines = []

        current_lang = line_lang

        if current_lang == "SAN":
            san_lines.append(line)
        else:
            eng_lines.append(line)

    if san_lines or eng_lines:
        entry = process_buffers(san_lines, eng_lines)
        if entry:
            entries.append(entry)

    return entries


def process_buffers(san_lines, eng_lines):
    if not san_lines and not eng_lines:
        return None

    san_text = "\n".join(san_lines).strip()
    eng_text = "\n".join(eng_lines).strip()

    # Clean colophons/invocations when looking for verse numbers
    san_clean_for_nums = re.sub(
        r"इति\s+श्रीपद्मपुराणे.*", "", san_text, flags=re.DOTALL
    )
    san_clean_for_nums = re.sub(
        r"इति\s+श्रीमद्भागवते.*", "", san_clean_for_nums, flags=re.DOTALL
    )

    san_vnums = re.findall(r"॥\s*([०-९\d]+)\s*॥", san_clean_for_nums)

    if san_vnums:
        start_v = deva_to_int(san_vnums[0])
        end_v = deva_to_int(san_vnums[-1])
        v_num = start_v
        range_str = str(start_v) if start_v == end_v else f"{start_v}-{end_v}"
    else:
        v_num = 0
        range_str = "Preamble"

    # Add 2 spaces before \n after (nn) or (nn-mm) to force <br /> in Markdown HTML rendering
    clean_eng = re.sub(r"(\([\d\s\-—–]+\))", r"\1  \n", eng_text).strip()

    return {
        "verse_number": v_num,
        "verse_range": range_str,
        "sanskrit": san_text,
        "english": clean_eng,
    }


if __name__ == "__main__":
    parse_aligned_markdown("markdown_aligned.md", "mahatmya_json")