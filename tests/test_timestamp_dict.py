
import unittest
import time

from ilmklib import TimestampDict

class TestTimestampDict(unittest.TestCase):

    def test_basic(self):

        t = TimestampDict()

        t["abba"] = "1234"
        self.assertIn("abba", t)
        self.assertIn("tsd::/abba", t)
        self.assertEqual(t["abba"], "1234")

    def test_del(self):

        t = TimestampDict()
        t["abba"] = "1234"
        self.assertIn("abba", t)
        del t["abba"]
        self.assertNotIn("abba", t)

    def test_error(self):

        t = TimestampDict()
        with self.assertRaises(TypeError):
            t[123] = "123"
        with self.assertRaises(TypeError):
            t["123"] = 123
        with self.assertRaises(ValueError):
            t[""] = "123"

        with self.assertRaises(KeyError):
            a = t["abba"]

    def test_timestamping(self):

        t = TimestampDict()

        t["a"] = "123"
        time.sleep(0.2)
        t["b"] = "123"
        self.assertGreater(t.time("b"), t.time("a"))

        time.sleep(0.2)
        t["a"] = "456"

        self.assertGreater(t.time("a"), t.time("b"))

    def test_iterators(self):

        t = TimestampDict()
        t["a"] = ""
        t["b"] = ""
        t["c"] = ""
        seen = []
        for item in t:
            seen.append(item)

        self.assertEqual(sorted(["a", "b", "c"]), sorted(seen))


if __name__ == "__main__":

    unittest.main()


