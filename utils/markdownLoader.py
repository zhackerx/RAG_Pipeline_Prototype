from pathlib import Path


class MarkdownLoader:
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def load(self) -> str:
        return self.file_path.read_text(encoding="utf-8")
