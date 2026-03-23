#!/usr/bin/env python3
"""Generate individual chapter PDFs and a full combined playbook PDF."""

import os
import re
from weasyprint import HTML, CSS

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

# CSS override to adapt HTML files (designed for web at 2050px) to print PDF
CHAPTER_PDF_CSS = CSS(string="""
@page {
    size: letter;
    margin: 30px 40px 40px 40px;
}

* {
    box-sizing: border-box !important;
}

html, body {
    width: auto !important;
    max-width: 100% !important;
    font-size: 10px !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.6 !important;
}

.page-wrapper {
    width: auto !important;
    max-width: 100% !important;
    display: block !important;
}

.main-content {
    max-width: 100% !important;
    width: auto !important;
    padding: 0 !important;
}

/* Logo */
.logo-container {
    margin-bottom: 16px !important;
}

.logo-container img {
    width: 120px !important;
    height: auto !important;
}

/* Chapter header */
.pillar-label {
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    margin-bottom: 4px !important;
}

.chapter-label {
    font-size: 10px !important;
    padding: 3px 10px !important;
    margin-bottom: 8px !important;
}

h1 {
    font-size: 26px !important;
    margin-bottom: 12px !important;
    line-height: 1.2 !important;
}

/* Header section - fix the float layout */
.header-section {
    overflow: hidden !important;
    display: block !important;
    margin-bottom: 20px !important;
}

.intro-image {
    float: right !important;
    width: 80px !important;
    height: auto !important;
    margin: 0 0 10px 12px !important;
}

.intro-text {
    font-size: 10px !important;
    margin-bottom: 8px !important;
}

.chapter-description {
    font-size: 10px !important;
    padding-bottom: 14px !important;
}

/* Section headings */
h2 {
    font-size: 18px !important;
    margin-top: 22px !important;
    margin-bottom: 10px !important;
}

h3 {
    font-size: 14px !important;
    margin-top: 16px !important;
    margin-bottom: 8px !important;
}

h4 {
    font-size: 12px !important;
}

p {
    font-size: 10px !important;
    margin-bottom: 8px !important;
}

/* Learning box */
.learning-box {
    padding: 14px 16px !important;
    margin: 16px 0 !important;
}

.learning-box h3 {
    font-size: 14px !important;
    margin-bottom: 8px !important;
}

.learning-box li {
    font-size: 10px !important;
    margin-bottom: 4px !important;
}

/* Definition box */
.definition-box {
    padding: 14px 16px !important;
    margin: 14px 0 !important;
}

/* AI types */
.ai-type {
    margin-bottom: 12px !important;
}

.ai-type-content {
    padding-left: 12px !important;
}

.ai-type-label {
    font-size: 11px !important;
}

.ai-type-image {
    height: auto !important;
    max-height: 200px !important;
}

/* Myth blocks */
.myth-block {
    margin: 12px 0 !important;
    padding: 12px 16px !important;
}

.myth-label {
    font-size: 11px !important;
}

.reality-label {
    font-size: 11px !important;
}

/* Benefits list */
.benefits-list li {
    font-size: 10px !important;
    margin-bottom: 6px !important;
    padding-left: 18px !important;
}

/* Takeaway box */
.takeaways-box {
    padding: 16px 20px !important;
    margin: 20px 0 16px !important;
}

.takeaways-box h2 {
    font-size: 16px !important;
    margin-bottom: 8px !important;
}

.takeaways-box p {
    font-size: 10px !important;
}

/* Hide download buttons and sidebar */
.takeaway-download {
    display: none !important;
}

.download-instructions {
    display: none !important;
}

.resource-sidebar {
    display: none !important;
}

.video-modal-overlay {
    display: none !important;
}

/* Images */
img {
    max-width: 100% !important;
    height: auto !important;
}

/* Tables */
table {
    width: 100% !important;
    font-size: 9px !important;
    border-collapse: collapse !important;
}

th {
    padding: 6px 8px !important;
    font-size: 9px !important;
}

td {
    padding: 6px 8px !important;
    font-size: 9px !important;
}

/* Lists */
ul, ol {
    margin: 6px 0 10px 20px !important;
}

li {
    font-size: 10px !important;
    margin-bottom: 4px !important;
}

/* Cards and grids */
.cards-grid, .role-cards, .grid-container {
    display: block !important;
}

.card, .role-card, .grid-item {
    margin: 8px 0 !important;
    padding: 10px 14px !important;
}

/* Info boxes */
.info-box, .key-insight, .best-practice, .tip-box, .note-box {
    padding: 12px 16px !important;
    margin: 10px 0 !important;
}

/* Scenario / step boxes */
.journey-step, .step, .scenario-box, .phase-box {
    margin: 8px 0 !important;
    padding: 10px 14px !important;
}

/* Numbered sections */
.step-number, .phase-number {
    font-size: 12px !important;
}

/* Assessment sections */
.assessment-section, .quiz-section, .exercise-section {
    padding: 12px 16px !important;
    margin: 10px 0 !important;
}

/* Module labels in intros */
.module-title {
    font-size: 20px !important;
}

.module-label {
    font-size: 10px !important;
}
""")


