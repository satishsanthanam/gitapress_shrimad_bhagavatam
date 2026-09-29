# Śrīmad Bhāgavata Mahapurāṇa by Shri Maharishi Vedavyasa | Language: English | Code: 564 & Code: 565 (Gita Press version Digital Edition)

A high-performance, responsive static web publication and search platform for the complete **Śrīmad Bhāgavata Purāṇa (Mahāpurāṇa)** across all 12 Skandhas (Books) and the Māhātmya. The portal provides parallel Sanskrit Devanagari text alongside English translations published by Gita Press (Gorakhpur), dynamic chapter index navigation, collapsible Canto cards, and client-side static site search.

🔗 **Live Application**: [https://gitapress-shrimad-bhagavatam.pages.dev/](https://gitapress-shrimad-bhagavatam.pages.dev/)

📂 **Deployment & CDN**: Hosted on Cloudflare Pages with automated Git CI/CD static builds.

---

## Features

* **Complete 12 Skandhas & Māhātmya Coverage**: Full digital scripture portal spanning Book 0 (Māhātmya) through Book 12 formatted into clean, verse-mapped HTML pages.
* **AI-Powered OCR & Pipeline**: Processed from source PDF archives using **Mistral AI PDF OCR** for high-accuracy Devanagari Sanskrit and English text extraction, structured using automated Python scripts.
* **Collapsible Accordion Table of Contents**: Interactive master index (`index.html`) featuring native `<details>` and `<summary>` Canto cards with quick Expand All / Collapse All controls.
* **Chapter Navigation & Home Link**: Automated top and bottom navigation bars on every chapter page providing **← Previous Chapter**, **📜 Table of Contents**, and **Next Chapter →** links.
* **Static Client-Side Search**: Embedded **Pagefind** static search engine enabling instant full-text query searches across Sanskrit and English text without requiring a backend server.
* **Responsive & Mobile-First UI**: Styled using warm, traditional typography and clean layout design optimized across desktop, tablet, and mobile browsers.

---

## Repository & Project Structure

```text
.
├── build_site.py          # Master build pipeline script
├── html_out/              # Static deployment root directory
│   ├── index.html         # Master collapsible landing page
│   ├── toc.md             # Master Table of Contents definitions
│   ├── 00/                # Śrīmad Bhāgavata Māhātmya chapters
│   ├── 01/                # Book One HTML pages
│   ├── ...
│   └── 12/                # Book Twelve HTML pages
├── mahatmya_json/         # Raw JSON verse data per chapter
├── markdowns/             # Aligned source markdown files
└── ocr_txt/               # Source OCR text extracts

```

---

## Build Pipeline Architecture

The site build pipeline executes automatically via Cloudflare Pages on every push to `main`:

```
┌─────────────────────────┐
│ Source HTML & toc.md    │
└────────────┬────────────┘
             │
             ▼
   [1] build_site.py           --> Parses toc.md, injects nav bars, site footer,
             │                     Pagefind attributes, and generates html_out/index.html
             │
             ▼
   [2] Pagefind CLI            --> Generates static client search index inside html_out/pagefind
             │
             ▼
┌─────────────────────────┐
│ Cloudflare Pages Deploy │   --> Publishes contents of html_out/ to global edge CDN
└─────────────────────────┘

```

---

## Local Setup & Development

### Prerequisites

* Python 3.10+
* Beautiful Soup 4 (`pip install beautifulsoup4`)
* Pagefind CLI (`npm install -g pagefind` or `npx pagefind`)

### Running the Build Locally

1. **Clone the Repository**:
```bash
git clone [https://bitbucket.org/satishsanthanam/gitapress_bhagavatam.git](https://bitbucket.org/satishsanthanam/gitapress_bhagavatam.git)
cd gitapress_bhagavatam

```


2. **Execute Full Build Pipeline**:
```bash
python build_site.py

```


3. **Generate Search Index**:
```bash
npx pagefind --site html_out

```


4. **Preview Locally**:
```bash
cd html_out
python -m http.server 8000

```


Open `http://localhost:8000` in your browser.

---

## Primary Sources & Credits

* **Sanskrit Text & English Translation**: *Śrīmad Bhāgavata Mahāpurāṇa* (Parts 1 & 2) — Published by [Gita Press, Gorakhpur](https://gitapress.org).
* **PDF Processing & OCR**: [Mistral AI OCR](https://mistral.ai) — High-accuracy document parsing and text extraction from source PDF scans.
* **Developer & Maintainer**: [Satish Santhanam](https://ventpipe.blog) — Engineered dataset conversion scripts, site generator pipeline, and Cloudflare Pages CI/CD integration.
* **Publication Blog**: [ventpipe.blog](https://ventpipe.blog)
* **AI Collaboration**: Pair-programming collaboration with **Google Gemini AI** (build automation, script engineering, UI architecture) & **Mistral AI** (PDF OCR & text extraction).


## License & Dedication

**🙏 Shri Krishnarpanam Asthu 🙏**

Maintained as part of an open-access digital Sanskrit scripture preservation initiative. Free for non-commercial, educational, and research utilization.