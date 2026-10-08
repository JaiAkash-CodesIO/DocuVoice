from pathlib import Path
import pytest
from PIL import Image

from backend.app.services.preprocessing.image_processor import ImageProcessor


def test_image_processor_resizing(tmp_path):
    # Create temporary source image
    input_file = tmp_path / "test_input.png"
    output_file = tmp_path / "test_processed.png"

    img = Image.new("RGB", (800, 600), color=(200, 200, 200))
    img.save(input_file)

    processor = ImageProcessor(target_width=1600, minimum_width=1400)
    result = processor.process(str(input_file), str(output_file))

    assert Path(result["output_path"]).exists()
    assert result["original_width"] == 800
    assert result["original_height"] == 600
    assert result["processed_width"] >= 1400


def test_image_processor_invalid_file(tmp_path):
    processor = ImageProcessor()
    non_existent = str(tmp_path / "does_not_exist.png")
    output = str(tmp_path / "output.png")

    with pytest.raises(ValueError):
        processor.process(non_existent, output)
