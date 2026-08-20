from pathlib import Path

import cv2


class ImageProcessor:
    """Preprocess document images for OCR."""

    def __init__(self, target_width: int = 1600):
        self.target_width = target_width

    def process(self, input_path: str, output_path: str) -> dict:
        input_file = Path(input_path)
        output_file = Path(output_path)

        image = cv2.imread(str(input_file))

        if image is None:
            raise ValueError(f"Unable to read image: {input_path}")

        original_height, original_width = image.shape[:2]

        image = self._resize(image)

        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        denoised = cv2.GaussianBlur(grayscale, (3, 3), 0)

        thresholded = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2,
        )

        output_file.parent.mkdir(parents=True, exist_ok=True)

        if not cv2.imwrite(str(output_file), thresholded):
            raise ValueError(f"Unable to write processed image: {output_path}")

        processed_height, processed_width = thresholded.shape

        return {
            "original_width": original_width,
            "original_height": original_height,
            "processed_width": processed_width,
            "processed_height": processed_height,
            "output_path": str(output_file),
        }

    def _resize(self, image):
        height, width = image.shape[:2]

        if width <= self.target_width:
            return image

        scale = self.target_width / width
        new_width = self.target_width
        new_height = int(height * scale)

        return cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA,
        )
