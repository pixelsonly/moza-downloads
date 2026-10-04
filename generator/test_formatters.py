import unittest

import formatters as fmt
import jseval


class FormatterTest(unittest.TestCase):
    def check(self, formatter, table):
        results = jseval.run([(formatter, inp) for inp, _ in table])
        self.assertEqual(results, [want for _, want in table])

    def test_gear(self):
        self.check(fmt.GEAR, [("0", "N"), ("3", "3"), ("-1", "R")])

    def test_pad2(self):
        self.check(fmt.PAD2, [("5", "05"), ("12", "12"), ("0", "00"), ("NaN", "--")])

    def test_int(self):
        self.check(fmt.INT, [("4", "4"), ("3650.6", "3651"), ("NaN", "-")])

    def test_delta(self):
        self.check(fmt.DELTA, [("-0.156", "-0.156"), ("1.2041", "+1.204"), ("0", "0.000"), ("NaN", "-.---")])

    def test_laptime(self):
        self.check(fmt.LAPTIME, [("74.033", "1:14.033"), ("59.9996", "1:00.000"), ("125.5", "2:05.500"),
                                 ("NaN", "-:--.---"), ("-3.4028234e+38", "-:--.---")])

    def test_name(self):
        self.check(fmt.NAME, [("'r.lindsey'", "R.LINDSEY"), ("null", "")])

    def test_bias(self):
        self.check(fmt.BIAS, [("54.5", "54.5"), ("0.545", "54.5"), ("NaN", "--.-")])


if __name__ == "__main__":
    unittest.main()
