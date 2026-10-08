import os
from pathlib import Path
import cv2
import pytesseract
from PIL import Image

from backend.app.services.ocr.sample_data import get_sample_ocr_result

# Auto-detect Tesseract on Windows if installed in standard paths
if os.name == "nt":
    for p in [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
    ]:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            break


class OCRService:
    """Extract text from document images using region-aware OCR."""

    @staticmethod
    def is_engine_available() -> bool:
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def extract(self, image_path: str, hint: str = None) -> dict:
        image_file = Path(image_path)

        if not image_file.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        # If Tesseract binary is not installed, use sample cache if available
        if not self.is_engine_available():
            sample_key = hint or image_file.stem
            if any(k in sample_key.lower() for k in ["invoice", "receipt", "resume", "sample"]):
                return get_sample_ocr_result(sample_key)

            raise RuntimeError(
                "Tesseract OCR engine is not installed on this system. "
                "To process custom images: (1) Run with Docker ('docker compose up'), or "
                "(2) Install Tesseract-OCR for Windows from https://github.com/UB-Mannheim/tesseract/wiki. "
                "Try the 3 preloaded Sample Documents above for an instant demo!"
            )

        variants = self._generate_variants(str(image_file))

        table_result = self._extract_table(
            variants["grayscale"]
        )

        if table_result is None:
            results = []

            for variant_name, image in variants.items():
                for psm in (6, 11):
                    result = self._run_ocr(
                        image,
                        variant_name,
                        psm,
                    )

                    results.append(result)

            best_result = max(
                results,
                key=lambda result: result["score"],
            )

            return {
                "text": best_result["text"],
                "average_confidence": best_result[
                    "average_confidence"
                ],
                "word_count": best_result["word_count"],
                "words": best_result["words"],
                "selected_variant": best_result["variant"],
                "selected_psm": best_result["psm"],
            }

        x, y, width, height = table_result["region"]

        page_image = variants["grayscale"].copy()

        cv2.rectangle(
            page_image,
            (x, y),
            (x + width, y + height),
            255,
            thickness=-1,
        )

        page_results = []

        for psm in (6, 11):
            result = self._run_ocr(
                page_image,
                "grayscale_without_table",
                psm,
            )

            page_results.append(result)

        best_page = max(
            page_results,
            key=lambda result: result["score"],
        )

        combined_words = (
            best_page["words"]
            + table_result["words"]
        )

        combined_text = "\n\n".join(
            part
            for part in (
                best_page["text"],
                table_result["text"],
            )
            if part
        )

        total_confidence = (
            sum(
                word["confidence"]
                for word in combined_words
            )
            / len(combined_words)
            if combined_words
            else 0.0
        )

        return {
            "text": combined_text,
            "average_confidence": round(
                total_confidence,
                2,
            ),
            "word_count": len(combined_words),
            "words": combined_words,
            "selected_variant": "region-aware",
            "selected_psm": 6,
        }

    def _generate_variants(self, image_path: str) -> dict:
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(
                f"Unable to read image: {image_path}"
            )

        height, width = image.shape[:2]

        if width < 1400:
            scale = 1400 / width

            image = cv2.resize(
                image,
                (
                    1400,
                    int(height * scale),
                ),
                interpolation=cv2.INTER_CUBIC,
            )

        elif width > 1600:
            scale = 1600 / width

            image = cv2.resize(
                image,
                (
                    1600,
                    int(height * scale),
                ),
                interpolation=cv2.INTER_AREA,
            )

        grayscale = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        blurred = cv2.GaussianBlur(
            grayscale,
            (3, 3),
            0,
        )

        otsu = cv2.threshold(
            blurred,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )[1]

        adaptive = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2,
        )

        return {
            "grayscale": grayscale,
            "otsu": otsu,
            "adaptive": adaptive,
        }

    def _run_ocr(
        self,
        image,
        variant_name: str,
        psm: int,
        offset_x: int = 0,
        offset_y: int = 0,
    ) -> dict:
        pil_image = Image.fromarray(image)

        config = f"--psm {psm}"

        try:
            text = pytesseract.image_to_string(
                pil_image,
                config=config,
            ).strip()

            data = pytesseract.image_to_data(
                pil_image,
                config=config,
                output_type=pytesseract.Output.DICT,
            )
        except pytesseract.TesseractNotFoundError as exc:
            raise RuntimeError(
                "Tesseract OCR engine is not installed or not available in system PATH. "
                "Please install Tesseract-OCR or run the application inside Docker."
            ) from exc

        words = []

        for index, word in enumerate(data["text"]):
            word = word.strip()

            if not word:
                continue

            try:
                confidence = float(
                    data["conf"][index]
                )
            except (ValueError, TypeError):
                confidence = -1.0

            if confidence < 0:
                continue

            words.append(
                {
                    "text": word,
                    "confidence": round(
                        confidence,
                        2,
                    ),
                    "x": data["left"][index] + offset_x,
                    "y": data["top"][index] + offset_y,
                    "width": data["width"][index],
                    "height": data["height"][index],
                }
            )

        average_confidence = (
            sum(
                word["confidence"]
                for word in words
            )
            / len(words)
            if words
            else 0.0
        )

        score = average_confidence
        return {
            "text": text,
            "average_confidence": round(
                average_confidence,
                2,
            ),
            "word_count": len(words),
            "words": words,
            "variant": variant_name,
            "psm": psm,
            "score": round(score, 2),
        }

    def _extract_table(self, image) -> dict | None:
        binary = cv2.threshold(
            image,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
        )[1]

        height, width = binary.shape

        horizontal_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (max(30, width // 25), 1),
        )

        vertical_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (1, max(30, height // 30)),
        )

        horizontal_lines = cv2.morphologyEx(
            binary,
            cv2.MORPH_OPEN,
            horizontal_kernel,
        )

        vertical_lines = cv2.morphologyEx(
            binary,
            cv2.MORPH_OPEN,
            vertical_kernel,
        )

        table_lines = cv2.add(
            horizontal_lines,
            vertical_lines,
        )

        contours, _ = cv2.findContours(
            table_lines,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        candidates = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            area = w * h

            if w < width * 0.35:
                continue

            if h < height * 0.10:
                continue

            if area < width * height * 0.04:
                continue

            candidates.append(
                (area, x, y, w, h)
            )

        if not candidates:
            return None

        _, x, y, w, h = max(
            candidates,
            key=lambda item: item[0],
        )

        padding = 5

        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(width, x + w + padding)
        y2 = min(height, y + h + padding)

        table = image[y1:y2, x1:x2].copy()

        table_binary = cv2.threshold(
            table,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
        )[1]

        table_height, table_width = table_binary.shape

        h_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (max(20, table_width // 20), 1),
        )

        v_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (1, max(20, table_height // 20)),
        )

        h_lines = cv2.morphologyEx(
            table_binary,
            cv2.MORPH_OPEN,
            h_kernel,
        )

        v_lines = cv2.morphologyEx(
            table_binary,
            cv2.MORPH_OPEN,
            v_kernel,
        )

        line_mask = cv2.add(
            h_lines,
            v_lines,
        )

        table_without_lines = cv2.inpaint(
            table,
            line_mask,
            3,
            cv2.INPAINT_TELEA,
        )

        result = self._run_ocr(
            table_without_lines,
            "table",
            6,
            offset_x=x1,
            offset_y=y1,
        )

        result["region"] = (
            x1,
            y1,
            x2 - x1,
            y2 - y1,
        )

        return result