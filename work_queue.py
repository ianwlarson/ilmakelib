#!/usr/bin/env python3
import unittest
from collections import deque
from threading import Condition
from concurrent.futures import ThreadPoolExecutor
import time
import copy

from .graph import Graph

class WorkQueue:


    def raises_on_error(func):
        def error_check(self, *args, **kwargs):
            with self.cond:
                if self.error:
                    raise RuntimeError()

            return func(self, *args, *kwargs)

        return error_check

    def _get_ts(self, item):

        item_type = self.g[item]
        ts_func = self.ts_rules[item_type]
        return ts_func(item)

    def __init__(self, graph, start, ts_rule_dict):
        # TODO: Add locking to the structure itself
        #

        self.start = start
        self.g = graph
        self.out_of_date = set()
        self.ready = set()
        self.inprogress = set()
        self.ts_rules = ts_rule_dict

        self.cond = Condition()
        self.error = False

        self.timestamps = {}
        self.depends = {}

        self.depends[start] = set(self.g.get_direct_predecessors(start))

        # Get a timestamp on all elements in the tree
        self.timestamps[start] = self._get_ts(start)

        # TODO: See if using a ThreadPoolExecutor to get all the timestamps
        # speeds anything up. I don't think it does because the timestamping
        # function is usually just calling os.path.getmtime, which (probably)
        # doesn't release the GIL.
        for prereq in self.g.get_all_predecessors(start):

            self.timestamps[prereq] = self._get_ts(prereq)
            self.depends[prereq] = set(self.g.get_direct_predecessors(prereq))


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
            else:
                # The entry is not out of date!
                for l_succ in self.g.get_direct_successors(prereq):
                    self.depends[l_succ].remove(prereq)


        # Go through all the elements that are out of date looking for elements
        # that have no predecessors who are out of date. This loop is probably
        # slow.
        for prereq in self.out_of_date:

            # If the prerequisite no longer depends on anything, add it to the
            # ready queue.
            if not self.depends[prereq]:
                self.ready.add(prereq)


    def ready_count(self):
        with self.cond:
            return len(self.ready)

    def done(self):
        with self.cond:
            no_more_work = (len(self.out_of_date) == 0) and (len(self.ready) == 0) and (len(self.inprogress) == 0)
            return no_more_work or self.error

    @raises_on_error
    def mark_done(self, name):
        with self.cond:

            assert name in self.timestamps

            # Update the timestamp for name
            new_ts = self._get_ts(name)
            self.timestamps[name] = new_ts

            dps = self.g.get_direct_predecessors(name)
            if any(self.timestamps[x] > new_ts for x in dps):
                raise Exception(f"{name} was not updated!")

            self.out_of_date.remove(name)
            self.inprogress.remove(name)

            for item in self.g.get_direct_successors(name):

                # Remove name from all of its direct successor's dependencies
                # and if there are no dependencies remaining, add it to the
                # ready queue.
                self.depends[item].remove(name)
                if not self.depends[item]:
                    self.ready.add(item)

            if self.done():
                self.cond.notify_all()
            else:
                self.cond.notify(self.ready_count())

    def mark_error(self):
        with self.cond:
            self.error = True
            self.cond.notify_all()

    @raises_on_error
    def get_item(self, wait=False):
        with self.cond:
            # If there will never be items, return None
            if self.done():
                return None

            if wait:
                # If we are waiting and there are no items, wait to be signalled
                if not self.ready:
                    self.cond.wait_for(lambda:self.done() or self.ready_count() > 0)

                # If we were awoken after the work queue was complete, return None
                if self.done():
                    return None

                assert self.ready

            if self.ready:
                o = self.ready.pop()
                self.inprogress.add(o)
            else:
                o = None

            return o


from enum import Enum, auto

class TestWorkQueue(unittest.TestCase):

    class wType(Enum):
        wFILE = auto()
        wDIRECTORY = auto()

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
        g["foo"] = getfileage
        g["foo.o"] = getfileage
        g["foo.c"] = getfileage
        g["foo.h"] = getfileage

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
