from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument


def extract_pdf(file_path: str):
    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append({
            "page_number": page_number,
            "text": text.strip()
        })

    return pages


def extract_docx(file_path: str):
    document = DocxDocument(file_path)

    text = []

    for paragraph in document.paragraphs:
        content = paragraph.text.strip()

        if content:
            text.append(content)

    return [{
        "page_number": 1,
        "text": "\n".join(text)
    }]


def extract_txt(file_path: str):
    path = Path(file_path)

    text = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    return [{
        "page_number": 1,
        "text": text.strip()
    }]


def extract_text(file_path: str, file_type: str):

    file_type = file_type.lower()

    if file_type == "pdf":
        return extract_pdf(file_path)

    if file_type == "docx":
        return extract_docx(file_path)

    if file_type == "txt":
        return extract_txt(file_path)

    raise ValueError(
        f"Unsupported file type: {file_type}"
    )