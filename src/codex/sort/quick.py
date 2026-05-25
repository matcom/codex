from typing import MutableSequence
from codex.types import Ordering, default_order


def partition[T](
    items: MutableSequence[T], lo: int, hi: int, order: Ordering[T]
) -> int:
    """
    Lomuto partition over items[lo:hi]. Treats items[hi - 1] as the pivot.
    Rearranges in place so items smaller than the pivot end up left of it,
    items not smaller end up right. Returns the pivot's final index.
    """
    pivot = items[hi - 1]
    i = lo
    for j in range(lo, hi - 1):
        if order(items[j], pivot) < 0:
            items[i], items[j] = items[j], items[i]
            i += 1
    items[i], items[hi - 1] = items[hi - 1], items[i]
    return i
def _quick_sort[T](
    items: MutableSequence[T], lo: int, hi: int, order: Ordering[T]
) -> None:
    if hi - lo < 2:
        return
    pivot_index = partition(items, lo, hi, order)
    _quick_sort(items, lo, pivot_index, order)
    _quick_sort(items, pivot_index + 1, hi, order)


def quick_sort[T](
    items: MutableSequence[T], order: Ordering[T] = default_order
) -> None:
    _quick_sort(items, 0, len(items), order)
