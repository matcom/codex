from typing import Sequence
from codex.types import Ordering, default_order
from codex.sort.basic import insertion_sort


def select[T](
    items: Sequence[T], k: int, order: Ordering[T] = default_order
) -> T:
    """Return the k-th smallest element of items in worst-case O(n) time."""
    if not 0 <= k < len(items):
        raise IndexError(f"k={k} out of range for sequence of length {len(items)}")
    return _select(list(items), k, order)
def _select[T](items: list[T], k: int, order: Ordering[T]) -> T:
    if len(items) <= 5:
        # Base case: sort and pick. Insertion sort is cheap on tiny inputs.
        insertion_sort(items, order)
        return items[k]

    # Find a good pivot via median of medians.
    pivot = _median_of_medians(items, order)

    # Three-way partition by value. Equality goes into its own bucket so the
    # k-equals-many-pivots case has a clean home.
    lo = [x for x in items if order(x, pivot) < 0]
    eq = [x for x in items if order(x, pivot) == 0]
    hi = [x for x in items if order(x, pivot) > 0]

    if k < len(lo):
        return _select(lo, k, order)
    elif k < len(lo) + len(eq):
        return pivot  # k falls inside the run of equal pivots
    else:
        return _select(hi, k - len(lo) - len(eq), order)
def _median_of_medians[T](items: list[T], order: Ordering[T]) -> T:
    medians = []
    for start in range(0, len(items), 5):
        group = list(items[start:start + 5])
        insertion_sort(group, order)
        medians.append(group[len(group) // 2])
    if len(medians) == 1:
        return medians[0]
    # Recurse to find the median of the medians.
    return _select(medians, len(medians) // 2, order)
