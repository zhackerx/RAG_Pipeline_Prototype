import re
from typing import Any

from config.settings import settings


class SecurityMaskingService:
    def __init__(self) -> None:
        self.pii_patterns = [
            ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
            ("PHONE", re.compile(r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b")),
            ("AADHAAR", re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")),
            ("PAN", re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", flags=re.IGNORECASE)),
            ("IFSC", re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", flags=re.IGNORECASE)),
            ("ACCOUNT", re.compile(r"\b\d{9,18}\b")),
            ("DOB", re.compile(r"\b(?:0?[1-9]|[12][0-9]|3[01])[/-](?:0?[1-9]|1[0-2])[/-](?:19|20)\d{2}\b")),
        ]
        self.phi_patterns = [
            ("MEDICAL_CONDITION", re.compile(r"\b(?:diabetes|hypertension|cancer|hiv|tuberculosis|asthma|hepatitis|renal failure)\b", flags=re.IGNORECASE)),
            ("PATIENT_ID", re.compile(r"\b(?:patient\s*id|mrn|medical\s*record\s*number)\s*[:=-]\s*[A-Za-z0-9-]+", flags=re.IGNORECASE)),
            ("PRESCRIPTION", re.compile(r"\b(?:prescription|medication|dosage)\s*[:=-]\s*[^\n,;]+", flags=re.IGNORECASE)),
        ]

    def mask_text(self, text: str) -> dict[str, Any]:
        if not settings.ENABLE_DATA_MASKING or not text:
            return {"text": text, "summary": {"masked": False, "pii_masks": 0, "phi_masks": 0, "patterns": []}}

        masked_text = text
        pii_count = 0
        phi_count = 0
        matched_patterns: list[str] = []

        if settings.MASK_PII:
            for token, pattern in self.pii_patterns:
                masked_text, count = self._apply_pattern(masked_text, pattern, token)
                if count:
                    pii_count += count
                    matched_patterns.append(token)

        if settings.MASK_PHI:
            for token, pattern in self.phi_patterns:
                masked_text, count = self._apply_pattern(masked_text, pattern, token)
                if count:
                    phi_count += count
                    matched_patterns.append(token)

        return {
            "text": masked_text,
            "summary": {
                "masked": (pii_count + phi_count) > 0,
                "pii_masks": pii_count,
                "phi_masks": phi_count,
                "patterns": sorted(set(matched_patterns)),
            },
        }

    def _apply_pattern(self, text: str, pattern: re.Pattern[str], token: str) -> tuple[str, int]:
        count = 0

        def replace(_: re.Match[str]) -> str:
            nonlocal count
            count += 1
            return f"[REDACTED_{token}]"

        return pattern.sub(replace, text), count
