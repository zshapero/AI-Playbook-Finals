#!/usr/bin/env python3
"""Generate individual chapter PDFs and a full combined playbook PDF.

Uses Playwright (headless Chromium) for faithful browser-quality rendering.
"""

import os
import re
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = "/home/user/AI-Playbook-Finals"
OUTPUT_DIR = os.path.join(BASE_DIR, "pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Chapter metadata: (filename, chapter_num, module_num, title)
CHAPTERS = [
    ("Chapter 1", 1, 1, "Making AI Simple and Approachable"),
    ("Chapter 2", 2, 1, "Three Initial AI Decisions That Will Set Your Course"),
    ("Chapter 3", 3, 1, "Education & Enablement"),
    ("Chapter 4", 4, 1, "Change Management"),
    ("Chapter 5", 5, 1, "Activate Your AI Leadership Team"),
    ("Chapter 6", 6, 2, "AI is Really a Change Initiative"),
    ("Chapter 7", 7, 2, "The Agent Workforce Journey"),
    ("Chapter_8.html", 8, 2, "Where to Start with the Calix Agentic Workforce"),
    ("Chapter 9", 9, 3, "Go Slow to Go Fast"),
    ("Chapter 10", 10, 3, "AI Governance Goes Mainstream"),
    ("Chapter 11", 11, 3, "Organizational Readiness and the Path Forward"),
]

MODULE_INTROS = [
    ("Module 1 Intro", 1, "Understanding AI and Why It Matters"),
    ("Module 2 Intro", 2, "Get Started with Calix Agent Workforce"),
    ("Module 3 Intro", 3, "Scaling AI Responsibly"),
]

SUPPLEMENTARY = [
    ("AI Ready Leader Strengths & Opportunities Finder", "AI Ready Leader Strengths & Opportunities Finder"),
    ("Thank You For Exploring This Playbook", "Thank You For Exploring This Playbook"),
]

# Viewport width for rendering — matches the site's content column so the page
# looks like the website viewed in a browser window at this width.
VIEWPORT_WIDTH = 1400
VIEWPORT_HEIGHT = 900

# Scale factor for PDF output.
PDF_SCALE = 0.55

# Minimal CSS injected to hide non-print elements and let the existing
# responsive styles handle layout.
PRINT_CSS = """
<style id="print-override">
/* Hide interactive / sidebar elements */
.resource-sidebar { display: none !important; }
.takeaway-download { display: none !important; }
.download-instructions { display: none !important; }
.video-modal-overlay { display: none !important; }

/* Ensure images fit within the page */
img {
    max-width: 100% !important;
    height: auto !important;
}

/* Keep logo at its intended size */
.logo-img {
    height: 48px !important;
    width: auto !important;
}
.intro-content > img:first-child {
    height: 48px !important;
    width: auto !important;
}
</style>
"""


def inject_print_css(html_content):
    """Inject print-friendly CSS and strip external scripts that block loading."""
    # Remove external script tags (CDN loads that timeout in headless mode)
    html_content = re.sub(r'<script\s+src="https?://[^"]*"[^>]*></script>', '', html_content)
    # Insert right before </head>
    if "</head>" in html_content:
        return html_content.replace("</head>", PRINT_CSS + "\n</head>")
    # Fallback: insert at the beginning
    return PRINT_CSS + html_content


def html_to_pdf_playwright(page, filepath, output_path):
    """Convert an HTML file to PDF using Playwright's Chromium renderer."""
    with open(filepath, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Inject print CSS
    modified_html = inject_print_css(html_content)

    # Write to a temp file so Chromium can load it with file:// protocol
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(modified_html)
        tmp_path = tmp.name

    try:
        page.set_viewport_size({"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT})
        page.goto(f"file://{tmp_path}", wait_until="domcontentloaded", timeout=60000)
        # Let fonts and images fully render
        page.wait_for_timeout(3000)

        page.pdf(
            path=output_path,
            format="Letter",
            margin={"top": "0.4in", "bottom": "0.5in", "left": "0.4in", "right": "0.4in"},
            print_background=True,
            prefer_css_page_size=False,
            scale=PDF_SCALE,
        )
    finally:
        os.unlink(tmp_path)


def generate_individual_pdfs(browser):
    """Generate one PDF per chapter, module intro, and supplementary file."""
    page = browser.new_page(viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT})

    all_files = []

    # Chapters
    for filename, ch_num, mod_num, title in CHAPTERS:
        safe_title = title.replace(' ', '_').replace('&', 'and').replace('—', '-')
        output_name = f"Chapter_{ch_num}_{safe_title}.pdf"
        all_files.append((filename, output_name))

    # Module intros
    for filename, mod_num, title in MODULE_INTROS:
        safe_title = title.replace(' ', '_').replace('&', 'and')
        output_name = f"Module_{mod_num}_Intro_{safe_title}.pdf"
        all_files.append((filename, output_name))

    # Supplementary
    for filename, title in SUPPLEMENTARY:
        safe_title = title.replace(' ', '_').replace('&', 'and')
        output_name = f"{safe_title}.pdf"
        all_files.append((filename, output_name))

    for filename, output_name in all_files:
        filepath = os.path.join(BASE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  SKIP: {filename} not found")
            continue

        output_path = os.path.join(OUTPUT_DIR, output_name)
        print(f"  Generating: {output_name}")
        try:
            html_to_pdf_playwright(page, filepath, output_path)
            print(f"  Done: {output_path}")
        except Exception as e:
            print(f"  ERROR generating {output_name}: {e}")
            # Re-create the page in case it's in a bad state
            page.close()
            page = browser.new_page(viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT})

    page.close()


def generate_cover_and_toc(browser):
    """Generate cover page and TOC as a PDF."""
    toc_items = []
    for mod_filename, mod_num, mod_title in MODULE_INTROS:
        toc_items.append(f'<li class="toc-module">Module {mod_num}: {mod_title}</li>')
        for filename, ch_num, mod, title in CHAPTERS:
            if mod == mod_num:
                toc_items.append(f'<li class="toc-chapter">Chapter {ch_num}: {title}</li>')

    for filename, title in SUPPLEMENTARY:
        toc_items.append(f'<li class="toc-supplementary">{title}</li>')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ font-family: 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif; color: #333; }}

        .cover-page {{
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            page-break-after: always;
            position: relative;
        }}
        .cover-bar {{
            position: absolute; top: 0; left: 0; right: 0;
            height: 8px; background: #0B38DB;
        }}
        .cover-title {{
            font-size: 52px; font-weight: 800; color: #0B38DB;
            line-height: 1.15; margin-bottom: 24px;
        }}
        .cover-divider {{
            width: 220px; height: 4px; background: #FF7600;
            margin: 24px auto;
        }}
        .cover-subtitle {{
            font-size: 22px; font-weight: 700; color: #FF7600;
            margin-bottom: 28px;
        }}
        .cover-desc {{
            font-size: 15px; color: #555; line-height: 1.8;
            margin-bottom: 80px;
        }}
        .cover-company {{
            font-size: 26px; font-weight: 800; color: #FF7600;
        }}

        .toc-page {{
            padding: 60px 80px;
        }}
        .toc-title {{
            font-size: 32px; font-weight: 800; color: #0B38DB;
            margin-bottom: 8px;
        }}
        .toc-divider {{
            width: 300px; height: 3px; background: #FF7600;
            margin: 16px 0 32px 0;
        }}
        .toc-list {{ list-style: none; padding: 0; }}
        .toc-module {{
            font-size: 17px; font-weight: 700; color: #0B38DB;
            margin-top: 20px; padding: 10px 0;
            border-bottom: 2px solid #eee;
        }}
        .toc-chapter {{
            font-size: 14px; color: #333; padding: 8px 0 8px 28px;
            border-bottom: 1px solid #f5f5f5;
        }}
        .toc-supplementary {{
            font-size: 14px; color: #555; padding: 8px 0;
            margin-top: 16px; border-bottom: 1px solid #eee;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="cover-page">
        <div class="cover-bar"></div>
        <h1 class="cover-title">AI LEADERSHIP<br>PLAYBOOK</h1>
        <div class="cover-divider"></div>
        <p class="cover-subtitle">The Complete Guide</p>
        <p class="cover-desc">A comprehensive guide for broadband leaders<br>to understand, adopt, and leverage AI</p>
        <p class="cover-company">CALIX INC</p>
    </div>
    <div class="toc-page">
        <h1 class="toc-title">Table of Contents</h1>
        <div class="toc-divider"></div>
        <ul class="toc-list">
            {''.join(toc_items)}
        </ul>
    </div>
</body>
</html>"""

    cover_path = os.path.join(OUTPUT_DIR, "_cover_toc.pdf")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(html)
        tmp_path = tmp.name

    try:
        page = browser.new_page()
        page.goto(f"file://{tmp_path}", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(500)
        page.pdf(
            path=cover_path,
            format="Letter",
            margin={"top": "0in", "bottom": "0in", "left": "0in", "right": "0in"},
            print_background=True,
        )
        page.close()
    finally:
        os.unlink(tmp_path)

    return cover_path


def generate_full_playbook(browser):
    """Generate the combined full playbook PDF by merging individual chapter PDFs."""
    from PyPDF2 import PdfMerger

    output_path = os.path.join(OUTPUT_DIR, "Full_AI_Leadership_Playbook.pdf")
    print("  Generating cover page and TOC...")
    cover_path = generate_cover_and_toc(browser)

    merger = PdfMerger()

    # Add cover + TOC
    merger.append(cover_path)

    # Add module intros and chapters in order
    module_chapters = {1: [], 2: [], 3: []}
    for filename, ch_num, mod_num, title in CHAPTERS:
        module_chapters[mod_num].append((filename, ch_num, title))

    for mod_filename, mod_num, mod_title in MODULE_INTROS:
        # Add module intro PDF
        safe_title = mod_title.replace(' ', '_').replace('&', 'and')
        intro_pdf = os.path.join(OUTPUT_DIR, f"Module_{mod_num}_Intro_{safe_title}.pdf")
        if os.path.exists(intro_pdf):
            print(f"  Adding: Module {mod_num} Intro")
            merger.append(intro_pdf)

        # Add chapter PDFs in this module
        for filename, ch_num, title in module_chapters.get(mod_num, []):
            safe_title = title.replace(' ', '_').replace('&', 'and').replace('—', '-')
            ch_pdf = os.path.join(OUTPUT_DIR, f"Chapter_{ch_num}_{safe_title}.pdf")
            if os.path.exists(ch_pdf):
                print(f"  Adding: Chapter {ch_num}")
                merger.append(ch_pdf)

    # Add supplementary
    for filename, title in SUPPLEMENTARY:
        safe_title = title.replace(' ', '_').replace('&', 'and')
        supp_pdf = os.path.join(OUTPUT_DIR, f"{safe_title}.pdf")
        if os.path.exists(supp_pdf):
            print(f"  Adding: {title}")
            merger.append(supp_pdf)

    merger.write(output_path)
    merger.close()

    # Clean up temp cover PDF
    os.unlink(cover_path)

    print(f"  Done: {output_path}")


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome"
        )

        print("=== Generating Individual Chapter PDFs ===")
        generate_individual_pdfs(browser)

        print("\n=== Generating Full Combined Playbook PDF ===")
        generate_full_playbook(browser)

        browser.close()

    print("\n=== All PDFs generated! ===")
    print(f"Output directory: {OUTPUT_DIR}")
