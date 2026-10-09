"""Order pricing."""


def subtotal(items):
    """Sum of price * qty for (price, qty) pairs."""
    return sum(price * qty for price, qty in items)


def order_total(items, tax_rate=0.0):
    """Total for an order: subtotal plus tax, rounded to cents.

    items: iterable of (unit_price, quantity)
    tax_rate: fraction, e.g. 0.08 for 8%
    """
    if tax_rate < 0:
        raise ValueError("tax_rate must be >= 0")
    sub = subtotal(items)
    return round(sub * (1 + tax_rate), 2)
