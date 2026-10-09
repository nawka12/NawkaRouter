import unittest

from shop.pricing import order_total, subtotal


class PricingTest(unittest.TestCase):
    def test_subtotal(self):
        self.assertEqual(subtotal([(2.5, 4), (1, 3)]), 13)

    def test_total_with_tax(self):
        self.assertEqual(order_total([(10, 2)], tax_rate=0.08), 21.6)

    def test_negative_tax(self):
        with self.assertRaises(ValueError):
            order_total([(1, 1)], tax_rate=-0.1)


if __name__ == "__main__":
    unittest.main()
