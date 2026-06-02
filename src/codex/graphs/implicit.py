from collections.abc import Callable, Iterable, Iterator

type NeighborFn[V] = Callable[[V], Iterable[V]]
def grid_neighbors(
    width: int,
    height: int,
    blocked: frozenset[tuple[int, int]] = frozenset(),
) -> NeighborFn[tuple[int, int]]:
    """Return a NeighborFn for a width x height 4-connected grid with the
    given blocked cells. The graph has width*height vertices but the cells
    are never materialized as a collection; neighbors are computed on demand.
    """
    def neighbors(cell: tuple[int, int]) -> Iterator[tuple[int, int]]:
        x, y = cell
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in blocked:
                yield (nx, ny)
    return neighbors
