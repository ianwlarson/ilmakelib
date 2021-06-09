
import random
from collections.abc import Iterable
from collections import deque
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


