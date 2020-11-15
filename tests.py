import unittest
from myparser import process_expression

class TestProcessExpression(unittest.TestCase):
    def test_parser(self):
        test_data = {
            "abc": {"abc"},
            "{foo,bar}": {"foo", "bar"},
            "a{b,c}d": {"abd", "acd"},
            "{a,b}{c,d}": {"ac", "bc", "ad", "bd"},
            "a{b,{c,d}e}": {"ab", "ace", "ade"},
            "{a,b}{{c,d}{e,f}}": {"ace", "acf", "ade", "adf", "bce", "bcf", "bde", "bdf"}
        }
        for (expression, expected_result) in test_data.items():
            with self.subTest(expression=expression):
                result = [*process_expression(expression)]
                result_set = set(result)
                self.assertEqual(len(result), len(result_set))
                self.assertEqual(result_set, expected_result)

if __name__ == "__main__":
  unittest.main()
