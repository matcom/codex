from collections.abc import Callable, Hashable, Iterable
from math import inf
from codex.trees.heap import HeapPriorityQueue

type WeightedNeighborFn[V] = Callable[[V], Iterable[tuple[V, float]]]


def dijkstra[V: Hashable](
    source: V, neighbors: WeightedNeighborFn[V]
) -> tuple[dict[V, float], dict[V, V | None]]:
    """Dijkstra's single-source shortest-path algorithm. Returns
    (dist, parent), where dist[v] is the weighted shortest-path distance
    from source to v (math.inf if v is unreachable), and parent[v] is
    the predecessor of v on a shortest path. Requires every edge weight
    returned by neighbors to be non-negative; raises ValueError on a
    negative weight.
    """
    dist: dict[V, float] = {source: 0.0}
    parent: dict[V, V | None] = {source: None}
    finalized: set[V] = set()
    pq: HeapPriorityQueue[float, V] = HeapPriorityQueue()
    pq.push(0.0, source)
    while pq:
        d, u = pq.pop()
        if u in finalized:
            continue
        finalized.add(u)
        for v, w in neighbors(u):
            if w < 0:
                raise ValueError(f"Dijkstra cannot handle negative edge weight {w}")
            new_d = d + w
            if new_d < dist.get(v, inf):
                dist[v] = new_d
                parent[v] = u
                pq.push(new_d, v)
    return dist, parent
