from collections.abc import Hashable, Iterable
from math import inf

type WeightedEdge[V] = tuple[V, V, float]


def bellman_ford[V: Hashable](
    source: V,
    vertices: Iterable[V],
    edges: Iterable[WeightedEdge[V]],
) -> tuple[dict[V, float], dict[V, V | None]]:
    """Bellman-Ford single-source shortest paths. Handles negative-weight
    edges. Raises ValueError if a negative-weight cycle is reachable from
    source. Returns (dist, parent), where dist[v] is the shortest-path
    distance from source to v (inf if unreachable) and parent[v] is the
    predecessor of v on a shortest path.
    """
    dist: dict[V, float] = {v: inf for v in vertices}
    dist[source] = 0.0
    parent: dict[V, V | None] = {source: None}
    n = len(dist)
    edge_list = list(edges)
    for _ in range(n - 1):
        _relax_pass(edge_list, dist, parent)
    if _relax_pass(edge_list, dist, parent):
        raise ValueError("negative-weight cycle reachable from source")
    return dist, parent


def _relax_pass[V: Hashable](
    edges: list[WeightedEdge[V]],
    dist: dict[V, float],
    parent: dict[V, V | None],
) -> bool:
    """Relax every edge once. Return True if any distance improved."""
    improved = False
    for u, v, w in edges:
        d_u = dist.get(u, inf)
        if d_u + w < dist.get(v, inf):
            dist[v] = d_u + w
            parent[v] = u
            improved = True
    return improved


def floyd_warshall[V: Hashable](
    vertices: Iterable[V],
    edges: Iterable[WeightedEdge[V]],
) -> dict[V, dict[V, float]]:
    """Floyd-Warshall all-pairs shortest paths. Returns dist where
    dist[u][v] is the shortest-path distance from u to v (inf if
    unreachable). Handles negative-weight edges. A negative-weight cycle
    is indicated by dist[v][v] < 0 for any vertex v after the call.
    """
    vlist = list(vertices)
    dist: dict[V, dict[V, float]] = {
        u: {v: (0.0 if u == v else inf) for v in vlist}
        for u in vlist
    }
    for u, v, w in edges:
        if w < dist[u][v]:
            dist[u][v] = w
    for k in vlist:
        _relax_via(vlist, dist, k)
    return dist


def _relax_via[V: Hashable](
    vertices: list[V],
    dist: dict[V, dict[V, float]],
    k: V,
) -> None:
    """Update dist[i][j] for all i, j by routing through intermediate k."""
    for i in vertices:
        for j in vertices:
            through_k = dist[i][k] + dist[k][j]
            if through_k < dist[i][j]:
                dist[i][j] = through_k
