import time
import collections

class TimedCache(collections.MutableMapping):
    """Makes a timed cache. Deletes cache after the time has expired.
    Parameters
    ----------
    seconds : int
        The seconds to cache the item for. Defaults to 10800 seconds or 3 hours
    """
    def __init__(self, seconds=10800):
        self._ttl = seconds
        self._data = {}

    def __getitem__(self, key):
        if key not in self._data:
            raise KeyError()
        item = self._data[key]
        if (time.time() - item[0]) < self._ttl:
            return item[1]
        else:
            del self._data[key]
            raise KeyError()

    def __setitem__(self, key, value) -> None:
        self._data[key] = (time.time(), value)

    def __delitem__(self, key):
        if key not in self._data:
            raise KeyError()
        item = self._data[key]
        del self._data[key]
        if (time.time() - item[0]) >= self._ttl:
            raise KeyError()

    def __contains__(self, key):
        if key not in self._data:
            return False
        item = self._data[key]
        if (time.time() - item[0]) < self._ttl:
            return True
        else:
            del self._ttl[key]
            return False

    def __len__(self) -> int:
        length = 0 
        now = time.time()
        keys_to_delete = []
        for key, value in self._data.items():
            if (now - value[0]) < self._ttl:
                length += 1
            else:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del self._data[key]

        return length

    def __iter__(self):
        keys_to_delete = []
        for key, value in self._data.items():
            if (time.time()- value[0]) < self._ttl:
                yield key
            else:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del self._data[key]