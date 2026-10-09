import unittest

from maxk import max_k_subarrays


class MaxKTest(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(max_k_subarrays([1, -2, 3, -1, 4], 1), 6)
        self.assertEqual(max_k_subarrays([1, -2, 3, -1, 4], 2), 7)
        self.assertEqual(max_k_subarrays([-5, -1], 3), 0)


if __name__ == "__main__":
    unittest.main()
