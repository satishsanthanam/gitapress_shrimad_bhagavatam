import logging
import os
import re

# Configure logging to write to both run.log and stdout
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# File Handler
file_handler = logging.FileHandler("run.log", mode="a", encoding="utf-8")
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)


def is_devanagari_line(line: str) -> bool:
    """Returns True if the line contains Devanagari text (excluding pure English with Devanagari digits)."""
    # Matches Devanagari characters outside the pure digit range \u0966-\u096F
    return bool(re.search(r"[\u0900-\u0965\u0970-\u097F]", line))


def fix_sanskrit_verse_format(text: str) -> str:
    """Formats Sanskrit verses into clean two-line hemistichs ending with ॥ number ॥."""
    # 1. Split merged half-verses at single danda '।' if followed by Devanagari text on the same line
    text = re.sub(r"(।)\s*([\u0900-\u097F])", r"\1\n\2", text)

    # 2. Join orphaned verse numbers on a new line back to the end of the previous line
    text = re.sub(
        r"(\r?\n)\s*([०-९\d]+)\s*।?", r" ॥ \2 ॥", text
    )

    # 3. Standardize verse numbers ending with double dandas
    text = re.sub(
        r"।\s*॥\s*([०-९\d]+)\s*॥", r"॥ \1 ॥", text
    )

    return text


def clean_and_wrap_markdown(
    input_path="markdown_clean.md",
    output_path="markdown_clean_03.md",
):
    if not os.path.exists(input_path):
        logging.error(f"Input file '{input_path}' not found.")
        return

    logging.info(f"🧹 Reading raw content from '{input_path}'...")

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Remove image tags, captions, and decorative dividers
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"—\s*::\s*x\s*::\s*—", "", text)

    # 2. Remove discourse and page tags: [ Dis. 1 ], [Dis. 4], Dis. 1 ], Dis. 6]
    text = re.sub(r"\[\s*Dis\.\s*\d+\s*\]?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Dis\.\s*\d+\s*\]", "", text, flags=re.IGNORECASE)

    # 3. Remove standalone running header titles
    text = re.sub(
        r"^\s*ŚRĪMAD\s+BHĀGAVATA(-MĀHĀTMYA)?\s*$",
        "",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    text = re.sub(
        r"^\s*BOOK\s+(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT)\s*$",
        "",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # 4. Remove standalone page numbers (lines consisting of only digits)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # 5. Fix Sanskrit verse formatting (half-verse splits and verse numbers)
    logging.info("🛠️ Formatting half-verses and verse numbering layout...")
    text = fix_sanskrit_verse_format(text)

    # 6. Wrap contiguous Sanskrit Devanagari lines in <sanskrit>...</sanskrit>
    logging.info(
        "📦 Wrapping Devanagari Sanskrit lines in <sanskrit>...</sanskrit> tags..."
    )
    lines = text.splitlines(keepends=True)
    processed_lines = []
    in_sanskrit_block = False

    for line in lines:
        stripped = line.strip()

        if stripped and is_devanagari_line(stripped):
            if not in_sanskrit_block:
                processed_lines.append("<sanskrit>\n")
                in_sanskrit_block = True
            processed_lines.append(line)
        else:
            if in_sanskrit_block:
                processed_lines.append("</sanskrit>\n")
                in_sanskrit_block = False
            processed_lines.append(line)

    if in_sanskrit_block:
        processed_lines.append("</sanskrit>\n")

    cleaned_text = "".join(processed_lines)

    # 7. Normalize blank lines
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text.strip())

    logging.info(
        f"✨ Cleaning and wrapping complete! Saved output to '{output_path}'."
    )


if __name__ == "__main__":
    clean_and_wrap_markdown("markdown_04.md", "markdown_clean_04.md")