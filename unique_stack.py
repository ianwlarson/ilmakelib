import collections
import unittest

class UniqueStack:
    """
    A stack of unique objects. Uses a deque and a set internally to ensure that
    each item is properly placed.

    Methods
    -------

    push

    pop

    peek
    """

    def __init__(self, iterable=None):
        self.stack = collections.deque()
        self.stackset = set()
        if iterable:
            self.stack.extend(iterable)
            self.stackset.update(iterable)

        if len(self.stack) != len(self.stackset):
            raise Exception("Stack requires unique elements")

    def __len__(self):
        return len(self.stack)

    def __contains__(self, key):
        return key in self.stackset

    def pop(self):
        to_return = self.stack.pop()
        self.stackset.discard(to_return)
        return to_return

    def push(self, item):
        if item in self.stackset:
            raise Exception("Stack requires unique elements")

        self.stack.append(item)
        self.stackset.add(item)

    def peek(self):
        return self.stack[-1]


class TestUniqueStack(unittest.TestCase):

    def test_empty(self):

        s = UniqueStack()
        with self.assertRaises(IndexError):
            s.pop()
        with self.assertRaises(IndexError):
            s.peek()
        self.assertEqual(len(s), 0)

    def test_ordering(self):

        s = UniqueStack()

        s.push("a")
        s.push("b")
        s.push("c")

        self.assertEqual(len(s), 3)
        self.assertEqual(s.peek(), "c")
        self.assertEqual(s.pop(), "c")
        self.assertEqual(len(s), 2)
        self.assertEqual(s.peek(), "b")
        self.assertEqual(s.pop(), "b")
        self.assertEqual(len(s), 1)
        self.assertEqual(s.peek(), "a")
        self.assertEqual(s.pop(), "a")
        self.assertEqual(len(s), 0)

    def test_uniqueness(self):

        s = UniqueStack()

        s.push("a")
        self.assertTrue("a" in s)

        with self.assertRaises(Exception):
            s.push("a")

        with self.assertRaises(Exception):
            # 1 occurs twice in the iterable
            s = UniqueStack([1,2,3,4,5,6,7,8,9,1])

    def test_set_properties(self):

        s = UniqueStack()

        for i in range(9):
            s.push(i)

        for i in range(9):
            self.assertTrue(i in s)


if __name__ == "__main__":
    unittest.main()

