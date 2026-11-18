import logging

from schemas.schemas import ExpenseData
from src.services.extractor import extract_expense_data
from tests.helper.resource_utils import read_as_bytes

_logger = logging.getLogger(__name__)


def test_expense_data_valid_image():
    """
    Tests that the expense data can be extracted from an image
    """
    image_bytes = read_as_bytes("images/valid_financial_image.png")

    expense_data: ExpenseData = extract_expense_data(image_bytes, mime_type="image/png")

    _logger.info("ExpenseData is %s", expense_data)

    assert expense_data is not None


def test_expense_data_invalid_image():
    """
    Tests that the expense data can be extracted from an image
    """
    image_bytes = read_as_bytes("images/invalid_financial_image.png")

    expense_data: ExpenseData = extract_expense_data(image_bytes, mime_type="image/png")

    logging.info("ExpenseData is %s", expense_data)

    assert expense_data is not None

    assert expense_data.is_financial is False
