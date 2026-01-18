import random
from typing import MutableSequence
from codex.types import Ordering, default_order

def quick_select[T](
    items: MutableSequence[T], k: int, f: Ordering[T] = None
) -> T:
    if f is None:
        f = default_order

    if not 0 <= k < len(items):
        raise IndexError("Rank k is out of bounds")

    return _select(items, 0, len(items) - 1, k, f)

def _select[T](
    items: MutableSequence[T], low: int, high: int, k: int, f: Ordering[T]
) -> T:
    if low == high:
        return items[low]

    # Randomized pivot selection to ensure good average performance
    pivot_idx = random.randint(low, high)
    items[pivot_idx], items[high] = items[high], items[pivot_idx]

    p = _partition(items, low, high, f)

    if k == p:
        return items[p]
    elif k < p:
        return _select(items, low, p - 1, k, f)
    else:
        return _select(items, p + 1, high, k, f)

def _partition[T](
    items: MutableSequence[T], low: int, high: int, f: Ordering[T]
) -> int:
    pivot = items[high]
    i = low
    for j in range(low, high):
        if f(items[j], pivot) <= 0:
            items[i], items[j] = items[j], items[i]
            i += 1
    items[i], items[high] = items[high], items[i]
    return i

def median_of_medians[T](
    items: MutableSequence[T], k: int, f: Ordering[T] = None
) -> T:
    if f is None:
        f = default_order

    def _get_pivot(sub_items: MutableSequence[T]) -> T:
        if len(sub_items) <= 5:
            return sorted(sub_items, key=lambda x: x)[len(sub_items) // 2]

        chunks = [sub_items[i:i + 5] for i in range(0, len(sub_items), 5)]
        medians = [sorted(c, key=lambda x: x)[len(c) // 2] for c in chunks]
        return _get_pivot(medians)

    # TODO: Use the median of medians to partition and select
    # (Implementation follows standard select logic using the calculated pivot)
    # ...

