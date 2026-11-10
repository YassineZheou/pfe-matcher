from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent.parent


def main():
    source = (ROOT / "data" / "sample_topics.txt").read_text(encoding="utf-8")
    styles = getSampleStyleSheet()
    story = []
    for line in source.splitlines():
        if not line.strip():
            story.append(Spacer(1, 8))
            continue
        style = styles["Heading3"] if line.startswith("DEMO") else styles["BodyText"]
        story.append(Paragraph(line, style))
    SimpleDocTemplate(str(ROOT / "data" / "sample_book.pdf"), pagesize=A4).build(story)


if __name__ == "__main__":
    main()
