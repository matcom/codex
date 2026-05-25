from typing import Sequence
from codex.types import Ordering, default_order


def count_inversions[T](
    items: Sequence[T], order: Ordering[T] = default_order
) -> int:
    n = len(items)
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            if order(items[i], items[j]) > 0:
                count += 1
    return count
from typing import MutableSequence, Sequence
from codex.types import Ordering, default_order


def count_inversions_fast[T](
    items: Sequence[T], order: Ordering[T] = default_order
) -> int:
    """Count inversions in O(n log n) via merge sort.

    Does not modify items; sorts a working copy internally.
    """
    work = list(items)
    return _merge_sort_counting(work, order)


def _merge_sort_counting[T](
    items: MutableSequence[T], order: Ordering[T]
) -> int:
    if len(items) <= 1:
        return 0
    mid = len(items) // 2
    left = list(items[:mid])
    right = list(items[mid:])
    count = _merge_sort_counting(left, order)
    count += _merge_sort_counting(right, order)
    count += _merge_counting(items, left, right, order)
    return count


def _merge_counting[T](
    items: MutableSequence[T],
    left: Sequence[T],
    right: Sequence[T],
    order: Ordering[T],
) -> int:
    count = 0
    i = j = k = 0
    while i < len(left) and j < len(right):
        if order(left[i], right[j]) <= 0:
            items[k] = left[i]
            i += 1
        else:
            items[k] = right[j]
            j += 1
            count += len(left) - i   # cross-inversions fixed by this pick
        k += 1
    while i < len(left):
        items[k] = left[i]
        i += 1
        k += 1
    while j < len(right):
        items[k] = right[j]
        j += 1
        k += 1
    return count
