"""Pydantic schemas and data transfer objects for Expense Vision Service."""

from pydantic import BaseModel, Field


class ExpenseData(BaseModel):
    """JSON contract for financial data extracted from receipts and UPI screenshots.

    :cvar is_financial: Whether image is a valid receipt or UPI screenshot.
    :cvar merchant_name: Name of the merchant or recipient, if present.
    :cvar amount: Total transaction or receipt amount as a float, if identified.
    :cvar date: Transaction date formatted in ISO YYYY-MM-DD, if identified.
    :cvar payment_method: Payment method used (e.g., UPI, Card, Cash), if identified.
    :cvar utr_number: Unique Transaction Reference (UTR) number, if present.
    """

    is_financial: bool = Field(
        ...,
        description="Whether the image is a valid financial receipt or UPI screenshot.",
    )
    merchant_name: str | None = Field(
        default=None,
        description="The name of the merchant.",
    )
    amount: float | None = Field(
        default=None,
        description="The amount of the expense.",
    )
    date: str | None = Field(
        default=None,
        description="The date of the expense in YYYY-MM-DD format.",
    )
    payment_method: str | None = Field(
        default=None,
        description="The payment method of the expense.",
    )
    utr_number: str | None = Field(
        default=None,
        description="The UTR number of the expense, if present.",
    )
