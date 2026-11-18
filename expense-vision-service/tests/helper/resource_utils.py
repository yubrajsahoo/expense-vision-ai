import logging
from pathlib import Path

_logger = logging.getLogger(__name__)

# Base path pointing to tests/resources
_RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"


def read_as_bytes(relative_path: str) -> bytes:
    """
    Reads a resource file relative to tests/resources and returns its content as bytes.

    Args:
        relative_path (str): Path relative to tests/resources
            (e.g., "images/invalid_financial_image.png").

    Returns:
        bytes: The content of the file in bytes.
    """
    clean_path = (
        str(relative_path)
        .replace("\\", "/")
        .removeprefix("resources/")
        .removeprefix("tests/resources/")
    )
    file_path = _RESOURCES_DIR / clean_path

    if not file_path.is_file():
        alt_path = _RESOURCES_DIR / "images" / clean_path
        if alt_path.is_file():
            file_path = alt_path

    _logger.info(f"Reading image file: {file_path}")
    with open(file_path, "rb") as file:
        return file.read()
