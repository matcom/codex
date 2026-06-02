from collections.abc import Hashable, Iterator
from codex.graphs.implicit import NeighborFn
from codex.structures.queue import LinkedQueue


def bfs_distances[V: Hashable](source: V, neighbors: NeighborFn[V]) -> dict[V, int]:
    """Return a dict mapping each vertex reachable from source to its
    distance in edges. Unreachable vertices are absent.
    """
    dist: dict[V, int] = {source: 0}
    queue: LinkedQueue[V] = LinkedQueue()
    queue.enqueue(source)
    while queue:
        u = queue.dequeue()
        for v in neighbors(u):
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.enqueue(v)
    return dist
def bfs[V: Hashable](
    source: V, neighbors: NeighborFn[V]
) -> tuple[dict[V, int], dict[V, V | None]]:
    """Run BFS from source. Return (dist, parent) where dist maps each
    reachable vertex to its distance and parent maps each non-source
    reachable vertex to the vertex it was first discovered from. The
    source maps to None in parent.
    """
    dist: dict[V, int] = {source: 0}
    parent: dict[V, V | None] = {source: None}
    queue: LinkedQueue[V] = LinkedQueue()
    queue.enqueue(source)
    while queue:
        u = queue.dequeue()
        for v in neighbors(u):
            if v not in dist:
                dist[v] = dist[u] + 1
                parent[v] = u
                queue.enqueue(v)
    return dist, parent
def reconstruct_path[V: Hashable](
    parent: dict[V, V | None], target: V
) -> list[V] | None:
    """Walk parent pointers backward from target to the source (the
    vertex whose parent is None). Return the path in source-first order,
    or None if target is not in parent (i.e., unreachable).
    """
    if target not in parent:
        return None
    path: list[V] = []
    current: V | None = target
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path
def bfs_layers[V: Hashable](
    source: V, neighbors: NeighborFn[V]
) -> Iterator[list[V]]:
    """Yield each BFS layer as a list, starting with [source] at layer 0.
    Layer k is the set of vertices at distance exactly k from source.
    """
    seen: set[V] = {source}
    frontier: list[V] = [source]
    while frontier:
        yield frontier
        next_frontier: list[V] = []
        for u in frontier:
            for v in neighbors(u):
                if v not in seen:
                    seen.add(v)
                    next_frontier.append(v)
        frontier = next_frontier
def connected_components[V: Hashable](
    vertices: Iterator[V] | list[V] | set[V],
    neighbors: NeighborFn[V],
) -> list[set[V]]:
    """Sweep BFS over the vertex set. Return a list of components, each
    as a set of vertices. The component containing vertex u is the set
    of vertices reachable from u via the undirected closure of neighbors.
    """
    seen: set[V] = set()
    components: list[set[V]] = []
    for start in vertices:
        if start in seen:
            continue
        component: set[V] = {start}
        queue: LinkedQueue[V] = LinkedQueue()
        queue.enqueue(start)
        while queue:
            u = queue.dequeue()
            for v in neighbors(u):
                if v not in component:
                    component.add(v)
                    queue.enqueue(v)
        seen |= component
        components.append(component)
    return components
