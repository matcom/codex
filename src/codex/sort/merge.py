from typing import MutableSequence, Sequence
from codex.types import Ordering, default_order


def merge_sort[T](
    items: MutableSequence[T], order: Ordering[T] = default_order
) -> None:
    if len(items) <= 1:
        return
    mid = len(items) // 2
    left = list(items[:mid])
    right = list(items[mid:])
    merge_sort(left, order)
    merge_sort(right, order)
    merge(items, left, right, order)
def merge[T](
    items: MutableSequence[T],
    left: Sequence[T],
    right: Sequence[T],
    order: Ordering[T],
) -> None:
    i = j = k = 0
    while i < len(left) and j < len(right):
        if order(left[i], right[j]) <= 0:
            items[k] = left[i]
            i += 1
        else:
            items[k] = right[j]
            j += 1
        k += 1
    while i < len(left):
        items[k] = left[i]
        i += 1
        k += 1
    while j < len(right):
        items[k] = right[j]
        j += 1
        k += 1
