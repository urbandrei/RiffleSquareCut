"""Date range helpers for reports."""

from datetime import datetime, timedelta, date


def start_of_today() -> datetime:
    return datetime.combine(date.today(), datetime.min.time())


def start_of_week() -> datetime:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return datetime.combine(monday, datetime.min.time())


def start_of_month() -> datetime:
    today = date.today()
    return datetime.combine(today.replace(day=1), datetime.min.time())


def date_range_label(start: datetime) -> str:
    """Human-readable label for a date range starting at `start` until now."""
    today = date.today()
    if start.date() == today:
        return "Today"
    elif start.date() == today - timedelta(days=today.weekday()):
        return "This Week"
    elif start.date() == today.replace(day=1):
        return "This Month"
    return f"Since {start.strftime('%b %d')}"
