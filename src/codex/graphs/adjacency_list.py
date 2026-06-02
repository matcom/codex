from collections.abc import Hashable, Iterable, Iterator


class AdjacencyList[V: Hashable]:
    """Graph stored as a dictionary mapping each vertex to a dictionary
    of (neighbor -> weight) entries.

    O(1) amortized for has_edge, weight, and add_edge. O(deg(u)) for
    neighbors(u). O(n + m) space. The default representation for almost
    every chapter in Part V.
    """

    def __init__(self, directed: bool = False) -> None:
        self._directed = directed
        self._adj: dict[V, dict[V, float]] = {}
    def add_vertex(self, v: V) -> None:
        if v not in self._adj:
            self._adj[v] = {}

    def add_edge(self, u: V, v: V, weight: float = 1.0) -> None:
        self.add_vertex(u)
        self.add_vertex(v)
        self._adj[u][v] = weight
        if not self._directed:
            self._adj[v][u] = weight

    def __len__(self) -> int:
        return len(self._adj)

    def vertices(self) -> Iterable[V]:
        return self._adj.keys()

    def has_edge(self, u: V, v: V) -> bool:
        return u in self._adj and v in self._adj[u]

    def weight(self, u: V, v: V) -> float:
        return self._adj[u][v]

    def degree(self, u: V) -> int:
        return len(self._adj[u])

    def neighbors(self, u: V) -> Iterator[V]:
        yield from self._adj[u].keys()

    def weighted_neighbors(self, u: V) -> Iterator[tuple[V, float]]:
        yield from self._adj[u].items()

    def edges(self) -> Iterator[tuple[V, V, float]]:
        seen: set[tuple[V, V]] = set()
        for u, nbrs in self._adj.items():
            for v, w in nbrs.items():
                if not self._directed and (v, u) in seen:
                    continue
                seen.add((u, v))
                yield (u, v, w)
