#!/usr/bin/env python3
import unittest
from collections import deque
import time
import copy
from graph import Graph

class WorkQueue:

    def __init__(self, graph, start):
        # TODO: Add locking to the structure itself
        #

        self.start = start
        self.g = graph
        self.out_of_date = set()
        self.ready = set()
        self.inprogress = set()

        self.timestamps = {}
        # Get a timestamp on all elements in the tree
        start_ts = self.g[start](start)
        self.timestamps[start] = start_ts

        out_of_date = (start_ts == -1)

        # TODO: Get all the timestamps using a threadpoolexecutor
        for prereq in self.g.get_all_predecessors(start):

            prereq_ts = self.g[prereq](prereq)
            self.timestamps[prereq] = prereq_ts

            if prereq_ts == -1:
                out_of_date = True

            if prereq_ts > start_ts:
                out_of_date = True

        if not out_of_date:
            return

        # Check to see whether the elements are out of date or not
        for prereq in self.g.get_all_predecessors(start):

            if prereq in self.out_of_date:
                continue

            dps = self.g.get_direct_predecessors(prereq)
            prereq_age = self.timestamps[prereq]
            if (prereq_age == -1) or any(self.timestamps[x] > prereq_age for x in dps):
                self.out_of_date.add(prereq)

                # If something is out of date, mark all its successors as out
                # of date.
                stack = deque(self.g.get_direct_successors(prereq))
                while stack:
                    e = stack.popleft()
                    # Only recurse down the tree if the element is not already
                    # marked out of date. This prevents us from doing complete
                    # comprehensions of larger and larger subtrees that
                    # actually only contain 1 more element than a previously
                    # seen subtree.
                    if not e in self.out_of_date:
                        self.out_of_date.add(e)
                        stack.extend(self.g.get_direct_successors(e))

                #self.out_of_date.update(self.g.get_all_successors(prereq))

        # Go through all the elements that are out of date looking for elements
        # that have no predecessors who are out of date. This loop is probably
        # slow.
        for prereq in self.out_of_date:
            allp = self.g.get_all_predecessors(prereq)
            if not any(x in self.out_of_date for x in allp):
                self.ready.add(prereq)


    def ready_count(self):
        return len(self.ready)

    def done(self):
        return len(self.out_of_date) == 0 and len(self.ready) == 0 and len(self.inprogress) == 0

    def mark_done(self, name):

        assert name in self.timestamps

        # Update the timestamp for name
        new_ts = self.g[name](name)
        self.timestamps[name] = new_ts

        dps = self.g.get_direct_predecessors(name)
        if any(self.timestamps[x] > new_ts for x in dps):
            raise Exception(f"{name} was not updated!")

        self.out_of_date.remove(name)
        self.inprogress.remove(name)

        for item in self.g.get_direct_successors(name):

            # If item has already been touched
            if item in self.ready or item in self.inprogress:
                continue

            # If all the predecessors are done, we can add this object to the
            # ready queue
            allp = self.g.get_direct_predecessors(item)
            if not any(x in self.out_of_date for x in allp):
                self.ready.add(item)


    def get_item(self):
        if self.ready:
            o = self.ready.pop()
            self.inprogress.add(o)
        else:
            o = None
        return o

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

        g = Graph()
        g["foo"] = getfileage
        g["foo.o"] = getfileage
        g["foo.c"] = getfileage
        g["foo.h"] = getfileage

        # foo depends on foo.o which depends on both foo.c and foo.h
        g.add_edge("foo", "foo.o")
        g.add_edge("foo.o", "foo.c", "foo.h")

        w = WorkQueue(g, "foo")

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
