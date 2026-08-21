from pathlib import Path

import pytesseract
from PIL import Image


class OCRService:
    """Extract text and word-level information from document images."""

    def extract(self, image_path: str) -> dict:
        image_file = Path(image_path)

        if not image_file.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = Image.open(image_file)

        text = pytesseract.image_to_string(
            image,
            config="--psm 6",
        ).strip()

        data = pytesseract.image_to_data(
            image,
            config="--psm 6",
            output_type=pytesseract.Output.DICT,
        )

        words = []

        for index, word in enumerate(data["text"]):
            word = word.strip()

            if not word:
                continue

            try:
                confidence = float(data["conf"][index])
            except (ValueError, TypeError):
                confidence = -1.0

            if confidence < 0:
                continue

            words.append(
                {
                    "text": word,
                    "confidence": round(confidence, 2),
                    "x": data["left"][index],
                    "y": data["top"][index],
                    "width": data["width"][index],
                    "height": data["height"][index],
                }
            )

        average_confidence = (
            sum(word["confidence"] for word in words) / len(words)
            if words
            else 0.0
        )

        return {
            "text": text,
            "average_confidence": round(average_confidence, 2),
            "word_count": len(words),
            "words": words,
        }
