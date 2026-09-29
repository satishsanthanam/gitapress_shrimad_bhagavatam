import json
import os
import re
import markdown

def convert_md_to_html(md_text):
    if not md_text:
        return ""
    
    # Pre-process single '#' speaker headers to '###' so they render as h3 instead of h1
    md_text = re.sub(r"^#\s+(.*?)$", r"### \1", md_text, flags=re.MULTILINE)
    
    # 'nl2br' preserves verse line breaks
    html_out = markdown.markdown(md_text, extensions=['nl2br', 'sane_lists'])
    return html_out

def render_chapter_html(ch_num, json_file, output_html_file):
    if not os.path.exists(json_file):
        print(f"Skipping Ch {ch_num}: {json_file} not found.")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        verses = json.load(f)

    # Convert Roman numeral for title display
    roman_map = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}
    r_num = roman_map.get(ch_num, str(ch_num))

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Śrīmad Bhāgavata Māhātmya - Discourse {r_num}</title>
    <style>
        :root {{
            --primary-color: #701c1c;
            --secondary-color: #8b2525;
            --bg-light: #fdfbf7;
            --card-bg: #ffffff;
            --text-dark: #2c2c2c;
            --border-color: #e2d9d0;
            --verse-bg: #faf6f0;
            --hover-yellow: #fffde7;
        }}

        body {{
            font-family: 'Georgia', 'Noto Serif Devanagari', serif;
            background-color: var(--bg-light);
            color: var(--text-dark);
            margin: 0;
            padding: 20px;
            line-height: 1.8;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid var(--border-color);
        }}

        h1 {{
            color: var(--primary-color);
            text-align: center;
            font-size: 2.2em;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 10px;
            margin-top: 0;
        }}

        .parallel-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        .parallel-table th {{
            background-color: var(--primary-color);
            color: #ffffff;
            font-size: 1.1em;
            padding: 12px;
            text-align: left;
        }}

        .parallel-table td {{
            padding: 16px;
            border-bottom: 1px solid var(--border-color);
            vertical-align: top;
        }}

        .parallel-table tr {{
            transition: background-color 0.2s ease-in-out;
        }}

        .parallel-table tr:nth-child(even) {{
            background-color: var(--verse-bg);
        }}

        /* Yellow Hover Highlight */
        .parallel-table tbody tr:hover {{
            background-color: var(--hover-yellow) !important;
        }}

        .sanskrit-col {{
            width: 45%;
            font-family: 'Noto Sans Devanagari', 'Mangal', serif;
            font-size: 1.1em;
            color: #1a1a1a;
            border-right: 1px dashed var(--border-color);
        }}

        .english-col {{
            width: 55%;
            font-size: 1em;
            color: var(--text-dark);
        }}

        /* Speaker Headers & Titles */
        .sanskrit-col h2, .sanskrit-col h3, .sanskrit-col h4,
        .english-col h2, .english-col h3, .english-col h4 {{
            color: var(--secondary-color);
            margin-top: 0;
            margin-bottom: 6px;
            font-weight: bold;
            font-style: italic;
        }}

        .sanskrit-col h2, .english-col h2 {{
            font-size: 1.3em;
            border-left: 4px solid var(--primary-color);
            padding-left: 8px;
            background: var(--verse-bg);
            padding-top: 4px;
            padding-bottom: 4px;
            border-radius: 4px;
        }}

        .sanskrit-col h3, .sanskrit-col h4, .english-col h3, .english-col h4 {{
            font-size: 1.05em;
        }}

        .sanskrit-col p, .english-col p {{
            margin: 0 0 8px 0;
            padding: 0;
            display: inline-block;
            width: 100%;
        }}

        .verse-num {{
            font-weight: bold;
            color: var(--primary-color);
            margin-left: 6px;
        }}

        @media (max-width: 768px) {{
            .parallel-table, .parallel-table tbody, .parallel-table tr, .parallel-table td {{
                display: block;
                width: 100%;
            }}
            .sanskrit-col {{
                border-right: none;
                border-bottom: 1px dashed var(--border-color);
                width: 100%;
            }}
            .english-col {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>

<div class="container">
    <h1>Śrīmad Bhāgavata Māhātmya - Discourse {r_num}</h1>

    <table class="parallel-table">
        <thead>
            <tr>
                <th class="sanskrit-col">Sanskrit (संस्कृतम्)</th>
                <th class="english-col">English Translation</th>
            </tr>
        </thead>
        <tbody>
"""

    for entry in verses:
        san_html = convert_md_to_html(entry.get("sanskrit", ""))
        eng_html = convert_md_to_html(entry.get("english", ""))
        v_range = entry.get("verse_range", "")

        html_content += f"""            <tr>
                <td class="sanskrit-col">
                    {san_html}
                </td>
                <td class="english-col">
                    {eng_html} <span class="verse-num">({v_range})</span>
                </td>
            </tr>
"""

    html_content += """        </tbody>
    </table>
</div>

</body>
</html>
"""

    with open(output_html_file, "w", encoding="utf-8") as out:
        out.write(html_content)

    print(f"✅ Generated: '{output_html_file}'")

def build_all():
    os.makedirs("html_out", exist_ok=True)
    for ch in range(1, 20):
        json_path = f"mahatmya_json/mahatmya_ch{ch:02d}.json"
        html_path = f"html_out/mahatmya_ch{ch:02d}.html"
        render_chapter_html(ch, json_path, html_path)

if __name__ == "__main__":
    build_all()