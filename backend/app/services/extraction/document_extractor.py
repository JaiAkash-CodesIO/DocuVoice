import re


class DocumentExtractor:
    """Extract generic structured information from OCR output."""

    def extract(self, ocr_result: dict) -> dict:
        text = ocr_result.get("text", "")
        words = ocr_result.get("words", [])

        return {
            "document_type": self._detect_document_type(text),
            "fields": self._extract_fields(text),
            "sections": self._extract_sections(text),
            "tables": [],
            "entities": self._extract_entities(text),
            "text": text,
            "ocr": {
                "average_confidence": ocr_result.get(
                    "average_confidence",
                    0.0,
                ),
                "word_count": ocr_result.get(
                    "word_count",
                    len(words),
                ),
            },
        }

    def _detect_document_type(self, text: str) -> str:
        text_lower = text.lower()

        document_patterns = {
            "invoice": [
                "invoice",
                "invoice number",
                "amount due",
            ],
            "receipt": [
                "receipt",
                "cashier",
                "thank you for your purchase",
            ],
            "resume": [
                "resume",
                "curriculum vitae",
                "work experience",
                "education",
                "skills",
            ],
            "certificate": [
                "certificate",
                "certify that",
                "awarded to",
            ],
            "application": [
                "application form",
                "applicant",
                "application number",
            ],
            "report": [
                "report",
                "executive summary",
                "conclusion",
            ],
            "letter": [
                "dear",
                "subject:",
                "sincerely",
            ],
        }

        scores = {}

        for document_type, patterns in document_patterns.items():
            score = 0

            for pattern in patterns:
                if pattern in text_lower:
                    score += 1

            scores[document_type] = score

        if not scores:
            return "unknown"

        best_type = max(
            scores,
            key=scores.get,
        )

        if scores[best_type] == 0:
            return "unknown"

        return best_type

    def _extract_fields(self, text: str) -> list:
        fields = []

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        for line in lines:
            match = re.match(
                r"^([^:]{2,60}):\s*(.+)$",
                line,
            )

            if not match:
                continue

            key = match.group(1).strip()
            value = match.group(2).strip()

            if not key or not value:
                continue

            fields.append(
                {
                    "key": key,
                    "value": value,
                }
            )

        return fields

    def _extract_sections(self, text: str) -> list:
        sections = []

        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        current_title = None
        current_content = []

        for line in lines:
            if not line:
                continue

            if self._looks_like_heading(line):
                if current_title is not None:
                    sections.append(
                        {
                            "title": current_title,
                            "content": " ".join(
                                current_content
                            ).strip(),
                        }
                    )

                current_title = line
                current_content = []

            elif current_title is not None:
                current_content.append(line)

        if current_title is not None:
            sections.append(
                {
                    "title": current_title,
                    "content": " ".join(
                        current_content
                    ).strip(),
                }
            )

        return sections

    def _looks_like_heading(self, line: str) -> bool:
        cleaned = line.strip()

        if len(cleaned) < 3:
            return False

        if len(cleaned) > 80:
            return False

        if cleaned.endswith(":"):
            return True

        words = cleaned.split()

        if len(words) > 8:
            return False

        uppercase_count = sum(
            1
            for char in cleaned
            if char.isupper()
        )

        alphabetic_count = sum(
            1
            for char in cleaned
            if char.isalpha()
        )

        if alphabetic_count == 0:
            return False

        uppercase_ratio = (
            uppercase_count / alphabetic_count
        )

        return uppercase_ratio >= 0.75

    def _extract_entities(self, text: str) -> dict:
        entities = {
            "emails": [],
            "phone_numbers": [],
            "dates": [],
            "urls": [],
        }

        entities["emails"] = list(
            dict.fromkeys(
                re.findall(
                    r"\b[A-Za-z0-9._%+-]+"
                    r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
                    text,
                )
            )
        )

        entities["phone_numbers"] = list(
            dict.fromkeys(
                re.findall(
                    r"(?<!\d)"
                    r"(?:\+?\d{1,3}[-.\s]?)?"
                    r"(?:\(?\d{3,5}\)?[-.\s]?)"
                    r"\d{3,5}[-.\s]?\d{3,5}"
                    r"(?!\d)",
                    text,
                )
            )
        )

        entities["dates"] = list(
            dict.fromkeys(
                re.findall(
                    r"\b(?:"
                    r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
                    r"|"
                    r"\d{1,2}\s+"
                    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|"
                    r"Sep|Oct|Nov|Dec)[a-z]*\s+"
                    r"\d{2,4}"
                    r")\b",
                    text,
                    re.IGNORECASE,
                )
            )
        )

        entities["urls"] = list(
            dict.fromkeys(
                re.findall(
                    r"https?://[^\s]+",
                    text,
                    re.IGNORECASE,
                )
            )
        )

        return entities
