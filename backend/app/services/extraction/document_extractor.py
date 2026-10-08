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
            "tables": self._extract_tables(ocr_result),
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
                "bill to",
                "subtotal",
                "tax amount",
            ],
            "receipt": [
                "receipt",
                "cashier",
                "thank you for your purchase",
                "change",
                "payment method",
            ],
            "resume": [
                "resume",
                "curriculum vitae",
                "work experience",
                "professional experience",
                "education",
                "skills",
                "employment history",
            ],
            "certificate": [
                "certificate",
                "certify that",
                "awarded to",
                "this is to certify",
            ],
            "application": [
                "application form",
                "applicant",
                "application number",
                "date of birth",
            ],
            "report": [
                "executive summary",
                "introduction",
                "methodology",
                "findings",
                "conclusion",
                "recommendations",
            ],
            "letter": [
                "dear ",
                "subject:",
                "sincerely",
                "regards",
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

        best_score = scores[best_type]

        if best_score == 0:
            return "general_document"

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
                    cleaned_t = self._clean_heading(current_title)
                    if cleaned_t:
                        sections.append(
                            {
                                "title": cleaned_t,
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
            cleaned_t = self._clean_heading(current_title)
            if cleaned_t:
                sections.append(
                    {
                        "title": cleaned_t,
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

        alphabetic_count = sum(
            1
            for char in cleaned
            if char.isalpha()
        )

        if alphabetic_count == 0:
            return False

        uppercase_count = sum(
            1
            for char in cleaned
            if char.isupper()
        )

        uppercase_ratio = (
            uppercase_count / alphabetic_count
        )

        if uppercase_ratio >= 0.75:
            return True

        heading_keywords = {
            "education",
            "experience",
            "skills",
            "projects",
            "certification",
            "certifications",
            "summary",
            "profile",
            "objective",
            "introduction",
            "background",
            "methodology",
            "results",
            "findings",
            "conclusion",
            "recommendations",
            "references",
            "qualifications",
            "achievements",
            "contact",
            "personal information",
            "work experience",
            "professional experience",
            "academic qualifications",
        }

        normalized = " ".join(words).lower()
        clean_normalized = re.sub(r"^[&</>|•*\-#\s]+", "", normalized).strip()

        return normalized in heading_keywords or clean_normalized in heading_keywords

    def _clean_heading(self, line: str) -> str:
        # Strip leading decorative bullets, icons, or separators
        cleaned = re.sub(r"^[&</>|•*\-#\s]+", "", line).strip()
        return cleaned if cleaned else line.strip()

    def _extract_entities(self, text: str) -> dict:
        entities = {
            "emails": [],
            "phone_numbers": [],
            "dates": [],
            "urls": [],
        }

        # 1. Emails
        entities["emails"] = list(
            dict.fromkeys(
                re.findall(
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
                    text,
                )
            )
        )

        # 2. Phone Numbers (including +91, Indian 10-digit mobile, US/UK international formats)
        entities["phone_numbers"] = list(
            dict.fromkeys(
                re.findall(
                    r"(?:\+91[-.\s]?[6-9]\d{9}|(?<!\d)(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3,5}\)?[-.\s]?)\d{3,5}[-.\s]?\d{3,5}(?!\d))",
                    text,
                )
            )
        )

        # 3. Dates
        entities["dates"] = list(
            dict.fromkeys(
                re.findall(
                    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b",
                    text,
                    re.IGNORECASE,
                )
            )
        )

        # 4. URLs (including github.com, linkedin.com, portfolio domains even without https://)
        raw_urls = re.findall(
            r"\b(?:https?://[^\s]+|www\.[^\s]+|(?:linkedin\.com/in/|github\.com/)[A-Za-z0-9_.-]+|[A-Za-z0-9_.-]+\.(?:com|org|net|io|dev|ai|in)/[^\s,]*)\b",
            text,
            re.IGNORECASE,
        )
        normalized_urls = []
        for u in raw_urls:
            u_clean = u.rstrip(".,;:)'\"")
            if not u_clean.startswith("http"):
                normalized_urls.append(f"https://{u_clean}")
            else:
                normalized_urls.append(u_clean)

        entities["urls"] = list(dict.fromkeys(normalized_urls))

        return entities
    #new class
    def _extract_tables(self, ocr_result: dict) -> list:
        words = ocr_result.get("words", [])

        if len(words) < 4:
            return []

        rows = self._group_words_into_rows(words)

        if len(rows) < 2:
            return []

        multi_word_rows = [
            row
            for row in rows
            if len(row["words"]) >= 2
        ]

        if len(multi_word_rows) < 2:
            return []

        table = self._build_table(
            multi_word_rows
        )

        if not table:
            return []

        return [table]

    def _group_words_into_rows(self, words: list) -> list:
        sorted_words = sorted(
            words,
            key=lambda word: (
                word["y"],
                word["x"],
            ),
        )

        rows = []

        for word in sorted_words:
            word_center_y = (
                word["y"] + word["height"] / 2
            )

            matched_row = None

            for row in rows:
                row_center_y = row["center_y"]

                tolerance = max(
                    word["height"],
                    row["average_height"],
                ) * 0.6

                if abs(
                    word_center_y - row_center_y
                ) <= tolerance:
                    matched_row = row
                    break

            if matched_row is None:
                rows.append(
                    {
                        "center_y": word_center_y,
                        "average_height": word["height"],
                        "words": [word],
                    }
                )
            else:
                matched_row["words"].append(word)

                heights = [
                    item["height"]
                    for item in matched_row["words"]
                ]

                matched_row["average_height"] = (
                    sum(heights) / len(heights)
                )

                centers = [
                    item["y"] + item["height"] / 2
                    for item in matched_row["words"]
                ]

                matched_row["center_y"] = (
                    sum(centers) / len(centers)
                )

        rows.sort(
            key=lambda row: row["center_y"]
        )

        for row in rows:
            row["words"].sort(
                key=lambda word: word["x"]
            )

        return rows

    def _build_table(self, rows: list) -> dict:
        if len(rows) < 2:
            return {}

        table_rows = []

        for row in rows:
            cells = [
                word["text"]
                for word in row["words"]
            ]

            if len(cells) >= 2:
                table_rows.append(cells)

        if len(table_rows) < 2:
            return {}

        column_count = max(
            len(row)
            for row in table_rows
        )

        if column_count < 2:
            return {}

        headers = table_rows[0]

        normalized_rows = []

        for row in table_rows[1:]:
            normalized_row = row[:column_count]

            while len(normalized_row) < column_count:
                normalized_row.append("")

            normalized_rows.append(
                normalized_row
            )

        return {
            "headers": headers,
            "rows": normalized_rows,
        }