from typing import MutableSequence
from codex.types import Ordering, default_order


def selection_sort[T](
    items: MutableSequence[T], order: Ordering[T] = default_order
) -> None:
    n = len(items)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if order(items[j], items[min_idx]) < 0:
                min_idx = j
        items[i], items[min_idx] = items[min_idx], items[i]
def insertion_sort[T](
    items: MutableSequence[T], order: Ordering[T] = default_order
) -> None:
    for i in range(1, len(items)):
        j = i
        while j > 0 and order(items[j], items[j - 1]) < 0:
            items[j], items[j - 1] = items[j - 1], items[j]
            j -= 1
def bubble_sort[T](
    items: MutableSequence[T], order: Ordering[T] = default_order
) -> None:
    n = len(items)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if order(items[j], items[j + 1]) > 0:
                items[j], items[j + 1] = items[j + 1], items[j]
