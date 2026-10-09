import unittest

from minire import search


class BasicTest(unittest.TestCase):
    def test_literal(self):
        self.assertEqual(search("abc", "xxabcxx"), ((2, 5), ()))
        self.assertIsNone(search("abd", "abc"))

    def test_star(self):
        self.assertEqual(search("a*", "aaab"), ((0, 3), ()))

    def test_group(self):
        self.assertEqual(search("(a)(b)?", "ac"), ((0, 1), ("a", None)))


if __name__ == "__main__":
    unittest.main()
