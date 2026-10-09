import contextlib, io, json, os, sys, tempfile, unittest

sys.path.insert(0, sys.argv[1])
from shop.pricing import order_total  # noqa: E402
from shop import cli  # noqa: E402


def run_cli(*args):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"items": [[19.99, 3], [5, 2]]}, f)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        cli.main([f.name, *args])
    os.unlink(f.name)
    return out.getvalue().strip()


class Hidden(unittest.TestCase):
    def test_default_unchanged(self):
        self.assertEqual(order_total([(10, 2)], tax_rate=0.08), 21.6)

    def test_discount_before_tax(self):
        self.assertEqual(order_total([(10, 2)], tax_rate=0.1, discount_pct=10), 19.8)

    def test_fractional_discount(self):
        self.assertEqual(order_total([(80, 1)], discount_pct=12.5), 70.0)

    def test_full_discount(self):
        self.assertEqual(order_total([(10, 2)], tax_rate=0.1, discount_pct=100), 0.0)

    def test_zero_discount(self):
        self.assertEqual(order_total([(10, 2)], discount_pct=0), 20.0)

    def test_out_of_range(self):
        for bad in (-0.01, 100.5, 150):
            with self.assertRaises(ValueError):
                order_total([(1, 1)], discount_pct=bad)

    def test_cli_discount(self):
        # (59.97 + 10) * 0.75 * 1.08 = 56.6757 -> 56.68
        self.assertEqual(run_cli("--tax", "0.08", "--discount", "25"), "56.68")

    def test_cli_default(self):
        self.assertEqual(run_cli("--tax", "0.08"), "75.57")


r = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(Hidden))
print(json.dumps({"passed": r.testsRun - len(r.failures) - len(r.errors), "total": r.testsRun,
                  "fails": [str(t[0]).split()[0] for t in r.failures + r.errors]}))
