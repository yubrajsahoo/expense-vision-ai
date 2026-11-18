import pytest
from pydantic import ValidationError

from schemas.schemas import ExpenseData


def test_expense_data_minimal_defaults():
    """Verify that only is_financial is required and other fields default to None."""
    data = ExpenseData(is_financial=False)
    assert data.is_financial is False
    assert data.merchant_name is None
    assert data.amount is None
    assert data.date is None
    assert data.payment_method is None
    assert data.utr_number is None


def test_expense_data_fully_populated():
    """Verify ExpenseData correctly stores all populated financial attributes."""
    data = ExpenseData(
        is_financial=True,
        merchant_name="SuperMart",
        amount=520.75,
        date="2026-11-18",
        payment_method="UPI",
        utr_number="123456789012",
    )
    assert data.is_financial is True
    assert data.merchant_name == "SuperMart"
    assert data.amount == 520.75
    assert data.date == "2026-11-18"
    assert data.payment_method == "UPI"
    assert data.utr_number == "123456789012"

    dumped = data.model_dump()
    assert dumped == {
        "is_financial": True,
        "merchant_name": "SuperMart",
        "amount": 520.75,
        "date": "2026-11-18",
        "payment_method": "UPI",
        "utr_number": "123456789012",
    }


def test_expense_data_missing_required_is_financial():
    """Verify ValidationError is raised when is_financial is omitted."""
    with pytest.raises(ValidationError) as exc_info:
        ExpenseData()

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("is_financial",)
    assert errors[0]["type"] == "missing"


def test_expense_data_json_roundtrip():
    """Verify serialization to JSON and deserialization via model_validate_json."""
    original = ExpenseData(
        is_financial=True,
        merchant_name="Cafe Coffee Day",
        amount=199.0,
        date="2026-11-18",
        payment_method="Google Pay",
        utr_number="UTR123456",
    )
    json_str = original.model_dump_json()
    reconstructed = ExpenseData.model_validate_json(json_str)
    assert reconstructed == original


def test_expense_data_amount_int_to_float_coercion():
    """Verify integer amount is coerced into a float."""
    data = ExpenseData(is_financial=True, amount=100)
    assert isinstance(data.amount, float)
    assert data.amount == 100.0


def test_expense_data_invalid_amount_type():
    """Verify ValidationError when amount cannot be parsed as a float."""
    with pytest.raises(ValidationError) as exc_info:
        ExpenseData(is_financial=True, amount="not_a_valid_amount")

    errors = exc_info.value.errors()
    assert errors[0]["loc"] == ("amount",)


def test_expense_data_invalid_is_financial_type():
    """Verify ValidationError when is_financial cannot be parsed as a boolean."""
    with pytest.raises(ValidationError) as exc_info:
        ExpenseData(is_financial="not_a_boolean")

    errors = exc_info.value.errors()
    assert errors[0]["loc"] == ("is_financial",)
