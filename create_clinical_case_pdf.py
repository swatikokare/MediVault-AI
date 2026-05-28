from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


APP_DIR = Path(__file__).parent
SOURCE_PATH = APP_DIR / "sample_clinical_case_report.md"
OUTPUT_PATH = APP_DIR / "sample_clinical_case_report.pdf"


def make_styles():
    styles = getSampleStyleSheet()
    styles["Title"].textColor = colors.HexColor("#12323f")
    styles["Heading2"].textColor = colors.HexColor("#0f766e")
    styles["BodyText"].fontSize = 9.5
    styles["BodyText"].leading = 13
    styles.add(
        ParagraphStyle(
            name="Meta",
            parent=styles["BodyText"],
            backColor=colors.HexColor("#f4f9fb"),
            borderColor=colors.HexColor("#cfe3e8"),
            borderWidth=0.5,
            borderPadding=6,
            leading=13,
        )
    )
    return styles


def table_from_markdown(lines: list[str], styles):
    rows = []
    for line in lines:
        if line.strip().startswith("| ---"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append([Paragraph(cell, styles["BodyText"]) for cell in cells])

    table = Table(rows, colWidths=[145, 330])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cfe3e8")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fcfd")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def markdown_to_story(markdown: str):
    styles = make_styles()
    story = []
    blocks = markdown.split("\n\n")

    for block in blocks:
        text = block.strip()
        if not text or text == "---":
            continue

        lines = text.splitlines()
        if all(line.strip().startswith("|") for line in lines):
            story.append(table_from_markdown(lines, styles))
            story.append(Spacer(1, 8))
            continue

        if text.startswith("# "):
            story.append(Paragraph(text[2:], styles["Title"]))
        elif text.startswith("## "):
            story.append(Spacer(1, 6))
            story.append(Paragraph(text[3:], styles["Heading2"]))
        elif text.startswith("**Document type:**"):
            story.append(Paragraph(text.replace("\n", "<br/>"), styles["Meta"]))
        else:
            html = text.replace("\n", "<br/>")
            html = html.replace("**", "<b>", 1).replace("**", "</b>", 1) if html.count("**") >= 2 else html
            while "**" in html:
                html = html.replace("**", "<b>", 1).replace("**", "</b>", 1)
            story.append(Paragraph(html, styles["BodyText"]))
        story.append(Spacer(1, 7))

    return story


def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#55707b"))
    canvas.drawString(42, 24, "Synthetic Clinical Case Report - For RAG Testing Only")
    canvas.drawRightString(A4[0] - 42, 24, f"Page {doc.page}")
    canvas.restoreState()


def main() -> None:
    document = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=42,
        bottomMargin=42,
        title="Synthetic Clinical Case Report For RAG Testing",
    )
    markdown = SOURCE_PATH.read_text(encoding="utf-8")
    document.build(markdown_to_story(markdown), onFirstPage=add_footer, onLaterPages=add_footer)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
