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

# Scale factor for PDF output.  The site's fonts are designed for a 2050px
# display.  At 1400px viewport the responsive breakpoint (≤1800px) is active
# giving a fluid layout.  Scaling to ~0.55 maps that onto Letter paper width
# (≈758px usable at 96 dpi) so text looks natural — roughly 13px effective
# body font, which reads like a normal printed document.
PDF_SCALE = 0.55

# Minimal CSS injected to hide non-print elements and let the existing
# responsive styles handle layout.  We do NOT override widths or font sizes —
# the scale parameter handles fitting to paper.
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
    """Convert an HTML file to PDF using Playwright's Chromium renderer.

    The page is rendered at VIEWPORT_WIDTH so the site's responsive CSS kicks
    in, then scaled down via PDF_SCALE to fit naturally on Letter paper — like
    viewing the website in a browser window resized to paper dimensions.
    """
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


def _unused_build_full_playbook_html():
    """Build a single HTML document combining all chapters in the full playbook style."""

    # Collect all sections in order
    sections = []
    module_chapters = {1: [], 2: [], 3: []}
    for filename, ch_num, mod_num, title in CHAPTERS:
        module_chapters[mod_num].append((filename, ch_num, title))

    for mod_filename, mod_num, mod_title in MODULE_INTROS:
        mod_path = os.path.join(BASE_DIR, mod_filename)
        if os.path.exists(mod_path):
            content = extract_body_content(mod_path)
            if content:
                sections.append(('module_intro', mod_num, mod_title, content))

        for filename, ch_num, title in module_chapters.get(mod_num, []):
            filepath = os.path.join(BASE_DIR, filename)
            if os.path.exists(filepath):
                content = extract_body_content(filepath)
                if content:
                    sections.append(('chapter', ch_num, title, content))

    for filename, title in SUPPLEMENTARY:
        filepath = os.path.join(BASE_DIR, filename)
        if os.path.exists(filepath):
            content = extract_body_content(filepath)
            if content:
                sections.append(('supplementary', 0, title, content))

    # Collect all unique styles from HTML files to preserve original styling
    all_styles = set()
    for filename, _, _, _ in CHAPTERS:
        filepath = os.path.join(BASE_DIR, filename)
        if os.path.exists(filepath):
            style = extract_style_block(filepath)
            if style:
                all_styles.add(style)
                break  # They all share similar styles, just need one

    # Build body parts
    body_parts = []

    # Cover page
    body_parts.append("""
    <div class="cover-page">
        <div class="cover-top-bar"></div>
        <div class="cover-content">
            <h1 class="cover-title">AI LEADERSHIP<br>PLAYBOOK</h1>
            <div class="cover-divider"></div>
            <p class="cover-subtitle">The Complete Guide</p>
            <p class="cover-description">A comprehensive guide for broadband leaders<br>to understand, adopt, and leverage AI</p>
            <p class="cover-company">CALIX INC</p>
        </div>
    </div>
    """)

    # Table of Contents
    toc_items = []
    for section_type, num, title, _ in sections:
        if section_type == 'module_intro':
            toc_items.append(f'<li class="toc-module">Module {num}: {title}</li>')
        elif section_type == 'chapter':
            toc_items.append(f'<li class="toc-chapter">Chapter {num}: {title}</li>')
        elif section_type == 'supplementary':
            toc_items.append(f'<li class="toc-supplementary">{title}</li>')

    body_parts.append(f"""
    <div class="toc-page">
        <h1 class="playbook-section-title">Table of Contents</h1>
        <div class="playbook-title-divider"></div>
        <ul class="toc-list">
            {''.join(toc_items)}
        </ul>
    </div>
    """)

    # Content sections
    for section_type, num, title, content in sections:
        if section_type == 'module_intro':
            header = f'<p class="playbook-pillar-ref">Module {num}</p>'
        elif section_type == 'chapter':
            header = f'<p class="playbook-pillar-ref">Chapter {num}</p>'
        else:
            header = ''

        body_parts.append(f"""
        <div class="playbook-content-section">
            <div class="playbook-page-top-bar"></div>
            {header}
            <h1 class="playbook-section-title">{title}</h1>
            <div class="playbook-title-divider"></div>
            <div class="chapter-body">
                {content}
            </div>
        </div>
        """)

    # Use the first chapter's styles as base, plus playbook overrides
    base_style = list(all_styles)[0] if all_styles else ""

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
    <style>
        /* Base chapter styles (for reused content blocks) */
        {base_style}

        /* === PLAYBOOK OVERRIDES === */
        html, body {{
            width: 100% !important;
            max-width: 100% !important;
            font-family: 'Open Sans', sans-serif;
            font-size: 11px;
            line-height: 1.6;
            color: #333;
        }}

        .page-wrapper {{
            display: none !important;
        }}

        /* Cover page */
        .cover-page {{
            page-break-after: always;
            text-align: center;
            padding-top: 60px;
        }}

        .cover-top-bar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 8px;
            background: #0B38DB;
        }}

        .cover-content {{
            margin-top: 140px;
        }}

        .cover-title {{
            font-family: 'Open Sans', sans-serif !important;
            font-size: 48px !important;
            font-weight: 800 !important;
            color: #0B38DB !important;
            line-height: 1.2 !important;
            margin-bottom: 30px !important;
            background: none !important;
            padding: 0 !important;
            display: block !important;
        }}

        .cover-divider {{
            width: 200px;
            height: 4px;
            background: #FF7600;
            margin: 30px auto;
        }}

        .cover-subtitle {{
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #FF7600 !important;
            margin-bottom: 30px !important;
        }}

        .cover-description {{
            font-size: 14px !important;
            color: #555 !important;
            line-height: 1.8 !important;
            margin-bottom: 80px !important;
        }}

        .cover-company {{
            font-size: 24px !important;
            font-weight: 800 !important;
            color: #FF7600 !important;
            margin-top: 60px !important;
        }}

        /* TOC */
        .toc-page {{
            page-break-after: always;
            padding-top: 20px;
        }}

        .toc-list {{
            list-style: none;
            padding: 0;
        }}

        .toc-module {{
            font-size: 16px;
            font-weight: 700;
            color: #0B38DB;
            margin-top: 18px;
            margin-bottom: 4px;
            padding: 8px 0;
            border-bottom: 2px solid #eee;
        }}

        .toc-chapter {{
            font-size: 13px;
            color: #333;
            padding: 6px 0 6px 24px;
            border-bottom: 1px solid #f5f5f5;
        }}

        .toc-supplementary {{
            font-size: 13px;
            color: #555;
            padding: 6px 0;
            margin-top: 14px;
            border-bottom: 1px solid #eee;
            font-style: italic;
        }}

        /* Page top bar */
        .playbook-page-top-bar {{
            height: 6px;
            background: #0B38DB;
            margin: 0 -50px 20px -50px;
        }}

        /* Playbook section titles */
        .playbook-pillar-ref {{
            font-size: 12px !important;
            font-weight: 600 !important;
            color: #888 !important;
            margin-bottom: 4px !important;
        }}

        .playbook-section-title {{
            font-family: 'Open Sans', sans-serif !important;
            font-size: 28px !important;
            font-weight: 800 !important;
            color: #0B38DB !important;
            line-height: 1.25 !important;
            margin-bottom: 12px !important;
            background: none !important;
            padding: 0 !important;
            display: block !important;
        }}

        .playbook-title-divider {{
            width: 60%;
            max-width: 400px;
            height: 3px;
            background: #FF7600;
            margin: 16px 0 24px 0;
        }}

        /* Content sections */
        .playbook-content-section {{
            page-break-before: always;
            padding: 0 50px;
        }}

        /* Override chapter body elements */
        .chapter-body {{
            font-size: 11px;
            line-height: 1.65;
        }}

        .chapter-body .pillar-label,
        .chapter-body .chapter-label {{
            display: none !important;
        }}

        .chapter-body .intro-image {{
            display: none !important;
        }}

        .chapter-body h1 {{
            display: none !important;
        }}

        .chapter-body h2 {{
            font-family: 'Open Sans', sans-serif !important;
            font-size: 22px !important;
            font-weight: 800 !important;
            color: #0B38DB !important;
            margin-top: 24px !important;
            margin-bottom: 12px !important;
        }}

        .chapter-body h3 {{
            font-size: 16px !important;
            margin-top: 18px !important;
            margin-bottom: 8px !important;
        }}

        .chapter-body p {{
            font-size: 11px !important;
            margin-bottom: 10px !important;
            text-align: justify !important;
        }}

        .chapter-body .intro-text {{
            font-style: italic !important;
            text-align: left !important;
        }}

        .chapter-body ul, .chapter-body ol {{
            margin: 8px 0 12px 24px !important;
        }}

        .chapter-body li {{
            font-size: 11px !important;
            margin-bottom: 5px !important;
        }}

        .chapter-body img {{
            max-width: 100% !important;
            height: auto !important;
        }}

        .chapter-body table {{
            width: 100% !important;
            border-collapse: collapse !important;
            font-size: 10px !important;
            margin: 12px 0 !important;
        }}

        .chapter-body th {{
            background: #0B38DB !important;
            color: #fff !important;
            padding: 8px 10px !important;
            text-align: left !important;
        }}

        .chapter-body td {{
            padding: 8px 10px !important;
            border-bottom: 1px solid #e0e0e0 !important;
        }}

        /* Takeaway box in playbook style */
        .chapter-body .takeaways-box {{
            background: #0B38DB !important;
            color: #fff !important;
            padding: 20px 24px !important;
            margin: 28px 0 16px !important;
            border-radius: 6px !important;
        }}

        .chapter-body .takeaways-box h2 {{
            color: #fff !important;
            display: block !important;
            font-size: 18px !important;
        }}

        .chapter-body .takeaways-box p {{
            color: #fff !important;
        }}

        .chapter-body .takeaway-download {{
            display: none !important;
        }}

        /* Learning box */
        .chapter-body .learning-box {{
            background: #f8f9fc !important;
            border-left: 4px solid #0B38DB !important;
            padding: 14px 18px !important;
            margin: 16px 0 !important;
        }}

        /* Myth blocks */
        .chapter-body .myth-block {{
            padding: 12px 16px !important;
            margin: 10px 0 !important;
        }}

        .chapter-body .myth-label {{
            font-size: 12px !important;
        }}

        /* AI types */
        .chapter-body .ai-type-label {{
            font-size: 12px !important;
        }}

        .chapter-body .ai-type-image {{
            height: auto !important;
            max-height: 200px !important;
        }}

        /* Cards */
        .chapter-body .cards-grid,
        .chapter-body .role-cards {{
            display: block !important;
        }}

        /* Hide sidebar/download elements */
        .resource-sidebar {{
            display: none !important;
        }}

        .download-instructions {{
            display: none !important;
        }}

        .video-modal-overlay {{
            display: none !important;
        }}
    </style>
