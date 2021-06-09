
import unittest
from ilmklib import WorkQueue, Graph
from enum import Enum, auto

class wType(Enum):
    wFILE = auto()
    wDIRECTORY = auto()

class TestWorkQueue(unittest.TestCase):


    """
    def test_base(self):

        g = Graph()
        g["a"] = lambda x: 1
        g["b"] = lambda x: 2
        g["c"] = lambda x: 3

        g.add_edge("a", "b")
        g.add_edge("b", "c")

        w = WorkQueue(g)

        for x in w.process("a"):
            #print(x)
            pass
    """

    def test_c_simulation(self):

        # foo is older than foo.c, foo.o doesn't exist, and foo.h has been modified recently
        files = {
            "foo" : 7,
            "foo.c" : 5,
            "foo.h" : 10
        }

        def getfileage(name):
            nonlocal files
            if name in files:
                return files[name]
            else:
                # Files that don't exist are very old
                return 0

        func_dict = { wType.wFILE : getfileage }

        g = Graph()
        g["foo"] = wType.wFILE
        g["foo.o"] = wType.wFILE
        g["foo.c"] = wType.wFILE
        g["foo.h"] = wType.wFILE

        # foo depends on foo.o which depends on both foo.c and foo.h
        g.add_edge("foo", "foo.o")
        g.add_edge("foo.o", "foo.c", "foo.h")

        w = WorkQueue(g, "foo", func_dict)

        item = w.get_item()
        self.assertEqual(item, "foo.o")
        files["foo.o"] = 11;
        w.mark_done(item)
        item = w.get_item()
        self.assertEqual(item, "foo")
        files["foo"] = 11;
        w.mark_done(item)
        item = w.get_item()
        self.assertEqual(item, None)


    def test_invalid_object(self):

        with self.assertRaises(TypeError):

            w = WorkQueue("abba")

if __name__ == "__main__":

    unittest.main()
