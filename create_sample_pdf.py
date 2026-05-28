from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


APP_DIR = Path(__file__).parent
SOURCE_PATH = APP_DIR / "sample_medical_reference.md"
OUTPUT_PATH = APP_DIR / "sample_medical_reference.pdf"


def markdown_to_story(markdown: str):
    styles = getSampleStyleSheet()
    story = []

    for block in markdown.split("\n\n"):
        text = block.strip()
        if not text:
            continue

        if text.startswith("# "):
            story.append(Paragraph(text[2:], styles["Title"]))
        elif text.startswith("## "):
            story.append(Spacer(1, 10))
            story.append(Paragraph(text[3:], styles["Heading2"]))
        else:
            story.append(Paragraph(text, styles["BodyText"]))
        story.append(Spacer(1, 8))

    return story


def main() -> None:
    document = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
        title="Sample Medical Reference For RAG Testing",
    )
    markdown = SOURCE_PATH.read_text(encoding="utf-8")
    document.build(markdown_to_story(markdown))
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
