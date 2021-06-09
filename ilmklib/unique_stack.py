from collections import deque

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
        self.stack = deque()
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

