from collections.abc import Callable, Hashable, Iterable
from math import inf
from codex.structures.union_find import UnionFind
from codex.trees.heap import HeapPriorityQueue

type WeightedEdge[V] = tuple[V, V, float]
type WeightedNeighborFn[V] = Callable[[V], Iterable[tuple[V, float]]]


def kruskal[V: Hashable](
    vertices: Iterable[V],
    edges: Iterable[WeightedEdge[V]],
) -> list[WeightedEdge[V]]:
    """Kruskal's minimum spanning tree. Sorts edges by weight and adds
    each one that doesn't form a cycle, using union-find for cycle
    detection. Returns the MST as a list of edges. On a disconnected
    graph, returns a minimum spanning forest (one tree per component).
    """
    vlist = list(vertices)
    index = {v: i for i, v in enumerate(vlist)}
    uf = UnionFind(len(vlist))
    mst: list[WeightedEdge[V]] = []
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        iu, iv = index[u], index[v]
        if not uf.connected(iu, iv):
            uf.union(iu, iv)
            mst.append((u, v, w))
    return mst


def prim[V: Hashable](
    source: V,
    neighbors: WeightedNeighborFn[V],
) -> tuple[dict[V, float], dict[V, V | None]]:
    """Prim's minimum spanning tree. Grows the MST from source using
    a min-heap keyed on edge weight (not accumulated path distance).
    Returns (key, parent) where key[v] is the weight of the MST edge
    connecting v to the tree, and parent[v] is v's predecessor in the
    MST. source maps to (0.0, None). Unreachable vertices don't appear.
    """
    key: dict[V, float] = {source: 0.0}
    parent: dict[V, V | None] = {source: None}
    in_mst: set[V] = set()
    pq: HeapPriorityQueue[float, V] = HeapPriorityQueue()
    pq.push(0.0, source)
    while pq:
        k, u = pq.pop()
        if u in in_mst:
            continue
        in_mst.add(u)
        for v, w in neighbors(u):
            if v not in in_mst and w < key.get(v, inf):
                key[v] = w
                parent[v] = u
                pq.push(w, v)
    return key, parent
