import calendar
from datetime import date


def days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


def add_month(d):
    """Return the same day next month, clamped to the last day of that month."""
    year = d.year + (d.month // 12)
    month = d.month % 12 + 1
    day = min(d.day, days_in_month(year, month))
    return date(year, month, day)
