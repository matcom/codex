from collections.abc import Sequence
from typing import Callable


class SegmentTree[T]:
    def __init__(
        self,
        data: Sequence[T],
        op: Callable[[T, T], T] | None = None,
        identity: T | None = None,
    ) -> None:
        if op is None:
            op = lambda a, b: a + b  # type: ignore[assignment,return-value]
        if identity is None:
            identity = 0  # type: ignore[assignment]
        self._n = len(data)
        self._op: Callable[[T, T], T] = op
        self._identity: T = identity  # type: ignore[assignment]
        self._tree: list[T] = [identity] * (4 * max(self._n, 1))  # type: ignore[list-item]
        if self._n > 0:
            self._build(1, 0, self._n, list(data))

    def __len__(self) -> int:
        return self._n
    def _build(self, node: int, lo: int, hi: int, data: list[T]) -> None:
        if hi - lo == 1:
            self._tree[node] = data[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, data)
        self._build(2 * node + 1, mid, hi, data)
        self._tree[node] = self._op(self._tree[2 * node], self._tree[2 * node + 1])
    def update(self, i: int, value: T) -> None:
        self._update(1, 0, self._n, i, value)
    def _update(
        self, node: int, lo: int, hi: int, i: int, value: T
    ) -> None:
        if hi - lo == 1:
            self._tree[node] = value
            return
        mid = (lo + hi) // 2
        if i < mid:
            self._update(2 * node, lo, mid, i, value)
        else:
            self._update(2 * node + 1, mid, hi, i, value)
        self._tree[node] = self._op(self._tree[2 * node], self._tree[2 * node + 1])
    def query(self, l: int, r: int) -> T:
        return self._query(1, 0, self._n, l, r)

    def _query(self, node: int, lo: int, hi: int, l: int, r: int) -> T:
        if r <= lo or hi <= l:
            return self._identity
        if l <= lo and hi <= r:
            return self._tree[node]
        mid = (lo + hi) // 2
        left_val = self._query(2 * node, lo, mid, l, r)
        right_val = self._query(2 * node + 1, mid, hi, l, r)
        return self._op(left_val, right_val)
class LazySegmentTree:
    def __init__(self, data: Sequence[int]) -> None:
        self._n = len(data)
        size = 4 * max(self._n, 1)
        self._tree: list[int] = [0] * size
        self._lazy: list[int] = [0] * size
        if self._n > 0:
            self._build(1, 0, self._n, list(data))

    def __len__(self) -> int:
        return self._n

    def _build(self, node: int, lo: int, hi: int, data: list[int]) -> None:
        if hi - lo == 1:
            self._tree[node] = data[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, data)
        self._build(2 * node + 1, mid, hi, data)
        self._tree[node] = self._tree[2 * node] + self._tree[2 * node + 1]
    def _apply(self, node: int, lo: int, hi: int, delta: int) -> None:
        self._tree[node] += delta * (hi - lo)
        self._lazy[node] += delta

    def _push_down(self, node: int, lo: int, hi: int) -> None:
        if self._lazy[node] != 0:
            mid = (lo + hi) // 2
            self._apply(2 * node, lo, mid, self._lazy[node])
            self._apply(2 * node + 1, mid, hi, self._lazy[node])
            self._lazy[node] = 0
    def update(self, l: int, r: int, delta: int) -> None:
        self._update(1, 0, self._n, l, r, delta)

    def _update(
        self, node: int, lo: int, hi: int, l: int, r: int, delta: int
    ) -> None:
        if r <= lo or hi <= l:
            return
        if l <= lo and hi <= r:
            self._apply(node, lo, hi, delta)
            return
        self._push_down(node, lo, hi)
        mid = (lo + hi) // 2
        self._update(2 * node, lo, mid, l, r, delta)
        self._update(2 * node + 1, mid, hi, l, r, delta)
        self._tree[node] = self._tree[2 * node] + self._tree[2 * node + 1]
    def query(self, l: int, r: int) -> int:
        return self._query(1, 0, self._n, l, r)

    def _query(self, node: int, lo: int, hi: int, l: int, r: int) -> int:
        if r <= lo or hi <= l:
            return 0
        if l <= lo and hi <= r:
            return self._tree[node]
        self._push_down(node, lo, hi)
        mid = (lo + hi) // 2
        left = self._query(2 * node, lo, mid, l, r)
        right = self._query(2 * node + 1, mid, hi, l, r)
        return left + right
