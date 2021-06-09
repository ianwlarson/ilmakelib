import unittest

from ilmklib import UniqueStack

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

    def test_alternate_constructor(self):

        lst = [1,2,3,4,5]
        s = UniqueStack(lst)

        self.assertEqual(len(s), 5)
        self.assertIn(5, s)
        self.assertIn(4, s)
        self.assertIn(3, s)
        self.assertIn(2, s)
        self.assertIn(1, s)
        self.assertEqual(s.peek(), 5)
        self.assertEqual(s.pop(), 5)
        self.assertEqual(s.pop(), 4)
        self.assertEqual(s.pop(), 3)
        self.assertEqual(s.pop(), 2)
        self.assertEqual(s.pop(), 1)

        with self.assertRaises(Exception):
            s = UniqueStack(5)

