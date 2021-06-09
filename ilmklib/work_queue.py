#!/usr/bin/env python3

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

    def _is_out_of_date(self, item):

        # If we've already evaluated an object, we can exit immediately
        if item in self.out_of_date:
            assert not item in self.in_date
            return True

        if item in self.in_date:
            return False

        ts = self._get_ts(item)
        self.timestamps[item] = ts

        depends = set()
        ood = (ts == -1)
        for l_pred in self.g.get_direct_predecessors(item):
            if self._is_out_of_date(l_pred):
                # The predecessor is itself out of date. Add it to our list of
                # dependencies
                depends.add(l_pred)
            elif ts < self.timestamps[l_pred]:
                # The predecessor is not out-of-date itself but it is newer
                # than item, so item must be out-of-date.
                ood = True
            else:
                pass

        if depends:
            # Depends on things that are out of date
            self.out_of_date.add(item)
            self.depends[item] = depends
            return True
        elif ood:
            # The item doesn't depend on anything that is out-of-date, but is
            # itself out-of-date w.r.t its predecessors
            self.out_of_date.add(item)
            self.ready.add(item)
            return True
        else:
            # The item is in-date
            self.in_date.add(item)
            return False


    def __init__(self, graph, start, ts_rule_dict):

        self.start = start
        self.g = graph

        self.out_of_date = set()
        self.in_date = set()

        self.ready = set()
        self.inprogress = set()
        self.ts_rules = ts_rule_dict

        self.cond = Condition()
        self.error = False

        self.timestamps = {}
        self.depends = {}

        if not self._is_out_of_date(start):
            return

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


