"""API v1 router for receipt and expense extraction endpoints."""

from fastapi import APIRouter, File, UploadFile

import services.expense
from schemas.schemas import ExpenseData

expense_router = APIRouter()


@expense_router.post("/expense", tags=["expense"], response_model=ExpenseData)
async def expense(
    image: UploadFile = File(..., description="The image file"),
) -> ExpenseData:
    """Extract financial and merchant data from an uploaded receipt or UPI screenshot.

    Validates file content type, checks for financial markers via local OCR,
    and extracts structured expense data using the Gemini model.

    :param image: Uploaded image file (PNG, JPEG, WebP).
    :return: Structured ExpenseData containing extraction results.
    """
    return await services.expense.extract_expense_data(image)
