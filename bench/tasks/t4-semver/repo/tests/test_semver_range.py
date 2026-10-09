import unittest

from semver_range import satisfies


class BasicTest(unittest.TestCase):
    def test_exact(self):
        self.assertTrue(satisfies("1.2.3", "1.2.3"))
        self.assertFalse(satisfies("1.2.4", "1.2.3"))

    def test_comparators(self):
        self.assertTrue(satisfies("1.2.4", ">1.2.3"))
        self.assertTrue(satisfies("1.2.9", ">=1.2.3 <1.3.0"))

    def test_caret(self):
        self.assertTrue(satisfies("1.9.9", "^1.2.3"))
        self.assertFalse(satisfies("2.0.0", "^1.2.3"))


if __name__ == "__main__":
    unittest.main()
