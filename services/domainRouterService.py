import re


class DomainRouterService:
    INDUSTRY_PATTERNS = [
        re.compile(r"industry\s*[:=-]\s*([A-Za-z0-9 &\-/]+)", flags=re.IGNORECASE),
        re.compile(r"sector\s*[:=-]\s*([A-Za-z0-9 &\-/]+)", flags=re.IGNORECASE),
        re.compile(r"business\s*type\s*[:=-]\s*([A-Za-z0-9 &\-/]+)", flags=re.IGNORECASE),
    ]

    def detect_industry(self, text: str) -> str:
        collapsed = " ".join(text.split())
        for pattern in self.INDUSTRY_PATTERNS:
            match = pattern.search(collapsed)
            if match:
                return match.group(1).strip().lower()
        return "general"
