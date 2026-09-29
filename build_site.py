import os
import re
from bs4 import BeautifulSoup

# Relative paths to output directories
HTML_DIR = "html_out"
TOC_FILE = os.path.join(HTML_DIR, "toc.md")
INDEX_FILE = os.path.join(HTML_DIR, "index.html")

# Global Footer
FOOTER_HTML = """
<footer class="doc-footer" style="margin-top: 3rem; padding: 1.5rem 0; border-top: 1px solid #e2e8f0; text-align: center; color: #64748b; font-size: 0.9rem;">
    <p><strong>🙏 Shri Krishnarpanam Asthu 🙏</strong> | Maintained &amp; published via <a href="https://ventpipe.blog/2026/09/29/shrimad-bhagavat-mahapurana/" target="_blank" rel="noopener noreferrer" style="color: #0284c7; text-decoration: none; font-weight: 500;">ventpipe.blog</a></p>
</footer>
"""


def parse_toc():
    """Parses TOC definitions from toc.md to construct Canto and Chapter title mappings."""
    toc_path = TOC_FILE if os.path.exists(TOC_FILE) else "toc.md"
    if not os.path.exists(toc_path):
        print(f"Error: Neither {TOC_FILE} nor 'toc.md' was found.")
        return {}, {}

    with open(toc_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    chapter_titles = {}
    canto_mapping = {
        "book zero": "00",
        "book one": "01",
        "book two": "02",
        "book three": "03",
        "book four": "04",
        "book five": "05",
        "book six": "06",
        "book seven": "07",
        "book eight": "08",
        "book nine": "09",
        "book ten": "10",
        "book eleven": "11",
        "book twelve": "12",
        "śrīmad bhāgavata-māhātmya": "00",
    }

    canto_titles = {
        "00": "Śrīmad Bhāgavata Māhātmya",
        "01": "Book One (First Canto)",
        "02": "Book Two (Second Canto)",
        "03": "Book Three (Third Canto)",
        "04": "Book Four (Fourth Canto)",
        "05": "Book Five (Fifth Canto)",
        "06": "Book Six (Sixth Canto)",
        "07": "Book Seven (Seventh Canto)",
        "08": "Book Eight (Eighth Canto)",
        "09": "Book Nine (Ninth Canto)",
        "10": "Book Ten (Tenth Canto)",
        "11": "Book Eleven (Eleventh Canto)",
        "12": "Book Twelve (Twelfth Canto)",
    }

    canto_data = {}
    current_canto = None

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue

        if re.match(r"^#+\s+", line_str):
            header_text = re.sub(r"^#+\s+", "", line_str).strip().lower()
            for key, val in canto_mapping.items():
                if key in header_text:
                    current_canto = val
                    if current_canto not in canto_data:
                        canto_data[current_canto] = {
                            "title": canto_titles.get(
                                current_canto, f"Canto {current_canto}"
                            ),
                            "chapters": [],
                        }
                    break

        match = re.match(r"^(\d+)\.\s+(.*)$", line_str)
        if match and current_canto:
            ch_num = int(match.group(1))
            raw_title = match.group(2).strip()
            cleaned_title = re.sub(r"\s+\d+$", "", raw_title)

            if not any(
                c["num"] == ch_num for c in canto_data[current_canto]["chapters"]
            ):
                chapter_titles[(current_canto, ch_num)] = cleaned_title
                canto_data[current_canto]["chapters"].append(
                    {"num": ch_num, "title": cleaned_title}
                )

    return canto_data, chapter_titles


def get_all_html_files():
    """Scans html_out/ and collects all structured chapter HTML files."""
    files_list = []
    if not os.path.exists(HTML_DIR):
        print(f"Error: Directory '{HTML_DIR}' does not exist.")
        return files_list

    for canto in sorted(os.listdir(HTML_DIR)):
        canto_path = os.path.join(HTML_DIR, canto)
        if os.path.isdir(canto_path) and canto.isdigit():
            c_files = sorted(
                [f for f in os.listdir(canto_path) if f.endswith(".html")]
            )
            for cf in c_files:
                match = re.search(r"(\d+)", cf)
                if match:
                    ch_num = int(match.group(1))
                    files_list.append(
                        {
                            "canto": canto,
                            "ch_num": ch_num,
                            "full_path": os.path.join(canto_path, cf),
                            "rel_path": f"{canto}/{cf}",
                        }
                    )
    return files_list


def inject_nav_and_pagefind(all_files, chapter_titles):
    """Injects responsive edge-to-edge styles, green hover accent, navigation, and Pagefind search attributes into all chapter HTML files."""
    print("Injecting Navigation, Edge-to-Edge Mobile CSS & Green Hover into HTML files...")

    nav_style = """
    <style id="custom-theme-fixes">
        :root {
            --hover-green: #e8f5e9 !important;
            --hover-green-border: #2e7d32 !important;
        }

        /* Global Box Sizing & Mobile Overflows */
        * {
            box-sizing: border-box !important;
        }
        html, body {
            overflow-x: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
        }
        .container {
            max-width: 1200px !important;
            width: 100% !important;
            margin: 0 auto !important;
            padding: 30px !important;
            box-sizing: border-box !important;
        }
        .parallel-table {
            width: 100% !important;
            table-layout: fixed !important;
            border-collapse: collapse !important;
            margin-top: 20px;
        }
        
        /* Forest Green Hover Accent */
        .parallel-table tbody tr:hover td,
        .parallel-table tbody tr:hover,
        .parallel-table tbody tr:active td {
            background-color: var(--hover-green) !important;
            border-left: 4px solid var(--hover-green-border) !important;
        }

        /* Mobile Viewport Edge-to-Edge Fixes */
        @media (max-width: 768px) {
            body {
                padding: 0 !important;
            }
            .container {
                padding: 10px 0 !important;
                margin: 0 !important;
                border: none !important;
                border-radius: 0 !important;
                box-shadow: none !important;
                width: 100% !important;
                max-width: 100vw !important;
                overflow-x: hidden !important;
            }
            .parallel-table, .parallel-table tbody, .parallel-table tr {
                display: block !important;
                width: 100% !important;
                max-width: 100% !important;
            }
            .parallel-table thead {
                display: none !important;
            }
            .sanskrit-col, .english-col {
                display: block !important;
                width: 100% !important;
                max-width: 100% !important;
                padding: 14px 16px !important;
                word-wrap: break-word !important;
                overflow-wrap: break-word !important;
            }
            .sanskrit-col {
                border-right: none !important;
                border-bottom: 1px dashed var(--border-color, #e2d9d0) !important;
            }
            /* Edge-to-Edge Background Shading */
            .parallel-table tr:nth-child(even) td {
                background-color: var(--verse-bg, #faf6f0);
            }
            .parallel-table tr:nth-child(odd) td {
                background-color: #ffffff;
            }
            .parallel-table tbody tr:active td,
            .parallel-table tbody tr:hover td {
                background-color: var(--hover-green) !important;
                border-left: 4px solid var(--hover-green-border) !important;
            }
            .page-nav {
                margin: 10px 12px !important;
            }
        }

        .page-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 20px 0;
            padding: 12px 16px;
            background-color: var(--verse-bg, #faf6f0);
            border: 1px solid var(--border-color, #e2d9d0);
            border-radius: 6px;
            font-size: 0.9em;
        }
        .page-nav a {
            color: var(--primary-color, #701c1c);
            text-decoration: none;
            font-weight: bold;
        }
        .page-nav a:hover {
            text-decoration: underline;
        }
        .page-nav .nav-home {
            font-weight: normal;
        }
    </style>
    """

    for idx, item in enumerate(all_files):
        full_path = item["full_path"]
        canto = item["canto"]
        ch_num = item["ch_num"]

        prev_item = all_files[idx - 1] if idx > 0 else None
        next_item = all_files[idx + 1] if idx < len(all_files) - 1 else None

        prev_link = f"../{prev_item['rel_path']}" if prev_item else None
        next_link = f"../{next_item['rel_path']}" if next_item else None
        home_link = "../index.html"

        title_text = chapter_titles.get((canto, ch_num), f"Chapter {ch_num}")

        prev_html = (
            f'<a href="{prev_link}">← Previous</a>'
            if prev_link
            else "<span></span>"
        )
        next_html = (
            f'<a href="{next_link}">Next →</a>'
            if next_link
            else "<span></span>"
        )
        home_html = f'<a href="{home_link}" class="nav-home">📜 TOC</a>'

        nav_bar = f"""
        <nav class="page-nav">
            {prev_html}
            {home_html}
            {next_html}
        </nav>
        """

        with open(full_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Strip legacy hover CSS rules if present
        for old_style in soup.find_all("style"):
            if "hover-yellow" in old_style.text or "custom-theme-fixes" in old_style.get("id", ""):
                old_style.decompose()

        if soup.head:
            soup.head.append(BeautifulSoup(nav_style, "html.parser"))

        container = soup.find("div", class_="container")
        if container:
            container["data-pagefind-body"] = "true"

        for old_nav in soup.find_all("nav", class_="page-nav"):
            old_nav.decompose()
        for old_footer in soup.find_all("footer", class_="doc-footer"):
            old_footer.decompose()

        if container:
            h1 = container.find("h1")
            if h1:
                h1.insert_after(BeautifulSoup(nav_bar, "html.parser"))
                h1.string = f"Canto {int(canto)} - Chapter {ch_num}: {title_text}"
            else:
                container.insert(0, BeautifulSoup(nav_bar, "html.parser"))

            container.append(BeautifulSoup(nav_bar, "html.parser"))
            container.append(BeautifulSoup(FOOTER_HTML, "html.parser"))

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(str(soup))


def generate_index_html(canto_data, existing_cantos):
    """Generates master index.html with multiline wrapping for mobile chapter titles."""
    cantos_html = ""

    for canto_num in sorted(canto_data.keys()):
        if canto_num not in existing_cantos:
            continue

        info = canto_data[canto_num]
        canto_title = info["title"]
        chapters = info["chapters"]

        ch_links = ""
        for ch in chapters:
            ch_num = ch["num"]
            ch_title = ch["title"]
            file_path = f"{canto_num}/mahatmya_ch{ch_num:02d}.html"

            if os.path.exists(
                os.path.join(HTML_DIR, canto_num, f"mahatmya_ch{ch_num:02d}.html")
            ):
                ch_links += f"""
                <li>
                    <a href="{file_path}">
                        <span class="ch-badge">Ch {ch_num}</span>
                        <span class="ch-title">{ch_title}</span>
                    </a>
                </li>"""

        is_open = "open" if canto_num == "00" else ""

        cantos_html += f"""
        <details class="canto-card" {is_open}>
            <summary>
                <h2>{canto_title}</h2>
                <span class="ch-count">{len(chapters)} Chapters</span>
            </summary>
            <ul class="chapter-list">
                {ch_links}
            </ul>
        </details>
        """

    index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Śrīmad Bhāgavata Purāṇa - Table of Contents</title>
    <!-- Pagefind Search Integration -->
    <link href="/pagefind/pagefind-ui.css" rel="stylesheet">
    <script src="/pagefind/pagefind-ui.js"></script>
    <style>
        :root {{
            --primary-color: #701c1c;
            --secondary-color: #8b2525;
            --bg-light: #fdfbf7;
            --card-bg: #ffffff;
            --text-dark: #2c2c2c;
            --border-color: #e2d9d0;
            --hover-bg: #e8f5e9;
        }}

        * {{
            box-sizing: border-box !important;
        }}

        body {{
            font-family: 'Georgia', serif;
            background-color: var(--bg-light);
            color: var(--text-dark);
            margin: 0;
            padding: 12px;
            line-height: 1.6;
            overflow-x: hidden;
        }}

        .main-container {{
            max-width: 1100px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 30px 16px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid var(--border-color);
        }}

        h1 {{
            color: var(--primary-color);
            text-align: center;
            font-size: 2em;
            margin-bottom: 5px;
        }}

        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 25px;
            font-style: italic;
            font-size: 0.95em;
        }}

        #search-box {{
            margin-bottom: 25px;
            padding: 12px;
            background: #fdfbf7;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }}

        .controls-bar {{
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-bottom: 15px;
        }}

        .btn-toggle {{
            background: #f4efe6;
            border: 1px solid var(--border-color);
            color: var(--primary-color);
            padding: 6px 14px;
            font-size: 0.85em;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }}

        .btn-toggle:hover {{
            background: var(--hover-bg);
            border-color: #2e7d32;
        }}

        .canto-card {{
            margin-bottom: 15px;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            background: #fff;
            overflow: hidden;
        }}

        summary {{
            list-style: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 16px;
            background: #faf6f0;
            cursor: pointer;
            user-select: none;
        }}

        summary::-webkit-details-marker {{
            display: none;
        }}

        summary h2 {{
            color: var(--secondary-color);
            margin: 0;
            font-size: 1.15em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        summary h2::before {{
            content: '▶';
            font-size: 0.75em;
            color: var(--primary-color);
            transition: transform 0.2s ease;
        }}

        .canto-card[open] summary h2::before {{
            transform: rotate(90deg);
        }}

        .ch-count {{
            font-size: 0.8em;
            color: #777;
            font-style: italic;
        }}

        .chapter-list {{
            list-style: none;
            padding: 12px;
            margin: 0;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 10px;
        }}

        .chapter-list li a {{
            display: flex;
            align-items: flex-start;
            padding: 10px 12px;
            text-decoration: none;
            color: var(--text-dark);
            border: 1px solid var(--border-color);
            border-radius: 5px;
            transition: all 0.2s ease;
            background: #fff;
        }}

        .chapter-list li a:hover {{
            background-color: var(--hover-bg);
            border-color: #2e7d32;
        }}

        .ch-badge {{
            background: var(--primary-color);
            color: white;
            font-size: 0.75em;
            font-weight: bold;
            padding: 3px 6px;
            border-radius: 4px;
            margin-right: 10px;
            white-space: nowrap;
            margin-top: 2px;
        }}

        .ch-title {{
            font-size: 0.9em;
            white-space: normal !important;
            word-break: break-word !important;
            flex: 1;
            line-height: 1.4;
        }}
    </style>
</head>
<body>

<div class="main-container">
    <h1>Śrīmad Bhāgavata Purāṇa</h1>
    <div class="subtitle">Complete Parallel Sanskrit & English Translation</div>

    <!-- Search Input Area -->
    <div id="search-box"></div>

    <!-- Expand/Collapse All Buttons -->
    <div class="controls-bar">
        <button class="btn-toggle" onclick="toggleAll(true)">Expand All</button>
        <button class="btn-toggle" onclick="toggleAll(false)">Collapse All</button>
    </div>

    <!-- Table of Contents -->
    <div id="toc">
        {cantos_html}
    </div>

    {FOOTER_HTML}
</div>

<script>
    window.addEventListener('DOMContentLoaded', (event) => {{
        new PagefindUI({{ element: "#search-box", showSubResults: true }});
    }});

    function toggleAll(openState) {{
        document.querySelectorAll('details.canto-card').forEach(el => {{
            el.open = openState;
        }});
    }}
</script>

</body>
</html>
"""
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(index_content)
    print("Generated master 'index.html' with green hover.")


if __name__ == "__main__":
    canto_data, chapter_titles = parse_toc()
    all_files = get_all_html_files()
    existing_cantos = set(item["canto"] for item in all_files)
    inject_nav_and_pagefind(all_files, chapter_titles)
    generate_index_html(canto_data, existing_cantos)