
import unittest
import time

import os
import shutil
import os.path

class FrozenTimestampDict:

    def __init__(self, basedir):
        currdir = os.getcwd()
        resolved = os.path.abspath(os.path.join(os.getcwd(), basedir))
        common = os.path.commonpath([currdir, resolved])
        if common != currdir:
            raise ValueError("basedir appears to resolve to above cwd")

        if not os.path.exists(basedir):
            raise RuntimeError(f"{basedir} does not exist")

        self.bd = basedir

    def __len__(self):
        return len(os.listdir(self.bd))

    def __contains__(self, key):
        if not type(key) is str:
            return False

        if key.startswith("tsd::"):
            key = key[len("tsd::"):]

        dn = os.path.dirname(key)
        if dn and dn != self.bd:
            return False
        key = os.path.basename(key)

        return key in os.listdir(self.bd)

    def __getitem__(self, key):
        fname = os.path.join(self.bd, key)
        try:
            f = open(fname)
            o = f.read()
            f.close()
        except OSError:
            raise KeyError(f"{key} does not exist")

        return o

    def items(self):
        for e in os.listdir(self.bd):
            yield (e, self[e])

    def __iter__(self):
        return iter(os.listdir(self.bd))

    def name(self, entry):
        return f"tsd::{os.path.join(self.bd, entry)}"

    def get_timestamp(self, entry):
        fpath = os.path.join(self.bd, entry)
        if not os.path.exists(fpath):
            return -1
        else:
            return os.path.getmtime(fpath)

class TimestampDict(FrozenTimestampDict):

    def __init__(self, basedir):
        currdir = os.getcwd()
        resolved = os.path.abspath(os.path.join(os.getcwd(), basedir))
        common = os.path.commonpath([currdir, resolved])
        if common != currdir:
            raise ValueError("basedir appears to resolve to above cwd")

        if not os.path.exists(basedir):
            os.makedirs(basedir)

        self.bd = basedir

    def __setitem__(self, key, value):
        if not type(value) is str or not type(key) is str:
            raise TypeError(f"Passed non-string value or key")
        if key == "":
            raise ValueError("Passed empty string as key")

        fname = os.path.join(self.bd, key)
        with open(fname, 'w') as f:
            f.write(value)

    def empty(self):
        for fname in os.listdir(self.bd):
            fpath = os.path.join(self.bd, fname)
            if os.path.isfile(fpath):
                os.unlink(fpath)
            else:
                raise Exception(f"unknown file type in target dict {fpath}")

    def rm(self, entry=None):
        if not entry and os.path.exists(self.bd):
            shutil.rmtree(self.bd)
        else:
            self.clean([entry])

    def clean(self, entries):
        if not type(entries) == list:
            raise ValueError("Clean passed non-list")

        for name in entries:
            fpath = os.path.join(self.bd, fname)
            if not os.path.exists(fpath):
                continue

            if os.path.isfile(fpath):
                os.unlink(fpath)
            else:
                raise Exception(f"Found non file {fpath}")

    def touch(self, entry):
        fpath = os.path.join(self.bd, entry)
        try:
            os.utime(fpath, None)
        except OSError:
            open(fpath, 'a').close()

def get_tsd_ts(tsd):
    return lambda x: tsd.get_timestamp(x)

class TestTimestampDict(unittest.TestCase):

    def test_basic(self):

        t = TimestampDict(".vardir")
        t.empty()

        t["abba"] = "1234"
        self.assertIn("abba", t)
        self.assertIn(".vardir/abba", t)
        self.assertIn("tsd::.vardir/abba", t)
        self.assertIn("tsd::abba", t)
        self.assertEqual(t["abba"], "1234")
        t.rm()

    def test_error(self):

        with self.assertRaises(ValueError):
            t = TimestampDict("../../../below")

        t = TimestampDict(".vardir")
        with self.assertRaises(TypeError):
            t[123] = "123"
        with self.assertRaises(TypeError):
            t["123"] = 123
        with self.assertRaises(ValueError):
            t[""] = "123"

        with self.assertRaises(KeyError):
            a = t["abba"]

        t.rm()

        with self.assertRaises(RuntimeError):
            t = FrozenTimestampDict(".vardir")

    def test_frozen(self):

        t = TimestampDict(".ok")
        t["123"] = "123"
        f = FrozenTimestampDict(".ok")
        self.assertEqual(f["123"], "123")

        with self.assertRaises(TypeError):
            f["123"] = "abba"

        with self.assertRaises(AttributeError):
            f.rm()
        with self.assertRaises(AttributeError):
            f.clear("123")
        with self.assertRaises(AttributeError):
            f.empty()
        with self.assertRaises(AttributeError):
            f.touch("123")

        t.rm()

    def test_touch(self):

        t = TimestampDict(".vardir")

        t["a"] = "123"
        time.sleep(0.2)
        t["b"] = "123"
        self.assertGreater(t.get_timestamp("b"), t.get_timestamp("a"))

        time.sleep(0.2)
        t.touch("a")

        self.assertGreater(t.get_timestamp("a"), t.get_timestamp("b"))

        t.rm()

    def test_iterators(self):

        t = TimestampDict(".vardir")
        t["a"] = ""
        t["b"] = ""
        t["c"] = ""
        seen = []
        for item in t:
            seen.append(item)

        self.assertEqual(sorted(["a", "b", "c"]), sorted(seen))

        t.rm()


if __name__ == "__main__":

    unittest.main()


