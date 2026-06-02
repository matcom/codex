from collections.abc import Hashable, Iterable, Iterator, Sequence
from math import inf


class AdjacencyMatrix[V: Hashable]:
    """Graph stored as an n x n matrix of edge weights, with float('inf')
    for absent edges.

    O(1) edge queries, O(n^2) space. Use when the graph is dense
    (m = Theta(n^2)) or when the algorithm hammers has_edge / weight
    lookups, like Floyd-Warshall in chapter 35.
    """

    def __init__(self, vertices: Sequence[V], directed: bool = False) -> None:
        self._directed = directed
        self._index: dict[V, int] = {v: i for i, v in enumerate(vertices)}
        self._vertices: list[V] = list(vertices)
        n = len(vertices)
        self._matrix: list[list[float]] = [[inf] * n for _ in range(n)]
    def __len__(self) -> int:
        return len(self._vertices)

    def vertices(self) -> Iterable[V]:
        return self._vertices

    def add_edge(self, u: V, v: V, weight: float = 1.0) -> None:
        i, j = self._index[u], self._index[v]
        self._matrix[i][j] = weight
        if not self._directed:
            self._matrix[j][i] = weight

    def has_edge(self, u: V, v: V) -> bool:
        return self._matrix[self._index[u]][self._index[v]] < inf

    def weight(self, u: V, v: V) -> float:
        return self._matrix[self._index[u]][self._index[v]]

    def neighbors(self, u: V) -> Iterator[V]:
        i = self._index[u]
        for j, w in enumerate(self._matrix[i]):
            if w < inf:
                yield self._vertices[j]

    def edges(self) -> Iterator[tuple[V, V, float]]:
        for i, row in enumerate(self._matrix):
            for j, w in enumerate(row):
                if w < inf and (self._directed or i <= j):
                    yield (self._vertices[i], self._vertices[j], w)