def generate_individual_chapter_pdfs():
    """Generate one PDF per chapter from the HTML files."""
    for filename, ch_num, mod_num, title in CHAPTERS:
        filepath = os.path.join(BASE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  SKIP: {filename} not found")
            continue

        output_name = f"Chapter_{ch_num}_{title.replace(' ', '_').replace('&', 'and').replace('—', '-')}.pdf"
        output_path = os.path.join(OUTPUT_DIR, output_name)

        print(f"  Generating: {output_name}")
        html = HTML(filename=filepath)
        html.write_pdf(output_path, stylesheets=[CHAPTER_PDF_CSS])
        print(f"  Done: {output_path}")


def generate_module_intro_pdfs():
    """Generate one PDF per module intro."""
    for filename, mod_num, title in MODULE_INTROS:
        filepath = os.path.join(BASE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  SKIP: {filename} not found")
            continue

        output_name = f"Module_{mod_num}_Intro_{title.replace(' ', '_').replace('&', 'and')}.pdf"
        output_path = os.path.join(OUTPUT_DIR, output_name)

        print(f"  Generating: {output_name}")
        html = HTML(filename=filepath)
        html.write_pdf(output_path, stylesheets=[CHAPTER_PDF_CSS])
        print(f"  Done: {output_path}")


def generate_supplementary_pdfs():
    """Generate PDFs for supplementary content."""
    for filename, title in SUPPLEMENTARY:
        filepath = os.path.join(BASE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  SKIP: {filename} not found")
            continue

        output_name = f"{title.replace(' ', '_').replace('&', 'and')}.pdf"
        output_path = os.path.join(OUTPUT_DIR, output_name)

        print(f"  Generating: {output_name}")
        html = HTML(filename=filepath)
        html.write_pdf(output_path, stylesheets=[CHAPTER_PDF_CSS])
        print(f"  Done: {output_path}")


def extract_body_content(filepath):
    """Extract the inner content from the <main class='main-content'> section."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract everything between <main class="main-content"> and </main>
    match = re.search(r'<main\s+class="main-content">(.*?)</main>', content, re.DOTALL)
    if match:
        body = match.group(1)
        # Remove logo container
        body = re.sub(r'<div class="logo-container">.*?</div>', '', body, flags=re.DOTALL)
        # Remove download buttons
        body = re.sub(r'<div class="takeaway-download">.*?</div>\s*</div>\s*</div>', '</div>', body, flags=re.DOTALL)
        body = re.sub(r'<a[^>]*class="takeaway-download-btn"[^>]*>.*?</a>', '', body, flags=re.DOTALL)
        body = re.sub(r'<span class="takeaway-download-text">.*?</span>', '', body, flags=re.DOTALL)
        body = re.sub(r'<span class="download-instructions">.*?</span>', '', body, flags=re.DOTALL)
        return body
    return ""


def build_full_playbook_html():
    """Build a single HTML document combining all chapters in the full playbook style."""

    # Collect all chapter body content
    sections = []

    # Add module intros and their chapters
    module_chapters = {1: [], 2: [], 3: []}
    for filename, ch_num, mod_num, title in CHAPTERS:
        module_chapters[mod_num].append((filename, ch_num, title))

    for mod_filename, mod_num, mod_title in MODULE_INTROS:
        # Add module intro
        mod_path = os.path.join(BASE_DIR, mod_filename)
        if os.path.exists(mod_path):
            mod_content = extract_body_content(mod_path)
            if mod_content:
                sections.append(('module_intro', mod_num, mod_title, mod_content))

        # Add chapters in this module
        for filename, ch_num, title in module_chapters.get(mod_num, []):
            filepath = os.path.join(BASE_DIR, filename)
            if os.path.exists(filepath):
                content = extract_body_content(filepath)
                if content:
                    sections.append(('chapter', ch_num, title, content))

    # Add supplementary content
    for filename, title in SUPPLEMENTARY:
        filepath = os.path.join(BASE_DIR, filename)
        if os.path.exists(filepath):
            content = extract_body_content(filepath)
            if content:
                sections.append(('supplementary', 0, title, content))

    # Build the full HTML
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

    # Table of contents
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
        <div class="page-top-bar"></div>
        <div class="page-content">
            <h1 class="section-title">Table of Contents</h1>
            <div class="title-divider"></div>
            <ul class="toc-list">
                {''.join(toc_items)}
            </ul>
        </div>
    </div>
    """)

    # Content sections
    for section_type, num, title, content in sections:
        if section_type == 'module_intro':
            header = f'<p class="pillar-ref">Module {num}</p>'
            heading = f'<h1 class="section-title">{title}</h1>'
        elif section_type == 'chapter':
            header = f'<p class="pillar-ref">Chapter {num}</p>'
            heading = f'<h1 class="section-title">{title}</h1>'
        else:
            header = ''
            heading = f'<h1 class="section-title">{title}</h1>'

        body_parts.append(f"""
        <div class="content-section">
            <div class="page-top-bar"></div>
            <div class="page-content">
                {header}
                {heading}
                <div class="title-divider"></div>
                <div class="chapter-body">
                    {content}
                </div>
            </div>
        </div>
        """)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: letter;
            margin: 50px 60px 60px 60px;

            @bottom-right {{
                content: counter(page);
                font-family: 'Helvetica', 'Arial', sans-serif;
                font-size: 10px;
                color: #666;
            }}
        }}

        @page :first {{
            @bottom-right {{
                content: none;
            }}
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html, body {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            color: #333;
            line-height: 1.6;
            font-size: 11px;
        }}

        /* Cover page */
        .cover-page {{
            page-break-after: always;
            text-align: center;
            padding-top: 80px;
        }}

        .cover-top-bar {{
            position: absolute;
            top: -50px;
            left: -60px;
            right: -60px;
            height: 8px;
            background: #0B38DB;
        }}

        .cover-content {{
            margin-top: 120px;
        }}

        .cover-title {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 42px;
            font-weight: 800;
            color: #0B38DB;
            line-height: 1.2;
            margin-bottom: 30px;
        }}

        .cover-divider {{
            width: 200px;
            height: 4px;
            background: #FF7600;
            margin: 30px auto;
        }}

        .cover-subtitle {{
            font-size: 18px;
            font-weight: 700;
            color: #FF7600;
            margin-bottom: 30px;
        }}

        .cover-description {{
            font-size: 13px;
            color: #555;
            line-height: 1.8;
            margin-bottom: 80px;
        }}

        .cover-company {{
            font-size: 22px;
            font-weight: 800;
            color: #FF7600;
            margin-top: 60px;
        }}

        /* TOC page */
        .toc-page {{
            page-break-after: always;
        }}

        .toc-list {{
            list-style: none;
            padding: 0;
        }}

        .toc-module {{
            font-size: 14px;
            font-weight: 700;
            color: #0B38DB;
            margin-top: 16px;
            margin-bottom: 4px;
            padding: 6px 0;
            border-bottom: 1px solid #eee;
        }}

        .toc-chapter {{
            font-size: 12px;
            color: #333;
            padding: 4px 0 4px 20px;
            border-bottom: 1px solid #f5f5f5;
        }}

        .toc-supplementary {{
            font-size: 12px;
            color: #555;
            padding: 4px 0 4px 0;
            margin-top: 12px;
            border-bottom: 1px solid #eee;
            font-style: italic;
        }}

        /* Page top bar */
        .page-top-bar {{
            position: relative;
            top: -50px;
            left: -60px;
            right: 0;
            width: calc(100% + 120px);
            height: 6px;
            background: #0B38DB;
            margin-bottom: -44px;
        }}

        .page-content {{
            padding: 0;
        }}

        /* Content sections */
        .content-section {{
            page-break-before: always;
        }}

        .pillar-ref {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11px;
            font-weight: 600;
            color: #888;
            margin-bottom: 4px;
        }}

        .section-title {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 26px;
            font-weight: 800;
            color: #0B38DB;
            line-height: 1.25;
            margin-bottom: 12px;
        }}

        .title-divider {{
            width: 100%;
            max-width: 500px;
            height: 3px;
            background: #FF7600;
            margin: 16px 0 20px 0;
        }}

        /* Override chapter body styles from HTML */
        .chapter-body {{
            font-size: 11px;
            line-height: 1.65;
        }}

        .chapter-body .pillar-label,
        .chapter-body .chapter-label {{
            display: none !important;
        }}

        .chapter-body .header-section {{
            display: block !important;
            margin-bottom: 16px;
        }}

        .chapter-body .intro-image {{
            display: none !important;
        }}

        .chapter-body h1 {{
            display: none !important;
        }}

        .chapter-body h2 {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 20px;
            font-weight: 800;
            color: #0B38DB;
            margin-top: 24px;
            margin-bottom: 10px;
            line-height: 1.3;
        }}

        .chapter-body h3 {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 15px;
            font-weight: 700;
            color: #0B38DB;
            margin-top: 16px;
            margin-bottom: 8px;
        }}

        .chapter-body h4 {{
            font-size: 13px;
            font-weight: 700;
            color: #333;
            margin-top: 12px;
            margin-bottom: 6px;
        }}

        .chapter-body p {{
            margin-bottom: 10px;
            text-align: justify;
        }}

        .chapter-body .intro-text {{
            font-style: italic;
            margin-bottom: 10px;
        }}

        .chapter-body .chapter-description {{
            margin-bottom: 14px;
        }}

        .chapter-body ul, .chapter-body ol {{
            margin: 8px 0 12px 24px;
        }}

        .chapter-body li {{
            margin-bottom: 4px;
        }}

        .chapter-body img {{
            max-width: 100% !important;
            height: auto !important;
        }}

        /* Learning box */
        .chapter-body .learning-box {{
            background: #f8f9fc;
            border-left: 4px solid #0B38DB;
            padding: 14px 18px;
            margin: 16px 0;
            border-radius: 4px;
        }}

        .chapter-body .learning-box h3 {{
            color: #0B38DB;
            font-size: 14px;
            margin-top: 0;
            margin-bottom: 8px;
        }}

        /* Definition box */
        .chapter-body .definition-box {{
            background: #f9f9f9;
            border: 1px solid #e0e0e0;
            padding: 14px 18px;
            margin: 12px 0;
            border-radius: 4px;
        }}

        /* AI types */
        .chapter-body .ai-types {{
            margin: 12px 0;
        }}

        .chapter-body .ai-type {{
            background: #f8f9fc;
            border-left: 3px solid #FF7600;
            padding: 10px 14px;
            margin: 8px 0;
            border-radius: 3px;
        }}

        .chapter-body .ai-type-label {{
            font-weight: 700;
            color: #FF7600;
            font-size: 13px;
            margin-bottom: 4px;
        }}

        /* Myth blocks */
        .chapter-body .myth-block {{
            background: #f8f9fc;
            border: 1px solid #e8e8e8;
            padding: 12px 16px;
            margin: 10px 0;
            border-radius: 4px;
        }}

        .chapter-body .myth-label {{
            font-weight: 700;
            color: #FF7600;
            font-size: 12px;
            margin-bottom: 4px;
        }}

        .chapter-body .myth-text {{
            font-style: italic;
            color: #555;
            margin-bottom: 6px;
        }}

        .chapter-body .reality-label {{
            font-weight: 700;
            color: #333;
            font-size: 12px;
        }}

        /* Takeaway box */
        .chapter-body .takeaways-box {{
            background: #0B38DB;
            color: #fff;
            padding: 18px 22px;
            margin: 24px 0 12px 0;
            border-radius: 6px;
        }}

        .chapter-body .takeaways-box h2 {{
            color: #fff !important;
            font-size: 18px;
            margin-top: 0;
        }}

        .chapter-body .takeaways-box p {{
            color: #fff;
            font-weight: 600;
        }}

        .chapter-body .takeaway-download {{
            display: none !important;
        }}

        .chapter-body .download-instructions {{
            display: none !important;
        }}

        /* Tables */
        .chapter-body table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
            font-size: 10px;
        }}

        .chapter-body th {{
            background: #0B38DB;
            color: #fff;
            padding: 8px 10px;
            text-align: left;
            font-weight: 600;
        }}

        .chapter-body td {{
            padding: 8px 10px;
            border-bottom: 1px solid #e0e0e0;
            vertical-align: top;
        }}

        .chapter-body tr:nth-child(even) td {{
            background: #f8f9fc;
        }}

        /* Info boxes */
        .chapter-body .info-box,
        .chapter-body .key-insight,
        .chapter-body .best-practice {{
            background: #f0f4ff;
            border-left: 4px solid #0B38DB;
            padding: 12px 16px;
            margin: 12px 0;
            border-radius: 3px;
        }}

        /* Journey steps, process steps, etc */
        .chapter-body .journey-step,
        .chapter-body .step {{
            margin: 10px 0;
            padding: 10px 14px;
            background: #fafafa;
            border-left: 3px solid #FF7600;
            border-radius: 3px;
        }}

        .chapter-body .step-number {{
            font-weight: 700;
            color: #0B38DB;
        }}

        /* Numbered sections */
        .chapter-body .numbered-section {{
            margin: 16px 0;
        }}

        /* Cards / grid items */
        .chapter-body .cards-grid,
        .chapter-body .role-cards {{
            display: block !important;
        }}

        .chapter-body .card,
        .chapter-body .role-card {{
            background: #f8f9fc;
            border: 1px solid #e0e0e0;
            padding: 10px 14px;
            margin: 8px 0;
            border-radius: 4px;
        }}

        /* Horizontal rule / divider */
        .chapter-body hr,
        .chapter-body .divider {{
            border: none;
            border-top: 2px solid #0B38DB;
            margin: 20px 0;
        }}

        /* Sidebar content should be hidden */
        .chapter-body .sidebar {{
            display: none !important;
        }}

        /* Strong / bold labels in orange */
        .chapter-body .highlight,
        .chapter-body .orange-text {{
            color: #FF7600;
            font-weight: 700;
        }}

        /* Benefits list */
        .chapter-body .benefits-list li {{
            margin-bottom: 6px;
        }}

        /* Scenario boxes */
        .chapter-body .scenario-box {{
            background: #fff8f0;
            border-left: 4px solid #FF7600;
            padding: 12px 16px;
            margin: 10px 0;
            border-radius: 3px;
        }}

        /* Assessment/quiz sections */
        .chapter-body .assessment-section,
        .chapter-body .quiz-section {{
            background: #f8f9fc;
            padding: 14px 18px;
            margin: 12px 0;
            border-radius: 4px;
            border: 1px solid #e0e0e0;
        }}

        /* Module intro specific */
        .chapter-body .module-title {{
            font-size: 22px;
            color: #0B38DB;
            font-weight: 800;
        }}

        .chapter-body .module-label {{
            color: #FF7600;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
        }}
    </style>
</head>
<body>
    {''.join(body_parts)}
</body>
</html>"""

    return full_html


def generate_full_playbook():
    """Generate the combined full playbook PDF."""
    output_path = os.path.join(OUTPUT_DIR, "Full_AI_Leadership_Playbook.pdf")
    print(f"  Building full playbook HTML...")

    html_content = build_full_playbook_html()

    # Save HTML for debugging
    html_path = os.path.join(OUTPUT_DIR, "_full_playbook.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"  Generating full playbook PDF...")
    html = HTML(string=html_content, base_url=BASE_DIR)
    html.write_pdf(output_path)
    print(f"  Done: {output_path}")


if __name__ == "__main__":
    print("=== Generating Individual Chapter PDFs ===")
    generate_individual_chapter_pdfs()

    print("\n=== Generating Module Intro PDFs ===")
    generate_module_intro_pdfs()

    print("\n=== Generating Supplementary PDFs ===")
    generate_supplementary_pdfs()

    print("\n=== Generating Full Combined Playbook PDF ===")
    generate_full_playbook()

    print("\n=== All PDFs generated! ===")
    print(f"Output directory: {OUTPUT_DIR}")
