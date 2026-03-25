"""Currency formatting helpers."""

from decimal import Decimal, ROUND_HALF_UP


def fmt(amount) -> str:
    """Format a number as $X,XXX.XX."""
    d = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"${d:,.2f}"


def to_decimal(value: str) -> Decimal:
    """Parse a user-entered dollar amount, stripping $ and commas."""
    cleaned = value.replace("$", "").replace(",", "").strip()
    return Decimal(cleaned).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
