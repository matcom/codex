from collections.abc import Hashable, Iterable
from collections import deque
from codex.graphs.implicit import NeighborFn


def topological_sort_dfs[V: Hashable](
    vertices: Iterable[V], neighbors: NeighborFn[V]
) -> list[V]:
    """Topological sort via DFS finish times. Returns vertices in topological
    order (sources first, sinks last). Raises ValueError if the graph
    contains a directed cycle.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[V, int] = {}
    finish_order: list[V] = []

    def visit(v: V) -> None:
        color[v] = GRAY
        for w in neighbors(v):
            state = color.get(w, WHITE)
            if state == GRAY:
                raise ValueError("graph contains a cycle — not a DAG")
            if state == WHITE:
                visit(w)
        color[v] = BLACK
        finish_order.append(v)

    for v in vertices:
        if color.get(v, WHITE) == WHITE:
            visit(v)

    return list(reversed(finish_order))


def topological_sort_kahn[V: Hashable](
    vertices: Iterable[V], neighbors: NeighborFn[V]
) -> list[V]:
    """Topological sort via Kahn's algorithm (BFS from in-degree-0 vertices).
    Returns vertices in topological order (sources first). Raises ValueError
    if the graph contains a directed cycle.
    """
    vlist = list(vertices)
    in_degree: dict[V, int] = {v: 0 for v in vlist}
    adj: dict[V, list[V]] = {v: [] for v in vlist}
    for v in vlist:
        for w in neighbors(v):
            in_degree[w] = in_degree.get(w, 0) + 1
            adj[v].append(w)
    queue: deque[V] = deque(v for v in vlist if in_degree[v] == 0)
    order: list[V] = []
    while queue:
        v = queue.popleft()
        order.append(v)
        for w in adj[v]:
            in_degree[w] -= 1
            if in_degree[w] == 0:
                queue.append(w)
    if len(order) != len(vlist):
        raise ValueError("graph contains a cycle — not a DAG")
    return order


def tarjan_scc[V: Hashable](
    vertices: Iterable[V], neighbors: NeighborFn[V]
) -> list[list[V]]:
    """Tarjan's strongly connected components. Returns a list of SCCs, each
    as a list of vertices. The list is in reverse topological order of the
    condensation DAG (sinks first, sources last). O(n + m) time.
    """
    disc: dict[V, int] = {}
    low: dict[V, int] = {}
    on_stack: set[V] = set()
    stack: list[V] = []
    sccs: list[list[V]] = []
    timer = [0]

    def visit(v: V) -> None:
        timer[0] += 1
        disc[v] = low[v] = timer[0]
        stack.append(v)
        on_stack.add(v)
        for w in neighbors(v):
            if w not in disc:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], disc[w])
        if low[v] == disc[v]:
            scc: list[V] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    for v in vertices:
        if v not in disc:
            visit(v)
    return sccs
