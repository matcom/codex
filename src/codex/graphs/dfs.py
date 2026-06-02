from collections.abc import Hashable, Iterable
from sys import setrecursionlimit
from codex.graphs.implicit import NeighborFn
from codex.structures.stack import ArrayStack


def dfs_recursive[V: Hashable](source: V, neighbors: NeighborFn[V]) -> set[V]:
    """Return the set of vertices reachable from source via depth-first
    recursion. Visits each reachable vertex exactly once.
    """
    seen: set[V] = set()
    def visit(u: V) -> None:
        seen.add(u)
        for v in neighbors(u):
            if v not in seen:
                visit(v)
    visit(source)
    return seen
def dfs_iterative[V: Hashable](source: V, neighbors: NeighborFn[V]) -> set[V]:
    """Iterative DFS using an explicit stack. Same reachability set as
    dfs_recursive, no recursion limit, $O(n)$ stack space.
    """
    seen: set[V] = {source}
    stack: ArrayStack[V] = ArrayStack()
    stack.push(source)
    while stack:
        u = stack.pop()
        for v in neighbors(u):
            if v not in seen:
                seen.add(v)
                stack.push(v)
    return seen
def dfs_timestamps[V: Hashable](
    source: V, neighbors: NeighborFn[V]
) -> tuple[dict[V, int], dict[V, int]]:
    """Recursive DFS recording discovery and finish times for every vertex
    reachable from source. Times are integers in [1, 2*reached], with
    each vertex contributing one discovery tick and one finish tick.
    Returns (discovery, finish).
    """
    discovery: dict[V, int] = {}
    finish: dict[V, int] = {}
    time = [0]  # boxed so the closure can increment it
    def visit(u: V) -> None:
        time[0] += 1
        discovery[u] = time[0]
        for v in neighbors(u):
            if v not in discovery:
                visit(v)
        time[0] += 1
        finish[u] = time[0]
    visit(source)
    return discovery, finish
def has_cycle[V: Hashable](
    vertices: Iterable[V], neighbors: NeighborFn[V]
) -> bool:
    """Detect whether the directed graph defined by (vertices, neighbors)
    contains a cycle. Uses a three-color DFS: white = undiscovered,
    gray = on the recursion stack, black = finished. A gray-to-gray
    edge is a back edge, which is the witness of a cycle.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[V, int] = {v: WHITE for v in vertices}
    def visit(u: V) -> bool:
        color[u] = GRAY
        for v in neighbors(u):
            if color.get(v, WHITE) == GRAY:
                return True
            if color.get(v, WHITE) == WHITE and visit(v):
                return True
        color[u] = BLACK
        return False
    for v in list(color.keys()):
        if color[v] == WHITE:
            if visit(v):
                return True
    return False
def connected_components[V: Hashable](
    vertices: Iterable[V], neighbors: NeighborFn[V]
) -> list[set[V]]:
    """Sweep DFS over the vertex set. Return a list of components, each
    as the set of vertices reachable from one starting vertex via the
    undirected closure of neighbors. Same contract as the BFS sweep in
    chapter 32; this version uses iterative DFS to avoid recursion-limit
    issues on long chains.
    """
    seen: set[V] = set()
    components: list[set[V]] = []
    for start in vertices:
        if start in seen:
            continue
        component: set[V] = {start}
        stack: ArrayStack[V] = ArrayStack()
        stack.push(start)
        while stack:
            u = stack.pop()
            for v in neighbors(u):
                if v not in component:
                    component.add(v)
                    stack.push(v)
        seen |= component
        components.append(component)
    return components
