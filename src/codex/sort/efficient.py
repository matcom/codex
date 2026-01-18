from typing import MutableSequence, List
from codex.types import Ordering, default_order

def merge_sort[T](
    items: MutableSequence[T], f: Ordering[T] = None
) -> None:
    if f is None:
        f = default_order

    if len(items) <= 1:
        return

    mid = len(items) // 2
    left = items[:mid]
    right = items[mid:]

    merge_sort(left, f)
    merge_sort(right, f)

    # Merge the sorted halves back into items
    i = j = k = 0
    while i < len(left) and j < len(right):
        if f(left[i], right[j]) <= 0:
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

def quick_sort[T](
    items: MutableSequence[T], f: Ordering[T] = None
) -> None:
    if f is None:
        f = default_order

    def _quick_sort(low: int, high: int):
        if low < high:
            p = _partition(low, high)
            _quick_sort(low, p)
            _quick_sort(p + 1, high)

    def _partition(low: int, high: int) -> int:
        pivot = items[(low + high) // 2]
        i = low - 1
        j = high + 1
        while True:
            i += 1
            while f(items[i], pivot) < 0:
                i += 1
            j -= 1
            while f(items[j], pivot) > 0:
                j -= 1
            if i >= j:
                return j
            items[i], items[j] = items[j], items[i]

    _quick_sort(0, len(items) - 1)

