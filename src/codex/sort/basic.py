from typing import MutableSequence
from codex.types import Ordering, default_order

def selection_sort[T](
    items: MutableSequence[T], f: Ordering[T] = default_order
) -> None:
    n = len(items)

    for i in range(n):
        min_idx = i

        for j in range(i + 1, n):
            if f(items[j], items[min_idx]) < 0:
                min_idx = j

        items[i], items[min_idx] = items[min_idx], items[i]

def insertion_sort[T](
    items: MutableSequence[T], f: Ordering[T] = default_order
) -> None:
    for i in range(1, len(items)):
        j = i
        # Move the element backward as long as it is smaller than its predecessor
        while j > 0 and f(items[j], items[j-1]) < 0:
            items[j], items[j-1] = items[j-1], items[j]
            j -= 1

def bubble_sort[T](
    items: MutableSequence[T], f: Ordering[T] = default_order
) -> None:
    n = len(items)

    for i in range(n):
        swapped = False

        for j in range(0, n - i - 1):
            # If we find a consecutive inversion, fix it
            if f(items[j+1], items[j]) < 0:
                items[j], items[j+1] = items[j+1], items[j]
                swapped = True

        # If no swaps occurred, the list is already sorted
        if not swapped:
            break

