from pathlib import Path

from pypdf import PdfReader


class PDFLoader:
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def load(self) -> list[dict[str, object]]:
        reader = PdfReader(str(self.file_path))
        pages: list[dict[str, object]] = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append({"page": page_number, "content": text})
        return pages
