from datetime import timedelta

from billing.dates import add_month


def billing_periods(start, end):
    """Monthly billing periods from `start` (the signup date) until `end`.

    Each period is (period_start, period_end) with period_end inclusive.
    """
    periods = []
    current = start
    while current <= end:
        nxt = add_month(current)
        periods.append((current, nxt - timedelta(days=1)))
        current = nxt
    return periods


def next_renewal(signup, today):
    """First renewal date strictly after `today` for a customer who signed up on `signup`."""
    renewal = add_month(signup)
    while renewal <= today:
        renewal = add_month(renewal)
    return renewal


def prorate(amount, signup, change_day):
    """Refund for the unused part of the current period when a plan changes on `change_day`."""
    period_start = signup
    while True:
        period_end = add_month(period_start)
        if period_end > change_day:
            break
        period_start = period_end
    total_days = (period_end - period_start).days
    remaining = (period_end - change_day).days
    return round(amount * remaining / total_days, 2)
