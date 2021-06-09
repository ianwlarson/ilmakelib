
import time

import os
import shutil
import os.path

class TimestampDict:

    def __init__(self, p_id=None):
        if not p_id:
            p_id = ""

        self.m_id = p_id
        self.m_full_prefix = f"tsd::{self.m_id}/"
        self.lookup = {}
        self.timestamps = {}


    def process_key(self, key):
        """
        Ensure that that tsd:: prefix doesn't get stuck
        """
        if not type(key) is str:
            return None

        if key.startswith("tsd::"):
            # If the key starts with `tsd::`, make sure it identifies this dictionary
            if not key.startswith(self.m_full_prefix):
                return None

            key = key[len(self.m_full_prefix):]

        return key

    def loadkeydir(self, dirname, overwrite=False):
        for fname in os.listdir(dirname):
            fpath = os.path.join(dirname, fname)
            if fname in self.lookup and not overwrite:
                continue

            with open(fpath) as f:
                t = f.read().rstrip()
                self.lookup[fname] = t
                self.timestamps[fname] = os.path.getmtime(fpath)

    def loadkey(self, dirname, key):
        pk = self.process_key(key)
        fpath = os.path.join(dirname, entry)
        if os.path.exists(fpath):
            with open(fpath) as f:
                t = f.read().rstrip()
                self.lookup[pk] = t
                self.timestamps[pk] = os.path.getmtime(fpath)
        else:
            raise KeyError(f"key {key} doesn't exist")


    def __contains__(self, key):
        pk = self.process_key(key)
        return pk in self.lookup

    def __getitem__(self, key):
        pk = self.process_key(key)
        return self.lookup[pk]

    def __setitem__(self, key, value):
        if not type(value) is str or not type(key) is str:
            raise TypeError(f"Passed non-string value or key")
        if key == "":
            raise ValueError("Passed empty string as key")

        pk = self.process_key(key)
        self.lookup[pk] = value
        self.timestamps[pk] = time.time()

    def items(self):
        return self.lookup.items()

    def __iter__(self):
        return iter(self.lookup)

    def __delitem__(self, instance):

        del self.lookup[instance]
        del self.timestamps[instance]

    def clear(self):
        self.lookup.clear()
        self.timestamps.clear()


    def touch(self, dirname, entry):
        pk = self.process_key(entry)
        fpath = os.path.join(dirname, pk)
        try:
            os.utime(fpath, None)
        except OSError:
            open(fpath, 'a').close()


    """
    def set(self, entry, value):
        if not type(entry) is str or not type(value) is str:
            raise ValueError("entry + value must be strings")

        pk = self.process_key(entry)
        fpath = os.path.join(self.bd, pk)
        with open(fpath, 'w') as f:
            f.write(value)

        self.lookup[entry] = value
        self.timestamps[entry] = os.path.getmtime(fpath)
    """

    def time(self, entry):

        pk = self.process_key(entry)
        o = self.timestamps[pk]
        return o

    def name(self, entry):
        return f"{self.m_full_prefix}{entry}"

    """

    def commit(self):
        for k, v in self.cache.items():
            fpath = os.path.join(self.bd, k)
            with open(fpath, 'w') as f:
                f.write(v)
    """

