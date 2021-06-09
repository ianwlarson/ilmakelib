
import random
from collections.abc import Iterable
from collections import deque
import unittest
from .unique_stack import UniqueStack


class Vertex:

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.successors = set()
        self.predecessors = set()

    def add_edge_to(self, other):
        self.successors.add(other.key)
        other.predecessors.add(self.key)


class Graph:

    def __init__(self):

        self.direct_cyclic = False
        self.vertices = {}
        self.leaf_nodes = set()
        self.root_nodes = set()

    def __len__(self):
        return len(self.vertices)

    def __contains__(self, key):
        return key in self.vertices

    def __getitem__(self, key):
        return self.vertices[key].value

    def __setitem__(self, key, value):
        self.add_vertex(key, value)

    def items(self):
        for k, v in self.vertices.items():
            yield (k, v.value)

    def add_vertex(self, key, value=None):
        if key in self.vertices:
            raise Exception(f"{key} already in graph")

        self.vertices[key] = Vertex(key, value)
        self.leaf_nodes.add(key)
        self.root_nodes.add(key)

    def add_edge(self, dst, *srcs):
        if dst not in self.vertices:
            raise Exception(f"{dst} not present in graph.")

        for src in srcs:

            if src not in self.vertices:
                raise Exception(f"{src} not present in graph.")

            # TODO: Change this to allow variadic sources
            if src == dst:
                self.direct_cyclic = True

            self.vertices[src].add_edge_to(self.vertices[dst])
            self.leaf_nodes.discard(dst)
            self.root_nodes.discard(src)

    def add_edges(self, dst, src_list):

        if not type(src_list) is list:
            raise TypeError("Add edges must be passed a list")

        for src in src_list:
            # TODO: Change this function to only take lists.
            self.add_edge(dst, src)


    def get_all_successors(self, key):

        seen = set(key)

        stack = deque(self.get_direct_successors(key))

        while stack:
            elem = stack.popleft()
            if not elem in seen:
                seen.add(elem)
                stack.extend(self.get_direct_successors(elem))
                yield elem


    def get_direct_successors(self, key):

        return iter(self.vertices[key].successors)


    def get_direct_predecessors(self, key):

        return iter(self.vertices[key].predecessors)


    def get_all_predecessors(self, key):

        seen = set(key)

        stack = deque(self.get_direct_predecessors(key))

        while stack:
            # Pop from the right side so we find nodes with the greatest
            # distance from key first. This optimizes some work_queue code.
            elem = stack.pop()
            if not elem in seen:
                seen.add(elem)
                stack.extend(self.get_direct_predecessors(elem))
                yield elem

    def tarjans(self, use_rng=False):

        node_st = {}
        idx = 0
        stack = UniqueStack()
        scc_list = []

        def strongconnect(v):
            nonlocal node_st
            nonlocal idx
            nonlocal stack
            nonlocal scc_list
            node_st[v] = (idx, idx)
            idx += 1
            stack.push(v)

            for w in self.vertices[v].successors:
                if not w in node_st:
                    strongconnect(w)
                    v_idx, v_ll = node_st[v]
                    w_idx, w_ll = node_st[w]
                    node_st[v] = (v_idx, min(v_ll, w_ll))
                else:
                    if w in stack:
                        v_idx, v_ll = node_st[v]
                        w_idx, w_ll = node_st[w]
                        node_st[v] = (v_idx, min(v_ll, w_idx))

            v_idx, v_ll = node_st[v]
            if v_idx == v_ll:
                scc = []
                while True:
                    w = stack.pop()
                    scc.append(w)
                    if w == v:
                        break
                scc_list.append(scc)

        elems = list(self.vertices.keys())
        if use_rng:
            random.shuffle(elems)

        for e in elems:
            if not e in node_st:
                strongconnect(e)

        return scc_list

    # Use Tarjan's Strongly connected components algorithm
    def is_cyclic(self, use_rng=False):

        if self.direct_cyclic:
            return True

        return len(self.tarjans(use_rng)) != len(self.vertices)


