from collections.abc import Hashable, Iterable, Iterator


class EdgeList[V: Hashable]:
    """Graph stored as a flat list of (u, v, weight) edge triples.

    Cheap to build, cheap to enumerate edges, expensive to query.
    Best for Kruskal's MST (chapter 36), where the whole point is to
    sort the edges once and walk them in order.
    """

    def __init__(self, directed: bool = False) -> None:
        self._directed = directed
        self._edges: list[tuple[V, V, float]] = []
        self._vertices: set[V] = set()

    def add_edge(self, u: V, v: V, weight: float = 1.0) -> None:
        self._edges.append((u, v, weight))
        self._vertices.add(u)
        self._vertices.add(v)

    def __len__(self) -> int:
        return len(self._vertices)

    def vertices(self) -> Iterable[V]:
        return self._vertices

    def edges(self) -> Iterator[tuple[V, V, float]]:
        yield from self._edges

    def neighbors(self, u: V) -> Iterator[V]:
        for x, y, _ in self._edges:
            if x == u:
                yield y
            elif not self._directed and y == u:
                yield x
