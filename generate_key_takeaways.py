#!/usr/bin/env python3
"""
Generate the Key Takeaways PDF matching the original Calix formatting.

Original format (from PDF stream analysis):
- A4 page (595.28 x 841.89 pts)
- Fonts: Helvetica, Helvetica-Bold, Helvetica-Oblique, ZapfDingbats
- Colors:
    Blue (#0B38DB): rgb(0.043137, 0.219608, 0.858824) - headings, chapter numbers, lines
    Orange (#FF7701): rgb(1, 0.466667, 0.003922) - subtitle, checklist bullets, tagline
    Dark gray (#333): rgb(0.2, 0.2, 0.2) - body text, chapter titles
    Medium gray (#666): rgb(0.4, 0.4, 0.4) - italic sub-points, page number
- Title: Helvetica-Bold 28pt, blue
- Subtitle: Helvetica-Bold 14pt, orange, with orange line below
- Chapter heading: Helvetica-Bold 11pt, "Chapter N:" in blue, rest in dark gray
- Body text: Helvetica 9pt, dark gray, 10pt indent, 11pt leading
- Sub-point: Helvetica-Oblique 8pt, medium gray, 10pt indent, 10pt leading
- Checklist: ZapfDingbats "n" (filled square) in orange, Helvetica 9pt dark gray
- Separator lines: blue 1pt (between sections), blue 3pt (top)
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color

BLUE = Color(0.043137, 0.219608, 0.858824)
ORANGE = Color(1, 0.466667, 0.003922)
DARK_GRAY = Color(0.2, 0.2, 0.2)
MED_GRAY = Color(0.4, 0.4, 0.4)

LEFT = 62.69
RIGHT = 544.58
WIDTH = RIGHT - LEFT

CHAPTERS = [
    # Module 1
    {"module": "Module 1: Understanding AI and Why It Matters"},
    {
        "num": "Chapter 1:",
        "title": " Making AI Simple and Approachable",
        "body": [
            "AI isn\u2019t about replacing your team or overhauling your business overnight. It\u2019s about taking practical steps to simplify",
            "operations, drive innovation, and grow your value with the team you already have.",
        ],
        "sub": [
            "AI works in two key ways: Assistance (conversational AI like Copilot) and Automation (AI Agents handling routine tasks).",
        ],
    },
    {
        "num": "Chapter 2:",
        "title": " Three Initial AI Decisions That Will Set Your Course",
        "body": [
            "Focus on leveraging the AI capabilities within the platforms you already trust and use the three key decisions set",
            "out in this chapter to frame out your early adoption of AI.",
        ],
        "sub": [
            "Ask: What business problems will AI solve? Start with efficiency, consistency, proactivity, professionalism, and personalization.",
        ],
    },
    {
        "num": "Chapter 3:",
        "title": " Education and Enablement",
        "body": [
            "Education and enablement are the foundation for confident, responsible AI adoption. Tailor training to each role,",
            "involve key partners, and use practical delivery methods.",
        ],
        "sub": [
            "Use microlearning, peer-led training, and vendor resources. Key personas: Marketing, Service Techs, CSRs, Network Managers,",
            "IT, and AI Champions.",
        ],
    },
    {
        "num": "Chapter 4:",
        "title": " Change Management",
        "body": [
            "Effective change management is the bridge between AI strategy and AI success. Assess readiness, build coalitions,",
            "manage resistance with empathy, and communicate with clarity.",
        ],
        "sub": [
            "Remember: Transformation is social before it is digital. Build coalitions, not committees. Treat resistance as feedback.",
        ],
    },
    # Module 2
    {"module": "Module 2: Get Started with the Agent Workforce"},
    {
        "num": "Chapter 5:",
        "title": " Activate Your AI Leadership Team",
        "body": [
            "As your first act in adopting AI, set out a specific leadership team with defined roles to lead your company on the",
            "journey to successful AI adoption.",
        ],
        "sub": [
            "Key roles include: Executive Sponsor, AI Lead, Change Champion, and Governance Owner. Start small\u2014even 2-3 people can",
            "drive meaningful progress.",
        ],
    },
    {
        "num": "Chapter 6:",
        "title": " AI is Really a Change Initiative",
        "body": [
            "AI does not create change on its own. Instead, it quickly reveals where change is needed. The organizations that move",
            "fastest treat AI as a business initiative\u2014and prepare their teams, data, and processes to support it.",
        ],
        "sub": [
            "Start with executive alignment on a specific business outcome, assess your readiness honestly, and build the management",
            "habits that let AI deliver lasting value.",
        ],
    },
    {
        "num": "Chapter 7:",
        "title": " The Agent Workforce Journey",
        "body": [
            "Data quality is one of the few levers every organization can fully control. The Agent Workforce Cloud Journey\u2014from",
            "Knowledge Assist to Task Automation to Process Orchestration\u2014only delivers its promise when data quality keeps pace.",
        ],
        "sub": [
            "Treat knowledge enrichment as an ongoing leadership discipline, not a technical chore, and each stage of agent maturity",
            "will compound the last.",
        ],
    },
    {
        "num": "Chapter 8:",
        "title": " Where to Start with the Agentic Workforce",
        "body": [
            "Knowing which AI capability connects to which financial outcome is not always clear. Use the interactive tool to connect",
            "income statement areas and KPIs to the AI capabilities that influence them.",
        ],
        "sub": [
            "Making AI\u2019s business impact visible and actionable helps leadership teams prioritize investments and measure results.",
        ],
    },
    # Module 3
    {"module": "Module 3: Scaling AI Responsibly"},
    {
        "num": "Chapter 9:",
        "title": " Go Slow to Go Fast",
        "body": [
            "AI adoption does not reward organizations that move recklessly. It rewards organizations that move thoughtfully and",
            "build trust as they scale. The goal is not speed alone. The goal is sustainable capability.",
        ],
        "sub": [
            "Measure what matters: adoption rates, time saved, quality improvements, and subscriber experience gains.",
        ],
    },
    {
        "num": "Chapter 10:",
        "title": " AI Governance Goes Mainstream",
        "body": [
            "AI governance is not a side project. It is a leadership responsibility that protects trust, ensures accountability,",
            "and supports long-term innovation.",
        ],
        "sub": [
            "Risk levels vary: Low (embedded SaaS AI), Medium (data/analytics AI), High (custom LLM/agents). Scale governance accordingly.",
        ],
    },
    {
        "num": "Chapter 11:",
        "title": " Organizational Readiness and the Path Forward",
        "body": [
            "AI maturity is not achieved through perfect readiness. It is built through leadership discipline, learning by doing,",
            "and consistent execution.",
        ],
        "sub": [
            "Leadership does not wait for readiness. Leadership creates it.",
        ],
    },
]

CHECKLIST = [
    "Form your AI leadership team with clear roles and responsibilities",
    "Define 2-3 specific business problems AI will help solve",
    "Identify AI capabilities already available in your existing platforms (Calix Cloud, Microsoft 365, etc.)",
    "Establish basic governance guidelines for AI use",
    "Launch role-based training starting with early adopters and champions",
    "Assess organizational readiness and identify gaps to address",
    "Start with a focused pilot and build momentum from measurable wins",
]


def generate_pdf(output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    w, h = A4
    y = h  # current y position

    # Top blue line (3pt)
    c.setStrokeColor(BLUE)
    c.setLineWidth(3)
    c.line(LEFT, h - 34, RIGHT, h - 34)

    y = h - 70

    # Title: "Key Takeaways" - Bold 28pt blue
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(BLUE)
    c.drawString(LEFT, y + 6, "Key Takeaways")
    y -= 38

    # Subtitle: orange bold 14pt
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(ORANGE)
    c.drawString(LEFT, y + 4, "AI Leadership Playbook \u2014 All Modules")
    y -= 18

    # Orange line (2pt)
    c.setStrokeColor(ORANGE)
    c.setLineWidth(2)
    c.line(LEFT, y + 3, RIGHT, y + 3)
    y -= 12

    for item in CHAPTERS:
        if "module" in item:
            # Module header - blue bold 10pt with blue line above
            if y < 100:
                _page_number(c, w)
                c.showPage()
                y = h - 50

            y -= 6
            c.setStrokeColor(BLUE)
            c.setLineWidth(1)
            c.line(LEFT, y + 3, RIGHT, y + 3)
            y -= 14

            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(BLUE)
            c.drawString(LEFT, y + 2, item["module"])
            y -= 16
            continue

        # Check page break
        needed = 11 + len(item["body"]) * 11 + len(item.get("sub", [])) * 10 + 12
        if y - needed < 80:
            _page_number(c, w)
            c.showPage()
            y = h - 50

        # Chapter heading: "Chapter N:" in blue bold 11pt, title in dark gray
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(BLUE)
        num_width = c.stringWidth(item["num"], "Helvetica-Bold", 11)
        c.drawString(LEFT, y + 2, item["num"])
        c.setFillColor(DARK_GRAY)
        c.drawString(LEFT + num_width, y + 2, item["title"])
        y -= 19

        # Body text: Helvetica 9pt, dark gray, indented 10pt, 11pt leading
        c.setFont("Helvetica", 9)
        c.setFillColor(DARK_GRAY)
        for line in item["body"]:
            c.drawString(LEFT + 10, y + 2, line)
            y -= 11

        # Sub-point: Helvetica-Oblique 8pt, medium gray
        if item.get("sub"):
            c.setFont("Helvetica-Oblique", 8)
            c.setFillColor(MED_GRAY)
            for line in item["sub"]:
                c.drawString(LEFT + 10, y + 2, line)
                y -= 10
            y -= 3

    # Separator before checklist
    y -= 4
    c.setStrokeColor(BLUE)
    c.setLineWidth(1)
    c.line(LEFT, y + 3, RIGHT, y + 3)
    y -= 16

    # Check if checklist fits on this page
    checklist_height = 14 + len(CHECKLIST) * 14 + 30
    if y - checklist_height < 40:
        _page_number(c, w)
        c.showPage()
        y = h - 50

    # Checklist title
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(BLUE)
    c.drawString(LEFT, y + 2, "Your AI Adoption Quick-Start Checklist")
    y -= 16

    # Checklist items with orange squares
    for item in CHECKLIST:
        c.setFont("ZapfDingbats", 9)
        c.setFillColor(ORANGE)
        c.drawString(LEFT + 5, y + 3, "n")  # filled square in ZapfDingbats
        c.setFont("Helvetica", 9)
        c.setFillColor(DARK_GRAY)
        c.drawString(LEFT + 18, y + 3, item)
        y -= 14

    # Tagline
    y -= 10
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(ORANGE)
    tagline = "Remember: Calix Success is your partner every step of the way."
    tw = c.stringWidth(tagline, "Helvetica-Bold", 10)
    c.drawString(LEFT + (WIDTH - tw) / 2, y + 3, tagline)

    y -= 16
    # CALIX INC
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(BLUE)
    cw = c.stringWidth("CALIX INC", "Helvetica-Bold", 12)
    c.drawString(LEFT + (WIDTH - cw) / 2, y, "CALIX INC")

    _page_number(c, w)
    c.save()


def _page_number(c, w):
    c.setFont("Helvetica", 9)
    c.setFillColor(MED_GRAY)
    pn = f"Page {c.getPageNumber()}"
    pw = c.stringWidth(pn, "Helvetica", 9)
    c.drawString(w - 85, 42.5, pn)


if __name__ == "__main__":
    output = "pdfs/AI_Leadership_Playbook_Key_Takeaways.pdf"
    generate_pdf(output)
    import os
    print(f"Generated: {output} ({os.path.getsize(output) / 1024:.0f} KB)")
    from PyPDF2 import PdfReader
    r = PdfReader(output)
    print(f"Pages: {len(r.pages)}")
