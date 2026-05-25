from dataclasses import dataclass
from typing import Iterator


@dataclass
class _Entry[K, V]:
    key: K
    value: V
    next: "_Entry[K, V] | None" = None
class ChainedHashMap[K, V]:
    LOAD_FACTOR_MAX = 0.75

    def __init__(self, initial_capacity: int = 8) -> None:
        self._capacity = initial_capacity
        self._slots: list[_Entry[K, V] | None] = [None] * initial_capacity
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def _hash(self, key: K) -> int:
        return hash(key) % self._capacity
    def __setitem__(self, key: K, value: V) -> None:
        slot = self._hash(key)
        cur = self._slots[slot]
        while cur is not None:
            if cur.key == key:
                cur.value = value
                return
            cur = cur.next
        self._slots[slot] = _Entry(key, value, self._slots[slot])
        self._size += 1
        if self._size > self._capacity * self.LOAD_FACTOR_MAX:
            self._resize(self._capacity * 2)
    def __getitem__(self, key: K) -> V:
        cur = self._slots[self._hash(key)]
        while cur is not None:
            if cur.key == key:
                return cur.value
            cur = cur.next
        raise KeyError(key)

    def __contains__(self, key: K) -> bool:
        cur = self._slots[self._hash(key)]
        while cur is not None:
            if cur.key == key:
                return True
            cur = cur.next
        return False
    def __delitem__(self, key: K) -> None:
        slot = self._hash(key)
        cur = self._slots[slot]
        prev: _Entry[K, V] | None = None
        while cur is not None:
            if cur.key == key:
                if prev is None:
                    self._slots[slot] = cur.next
                else:
                    prev.next = cur.next
                self._size -= 1
                return
            prev = cur
            cur = cur.next
        raise KeyError(key)
    def __iter__(self) -> Iterator[K]:
        for head in self._slots:
            cur = head
            while cur is not None:
                yield cur.key
                cur = cur.next
    def _resize(self, new_capacity: int) -> None:
        old_slots = self._slots
        self._capacity = new_capacity
        self._slots = [None] * new_capacity
        self._size = 0
        for head in old_slots:
            cur = head
            while cur is not None:
                self[cur.key] = cur.value
                cur = cur.next
def linear_probe(h1: int, h2: int, i: int, capacity: int) -> int:
    return (h1 + i) % capacity


def quadratic_probe(h1: int, h2: int, i: int, capacity: int) -> int:
    return (h1 + i * i) % capacity


def double_hash_probe(h1: int, h2: int, i: int, capacity: int) -> int:
    return (h1 + i * h2) % capacity
from typing import Callable

_TOMBSTONE = object()
Probe = Callable[[int, int, int, int], int]
class OpenAddressedHashMap[K, V]:
    LOAD_FACTOR_MAX = 0.5  # tighter than chaining — open addressing degrades faster

    def __init__(self, initial_capacity: int = 8, probe: Probe = linear_probe) -> None:
        self._capacity = initial_capacity
        self._slots: list[tuple[K, V] | object | None] = [None] * initial_capacity
        self._size = 0
        self._probe = probe

    def __len__(self) -> int:
        return self._size

    def _hashes(self, key: K) -> tuple[int, int]:
        h1 = hash(key) % self._capacity
        # second hash must be odd so it's coprime to a power-of-2 capacity
        h2 = hash((key, "salt")) | 1
        return h1, h2
    def _find_slot(self, key: K) -> tuple[int, bool]:
        h1, h2 = self._hashes(key)
        first_tomb = -1
        for i in range(self._capacity):
            slot = self._probe(h1, h2, i, self._capacity)
            entry = self._slots[slot]
            if entry is None:
                return (first_tomb if first_tomb >= 0 else slot), False
            if entry is _TOMBSTONE:
                if first_tomb < 0:
                    first_tomb = slot
                continue
            if entry[0] == key:  # type: ignore[index]
                return slot, True
        raise RuntimeError("hash table full — should have been resized")
    def __setitem__(self, key: K, value: V) -> None:
        slot, found = self._find_slot(key)
        if found:
            self._slots[slot] = (key, value)
            return
        self._slots[slot] = (key, value)
        self._size += 1
        if self._size > self._capacity * self.LOAD_FACTOR_MAX:
            self._resize(self._capacity * 2)

    def __getitem__(self, key: K) -> V:
        slot, found = self._find_slot(key)
        if not found:
            raise KeyError(key)
        return self._slots[slot][1]  # type: ignore[index,return-value]

    def __contains__(self, key: K) -> bool:
        _, found = self._find_slot(key)
        return found

    def __delitem__(self, key: K) -> None:
        slot, found = self._find_slot(key)
        if not found:
            raise KeyError(key)
        self._slots[slot] = _TOMBSTONE
        self._size -= 1
    def _resize(self, new_capacity: int) -> None:
        old_slots = self._slots
        self._capacity = new_capacity
        self._slots = [None] * new_capacity
        self._size = 0
        for entry in old_slots:
            if entry is not None and entry is not _TOMBSTONE:
                k, v = entry  # type: ignore[misc]
                self[k] = v
