from collections.abc import Sequence


class FenwickTree:
    def __init__(self, n_or_data: int | Sequence[int]) -> None:
        if isinstance(n_or_data, int):
            self._n = n_or_data
            self._tree: list[int] = [0] * (self._n + 1)
        else:
            data = list(n_or_data)
            self._n = len(data)
            self._tree = [0] * (self._n + 1)
            for i in range(1, self._n + 1):
                self._tree[i] += data[i - 1]
                parent = i + (i & -i)
                if parent <= self._n:
                    self._tree[parent] += self._tree[i]

    def __len__(self) -> int:
        return self._n
    def update(self, i: int, delta: int) -> None:
        while i <= self._n:
            self._tree[i] += delta
            i += i & -i
    def prefix(self, i: int) -> int:
        total = 0
        while i > 0:
            total += self._tree[i]
            i -= i & -i
        return total
    def range_sum(self, l: int, r: int) -> int:
        return self.prefix(r) - self.prefix(l - 1)
class FenwickXOR:
    def __init__(self, n_or_data: int | Sequence[int]) -> None:
        if isinstance(n_or_data, int):
            self._n = n_or_data
            self._tree: list[int] = [0] * (self._n + 1)
        else:
            data = list(n_or_data)
            self._n = len(data)
            self._tree = [0] * (self._n + 1)
            for i in range(1, self._n + 1):
                self._tree[i] ^= data[i - 1]
                parent = i + (i & -i)
                if parent <= self._n:
                    self._tree[parent] ^= self._tree[i]

    def __len__(self) -> int:
        return self._n

    def update(self, i: int, delta: int) -> None:
        while i <= self._n:
            self._tree[i] ^= delta
            i += i & -i

    def prefix(self, i: int) -> int:
        total = 0
        while i > 0:
            total ^= self._tree[i]
            i -= i & -i
        return total