class TestGraph(unittest.TestCase):

    def test_simple_errors(self):

        g = Graph()

        self.assertFalse(g.is_cyclic())

        g.add_vertex("a")


        with self.assertRaises(Exception):
            g.add_vertex("a")

        self.assertFalse(g.is_cyclic())

        g.add_edge("a", "a")
        self.assertTrue(g.is_cyclic())

        g = Graph()
        self.assertEqual(len(g), 0)
        g.add_vertex("a")
        self.assertEqual(len(g), 1)

        self.assertTrue("a" in g)

        with self.assertRaises(Exception):
            # Try to add an edge with a dst that isn't in the graph
            g.add_edge("d", "a")

        with self.assertRaises(Exception):
            # Try to add an edge with a src that isn't in the graph
            g.add_edge("a", "d")


    def test_simple_cyclic(self):

        g = Graph()
        g.add_vertex("a")
        g.add_vertex("b")
        g.add_vertex("c")

        g.add_edge("b", "a")
        g.add_edge("c", "b")
        g.add_edge("a", "c")

        self.assertTrue(g.is_cyclic())

    def test_get_items(self):
        """
        Test that the items function iterates over the entire set of vertices
        """

        g = Graph()
        g.add_vertex("a")
        g.add_vertex("b")
        g.add_vertex("c")

        seen = []
        for k, v in g.items():
            seen.append(k)

        self.assertEqual(sorted(seen), sorted(["a", "b", "c"]))

    def test_complicated_cyclic(self):
        """ Create a tree structure where each node points to its own numerical
        value divided by 2 (as an int)
        e.g. 1 has an edge to 0
             2 and 3 have an edge to 1
             4 and 5 have an edge to 2
             etc.
        """

        g = Graph()
        for i in range(100):
            g.add_vertex(i)

        for i in range(100):
            if i == 0:
                continue
            o = int(i / 2)
            g.add_edge(o, i)

        self.assertFalse(g.is_cyclic())

        # add in an edge from 1 to 99 and ensure that the cycle is detected
        # (99 -> 49 -> 24 -> 12 -> 6 -> 3 -> 1 -> 99)
        g.add_edge(99, 1)

        # The whole graph should be deterministically cyclic
        for i in range(100):
            self.assertTrue(g.is_cyclic(True))

    def test_complicated_disconnected_cyclic(self):
        """ Create a tree structure where each node points to its own numerical
        value divided by 2 (as an int)
        e.g. 1 has an edge to 0
             2 and 3 have an edge to 1
             4 and 5 have an edge to 2
             etc.
        """

        g = Graph()
        for i in range(100):
            g.add_vertex(i)

        for i in range(1, 100):
            o = int(i / 2)
            g.add_edge(o, i)

        self.assertFalse(g.is_cyclic(True))

        # Create a small cycle of 3 vertices
        g.add_vertex("a")
        g.add_vertex("b")
        g.add_vertex("c")

        g.add_edge("b", "a")
        g.add_edge("c", "b")
        g.add_edge("a", "c")

        # The whole graph should be deterministically cyclic
        for i in range(100):
            self.assertTrue(g.is_cyclic(True))

    def test_disconnected_cyclic(self):

        g = Graph()
        g.add_vertex("a")
        g.add_vertex("b")
        g.add_vertex("c")

        g.add_vertex("e")
        g.add_vertex("f")
        g.add_vertex("g")

        # a -> b -> c -> a is a cyclic graph
        g.add_edge("b", "a")
        g.add_edge("c", "b")
        g.add_edge("a", "c")

        # e -> f -> g is not cyclic, but is disconnected
        g.add_edge("f", "e")
        g.add_edge("g", "f")

        # The whole graph should be deterministically cyclic
        for i in range(100):
            self.assertTrue(g.is_cyclic(True))

    def test_c_source(self):

        g = Graph()
        g.add_vertex("source1.c")
        g.add_vertex("source2.c")
        g.add_vertex("source3.c")

        g.add_vertex("header1.h")
        g.add_vertex("header2.h")
        g.add_vertex("header3.h")

        g.add_vertex("common1.h")
        g.add_vertex("common2.h")

        g.add_vertex("source1.o")
        g.add_vertex("source2.o")
        g.add_vertex("source3.o")

        g.add_vertex("binary")

        g.add_edge("source1.o", "source1.c")
        g.add_edge("source2.o", "source2.c")
        g.add_edge("source3.o", "source3.c")

        g.add_edge("source1.o", "header1.h")
        g.add_edge("source2.o", "header2.h")
        g.add_edge("source3.o", "header3.h")

        g.add_edge("source1.o", "common1.h")
        g.add_edge("source2.o", "common1.h")

        g.add_edge("source2.o", "common2.h")
        g.add_edge("source3.o", "common2.h")

        g.add_edge("binary", "source1.o")
        g.add_edge("binary", "source2.o")
        g.add_edge("binary", "source3.o")

        self.assertFalse(g.is_cyclic())

        deps = list(g.get_direct_predecessors("binary"))
        self.assertEqual(len(deps), 3)
        self.assertIn("source1.o", deps)
        self.assertIn("source2.o", deps)
        self.assertIn("source3.o", deps)

        deps = list(g.get_direct_successors("common1.h"))
        self.assertEqual(len(deps), 2)
        self.assertIn("source1.o", deps)
        self.assertIn("source2.o", deps)

        deps = list(g.get_all_predecessors("source2.o"))
        self.assertEqual(len(deps), 4)
        self.assertIn("source2.c", deps)
        self.assertIn("header2.h", deps)
        self.assertIn("common1.h", deps)
        self.assertIn("common2.h", deps)

        deps = list(g.get_all_successors("common1.h"))
        self.assertEqual(len(deps), 3)
        self.assertIn("source1.o", deps)
        self.assertIn("source2.o", deps)
        self.assertIn("binary", deps)

    def test_multi_cyclic(self):

        g = Graph()
        g.add_vertex("a")
        g.add_vertex("b")
        g.add_vertex("c")
        g.add_vertex("d")
        g.add_vertex("e")
        g.add_vertex("f")
        g.add_vertex("g")
        g.add_vertex("h")
        g.add_vertex("i")
        g.add_vertex("j")
        """
             a   e   h      |
            / \ / \ / \     |
           d   b   f   i    |
            \ / \ / \ /     |
             c   g   j      |
        """
        # a -> b -> c -> d -> a
        g.add_edge("b", "a")
        g.add_edge("c", "b")
        g.add_edge("d", "c")
        g.add_edge("a", "d")

        # e -> b -> g -> f -> e
        g.add_edge("b", "e")
        g.add_edge("g", "b")
        g.add_edge("f", "g")
        g.add_edge("e", "f")

        # h -> f -> j -> i -> h
        g.add_edge("f", "h")
        g.add_edge("h", "i")
        g.add_edge("i", "j")
        g.add_edge("j", "f")

        for i in range(100):
            self.assertTrue(g.is_cyclic(True))

    def test_alternate_api(self):

        g = Graph()
        g.add_vertex("a")
        g.add_vertex("b")
        g.add_vertex("c")
        g.add_vertex("d")
        g.add_vertex("e")
        g.add_vertex("f")
        g.add_vertex("g")

        g.add_edge("a", "b", "c", "d", "e", "f")
        deps = list(g.get_direct_predecessors("a"))
        self.assertIn("b", deps)
        self.assertIn("c", deps)
        self.assertIn("d", deps)
        self.assertIn("e", deps)
        self.assertIn("f", deps)

        g = Graph()
        g.add_vertex("a")
        g.add_vertex("b")
        g.add_vertex("c")
        g.add_vertex("d")
        g.add_vertex("e")
        g.add_vertex("f")
        g.add_vertex("g")

        g.add_edges("a", ["b", "c", "d", "e", "f"])
        deps = list(g.get_direct_predecessors("a"))
        self.assertIn("b", deps)
        self.assertIn("c", deps)
        self.assertIn("d", deps)
        self.assertIn("e", deps)
        self.assertIn("f", deps)

        with self.assertRaises(TypeError):
            g.add_edges("a", "b")

    def test_reaching_recursion_depth(self):
        g = Graph()
        for i in range(2000):
            g.add_vertex(i)

        for i in range(1, 2000):
            g.add_edge(i-1, i)

        with self.assertRaises(RecursionError):
            for i in range(100):
                g.is_cyclic(True)


if __name__ == "__main__":
    unittest.main()

