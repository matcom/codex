from collections.abc import Hashable, Iterable
from collections import deque

type FlowEdge[V] = tuple[V, V, float]


def edmonds_karp[V: Hashable](
    source: V,
    sink: V,
    vertices: Iterable[V],
    capacities: Iterable[FlowEdge[V]],
) -> tuple[float, dict[tuple[V, V], float]]:
    """Edmonds-Karp maximum flow (BFS augmenting paths). O(nm^2) time.
    Returns (max_flow_value, flow) where flow[(u, v)] is the flow on each
    original edge. Assumes no antiparallel edges in capacities.
    """
    vlist = list(vertices)
    cap: dict[V, dict[V, float]] = {v: {} for v in vlist}
    for u, v, c in capacities:
        cap.setdefault(u, {})
        cap.setdefault(v, {})
        cap[u][v] = cap[u].get(v, 0.0) + c   # merge parallel edges
        cap[v].setdefault(u, 0.0)              # ensure reverse arc exists

    res: dict[V, dict[V, float]] = {u: dict(nb) for u, nb in cap.items()}

    max_flow = 0.0
    while True:
        parent: dict[V, V | None] = {source: None}
        queue: deque[V] = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v, r in res[u].items():
                if v not in parent and r > 0:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            break

        path_flow: float = float("inf")
        v = sink
        while parent[v] is not None:
            u = parent[v]  # type: ignore
            path_flow = min(path_flow, res[u][v])
            v = u

        v = sink
        while parent[v] is not None:
            u = parent[v]  # type: ignore
            res[u][v] -= path_flow
            res[v][u] = res[v].get(u, 0.0) + path_flow
            v = u
        max_flow += path_flow

    flow: dict[tuple[V, V], float] = {
        (u, v): c - res[u].get(v, 0.0)
        for u, nb in cap.items()
        for v, c in nb.items()
        if c > 0
    }
    return max_flow, flow
