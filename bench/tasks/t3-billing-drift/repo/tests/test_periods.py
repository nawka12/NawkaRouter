import unittest
from datetime import date

from billing.periods import billing_periods


class PeriodsTest(unittest.TestCase):
    def test_mid_month_signup(self):
        p = billing_periods(date(2025, 3, 15), date(2025, 5, 1))
        self.assertEqual(p[0], (date(2025, 3, 15), date(2025, 4, 14)))
        self.assertEqual(p[1], (date(2025, 4, 15), date(2025, 5, 14)))

    def test_signup_on_31st(self):
        p = billing_periods(date(2025, 1, 31), date(2025, 4, 1))
        starts = [s for s, _ in p]
        self.assertEqual(starts, [date(2025, 1, 31), date(2025, 2, 28), date(2025, 3, 31)])
        self.assertEqual(p[1], (date(2025, 2, 28), date(2025, 3, 30)))


if __name__ == "__main__":
    unittest.main()
