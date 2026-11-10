import io
import re

from .models import Topic
from .skills import extract_skills

HEADER = re.compile(r"^\s*([A-Z]{1,4})\s?(\d{3})\s*[:\-–—]\s*(.+?)\s*$", re.MULTILINE)
DURATION = re.compile(
    r"dur[ée]e\s*:\s*(\d+)(?:\s*(?:à|a|-|–)\s*(\d+))?\s*mois", re.IGNORECASE
)
PLACES = re.compile(r"places?\s*:\s*(\d+)", re.IGNORECASE)


def read_pdf_bytes(data):
    import pdfplumber

    pages = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    text = "\n".join(pages)
    if text.strip():
        return text
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    return "\n".join(p.extract_text() or "" for p in reader.pages)


def read_bytes(filename, data):
    if filename.lower().endswith(".pdf"):
        return read_pdf_bytes(data)
    return data.decode("utf-8", errors="replace")


def read_file(path):
    with open(path, "rb") as handle:
        return read_bytes(str(path), handle.read())


def clean(text):
    text = text.replace("\u00a0", " ").replace("\x00", "")
    text = re.sub(r"\(cid:\d+\)", "-", text)
    return re.sub(r"[ \t]+", " ", text)


def parse_topics(text):
    text = clean(text)
    headers = list(HEADER.finditer(text))
    topics = []
    seen = set()
    for index, header in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        body = text[header.end():end].strip()
        ref = f"{header.group(1)} {header.group(2)}"
        if ref in seen:
            continue
        seen.add(ref)
        title = header.group(3)
        duration = DURATION.search(body)
        places = PLACES.search(body)
        d_min = d_max = None
        if duration:
            d_min = int(duration.group(1))
            d_max = int(duration.group(2)) if duration.group(2) else d_min
        topics.append(
            Topic(
                ref=ref,
                title=title,
                text=body,
                skills=extract_skills(f"{title}\n{body}"),
                duration_min=d_min,
                duration_max=d_max,
                places=int(places.group(1)) if places else None,
            )
        )
    return topics
