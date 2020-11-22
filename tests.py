import unittest
from contextlib import nullcontext
from myparser import process_expression

class TestProcessExpression(unittest.TestCase):
    def assert_raises_if_exception(self, expected_result):
        if expected_result == Exception:
            return self.assertRaises(Exception)
        else:
            return nullcontext()

    def test_parser(self):
        test_data = {
            "": {""},
            "abc": {"abc"},
            "{foo,bar}": {"foo", "bar"},
            "a{b,c}d": {"abd", "acd"},
            "{a,b}{c,d}": {"ac", "bc", "ad", "bd"},
            "a{b,{c,d}e}": {"ab", "ace", "ade"},
            "{a,b}{{c,d}{e,f}}": {"ace", "acf", "ade", "adf", "bce", "bcf", "bde", "bdf"},

            "{a,b,c}": {"a","b","c"},
            "a{b,c}": {"ab", "ac"},
            "{a}": {"a"},
            "a{b,c}d{e,f,g}": {"abde", "abdf", "abdg", "acde", "acdf", "acdg"},
            "a{b{xX{u,VvV},yY},c}":  {"abxXu", "abxXVvV", "abyY", "ac"},
            "z{a,b,c{d,e}}": {"za","zb", "zcd", "zce"},
            "}abc": Exception,
            "{abc": Exception,
            "}{": Exception,
            "{}": {""},
            "a,b,c": Exception,
            "{a{b,c}": Exception,
            "{a,}": {"", "a"}
        }
        for (expression, expected_result) in test_data.items():
            with self.subTest(expression=expression):
                result = None
                with self.assert_raises_if_exception(expected_result):
                    result = [*process_expression(expression)]

                if expected_result != Exception:
                    result_set = set(result)
                    self.assertEqual(len(result), len(result_set))
                    self.assertEqual(result_set, expected_result)

if __name__ == "__main__":
  unittest.main()
