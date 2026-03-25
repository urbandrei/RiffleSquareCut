"""Shared input validators for conversational flows."""

from datetime import date, timedelta


def validate_date_input(text: str) -> str | None:
    """Validate a date string. Returns error message or None if valid.

    Accepts: "today", "tomorrow", "YYYY-MM-DD"
    """
    lower = text.strip().lower()
    if lower in ("today", "tomorrow"):
        return None
    try:
        date.fromisoformat(lower)
    except ValueError:
        return "Enter a date as **YYYY-MM-DD**, **today**, or **tomorrow**."
    return None


def parse_date_input(text: str) -> date:
    """Parse a validated date string into a date object."""
    lower = text.strip().lower()
    if lower == "today":
        return date.today()
    if lower == "tomorrow":
        return date.today() + timedelta(days=1)
    return date.fromisoformat(lower)
