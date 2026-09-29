from pathlib import Path

import cv2
import pymupdf


class ImageProcessor:
    """Generate OCR-ready preprocessing variants."""

    def __init__(
        self,
        target_width: int = 1600,
        minimum_width: int = 1400,
    ):
        self.target_width = target_width
        self.minimum_width = minimum_width

    def process(self, input_path: str, output_path: str) -> dict:
        input_file = Path(input_path)
        output_file = Path(output_path)

        image = cv2.imread(str(input_file))

        if image is None:
            raise ValueError(f"Unable to read image: {input_path}")

        original_height, original_width = image.shape[:2]

        image = self._resize(image)

        grayscale = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not cv2.imwrite(
            str(output_file),
            grayscale,
        ):
            raise ValueError(
                f"Unable to write processed image: {output_path}"
            )

        processed_height, processed_width = grayscale.shape

        return {
            "original_width": original_width,
            "original_height": original_height,
            "processed_width": processed_width,
            "processed_height": processed_height,
            "output_path": str(output_file),
        }
    def process_pdf(
        self,
        input_path: str,
        output_directory: str,
    ) -> list:
        input_file = Path(input_path)
        output_dir = Path(output_directory)

        if not input_file.exists():
            raise FileNotFoundError(
                f"PDF not found: {input_path}"
            )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        document = pymupdf.open(str(input_file))
        processed_pages = []

        try:
            for page_number, page in enumerate(
                document,
                start=1,
            ):
                pixmap = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False,
                )

                page_image = output_dir / (
                    f"{input_file.stem}"
                    f"_page_{page_number}.png"
                )

                pixmap.save(str(page_image))

                processed_pages.append(
                    {
                        "page_number": page_number,
                        "output_path": str(page_image),
                    }
                )
        finally:
            document.close()

        if not processed_pages:
            raise ValueError(
                f"PDF contains no pages: {input_path}"
            )

        return processed_pages

    def generate_variants(self, input_path: str) -> dict:
        input_file = Path(input_path)

        image = cv2.imread(str(input_file))

        if image is None:
            raise ValueError(
                f"Unable to read image: {input_path}"
            )

        image = self._resize(image)

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

    def _resize(self, image):
        height, width = image.shape[:2]

        if width < self.minimum_width:
            scale = self.minimum_width / width

            new_width = self.minimum_width
            new_height = int(height * scale)

            return cv2.resize(
                image,
                (new_width, new_height),
                interpolation=cv2.INTER_CUBIC,
            )

        if width > self.target_width:
            scale = self.target_width / width

            new_width = self.target_width
            new_height = int(height * scale)

            return cv2.resize(
                image,
                (new_width, new_height),
                interpolation=cv2.INTER_AREA,
            )

        return image