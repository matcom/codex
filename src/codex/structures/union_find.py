class QuickFind:
    def __init__(self, n: int) -> None:
        self._label = list(range(n))

    def find(self, x: int) -> int:
        return self._label[x]

    def connected(self, x: int, y: int) -> bool:
        return self._label[x] == self._label[y]
    def union(self, x: int, y: int) -> None:
        lx, ly = self._label[x], self._label[y]
        if lx == ly:
            return
        for i in range(len(self._label)):
            if self._label[i] == lx:
                self._label[i] = ly
class QuickUnion:
    def __init__(self, n: int) -> None:
        self._parent = list(range(n))

    def find(self, x: int) -> int:
        while self._parent[x] != x:
            x = self._parent[x]
        return x

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)
    def union(self, x: int, y: int) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        self._parent[rx] = ry
class UnionFind:
    def __init__(self, n: int) -> None:
        self._parent = list(range(n))
        self._rank = [0] * n
    def union(self, x: int, y: int) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self._rank[rx] < self._rank[ry]:
            self._parent[rx] = ry
        elif self._rank[rx] > self._rank[ry]:
            self._parent[ry] = rx
        else:
            self._parent[ry] = rx
            self._rank[rx] += 1
    def find(self, x: int) -> int:
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)
