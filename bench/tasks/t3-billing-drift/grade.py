import io, json, sys, unittest
from datetime import date

sys.path.insert(0, sys.argv[1])
from billing.periods import billing_periods, next_renewal, prorate  # noqa: E402


def starts(signup, end):
    return [s for s, _ in billing_periods(signup, end)]


class Hidden(unittest.TestCase):
    def test_periods_31st(self):
        self.assertEqual(starts(date(2025, 1, 31), date(2025, 6, 1)),
                         [date(2025, 1, 31), date(2025, 2, 28), date(2025, 3, 31),
                          date(2025, 4, 30), date(2025, 5, 31)])

    def test_periods_inclusive_end(self):
        p = billing_periods(date(2025, 1, 31), date(2025, 4, 1))
        self.assertEqual(p[1], (date(2025, 2, 28), date(2025, 3, 30)))
        self.assertEqual(p[2], (date(2025, 3, 31), date(2025, 4, 29)))

    def test_periods_30th(self):
        self.assertEqual(starts(date(2025, 1, 30), date(2025, 4, 1)),
                         [date(2025, 1, 30), date(2025, 2, 28), date(2025, 3, 30)])

    def test_leap_year(self):
        self.assertEqual(starts(date(2024, 1, 31), date(2024, 3, 31)),
                         [date(2024, 1, 31), date(2024, 2, 29), date(2024, 3, 31)])

    def test_feb29_signup(self):
        s = starts(date(2024, 2, 29), date(2025, 3, 1))
        self.assertEqual(s[1], date(2024, 3, 29))
        self.assertEqual(s[12], date(2025, 2, 28))
        self.assertEqual(s[-1], date(2025, 2, 28))

    def test_year_boundary(self):
        self.assertEqual(starts(date(2024, 12, 31), date(2025, 3, 1)),
                         [date(2024, 12, 31), date(2025, 1, 31), date(2025, 2, 28)])

    def test_mid_month_unchanged(self):
        self.assertEqual(starts(date(2025, 3, 15), date(2025, 5, 20)),
                         [date(2025, 3, 15), date(2025, 4, 15), date(2025, 5, 15)])

    def test_next_renewal_after_short_month(self):
        self.assertEqual(next_renewal(date(2025, 1, 31), date(2025, 3, 1)), date(2025, 3, 31))

    def test_next_renewal_far(self):
        self.assertEqual(next_renewal(date(2025, 1, 31), date(2025, 7, 31)), date(2025, 8, 31))

    def test_next_renewal_mid_month(self):
        self.assertEqual(next_renewal(date(2025, 1, 10), date(2025, 1, 10)), date(2025, 2, 10))

    def test_prorate_after_drift(self):
        # period Mar 31 -> Apr 30 (30 days); change on Apr 15 leaves 15 days
        self.assertEqual(prorate(30.0, date(2025, 1, 31), date(2025, 4, 15)), 15.0)

    def test_prorate_simple(self):
        # period Jan 10 -> Feb 10 (31 days); change on Jan 20 leaves 21 days
        self.assertEqual(prorate(31.0, date(2025, 1, 10), date(2025, 1, 20)), 21.0)


r = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(Hidden))
print(json.dumps({"passed": r.testsRun - len(r.failures) - len(r.errors), "total": r.testsRun,
                  "fails": [str(t[0]).split()[0] for t in r.failures + r.errors]}))