</head>
<body>
    {''.join(body_parts)}
</body>
</html>"""

    return full_html


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
    # Build TOC items
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
    from pypdf import PdfWriter

    output_path = os.path.join(OUTPUT_DIR, "Full_AI_Leadership_Playbook.pdf")
    print("  Generating cover page and TOC...")
    cover_path = generate_cover_and_toc(browser)

    writer = PdfWriter()

    # Add cover + TOC
    writer.append(cover_path)

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
            writer.append(intro_pdf)

        # Add chapter PDFs in this module
        for filename, ch_num, title in module_chapters.get(mod_num, []):
            safe_title = title.replace(' ', '_').replace('&', 'and').replace('—', '-')
            ch_pdf = os.path.join(OUTPUT_DIR, f"Chapter_{ch_num}_{safe_title}.pdf")
            if os.path.exists(ch_pdf):
                print(f"  Adding: Chapter {ch_num}")
                writer.append(ch_pdf)

    # Add supplementary
    for filename, title in SUPPLEMENTARY:
        safe_title = title.replace(' ', '_').replace('&', 'and')
        supp_pdf = os.path.join(OUTPUT_DIR, f"{safe_title}.pdf")
        if os.path.exists(supp_pdf):
            print(f"  Adding: {title}")
            writer.append(supp_pdf)

    writer.write(output_path)
    writer.close()

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
