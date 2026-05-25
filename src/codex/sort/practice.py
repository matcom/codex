from typing import MutableSequence
from codex.types import Ordering, default_order


def _insertion_sort_range[T](
    items: MutableSequence[T], lo: int, hi: int, order: Ordering[T]
) -> None:
    """In-place insertion sort on items[lo:hi]. Tight loop, no recursion."""
    for i in range(lo + 1, hi):
        j = i
        while j > lo and order(items[j], items[j - 1]) < 0:
            items[j], items[j - 1] = items[j - 1], items[j]
            j -= 1
import random
from codex.sort.quick import partition


def introsort[T](
    items: MutableSequence[T],
    order: Ordering[T] = default_order,
    insertion_cutoff: int = 16,
) -> None:
    """Introsort-lite: quicksort with insertion-sort cutover for small subarrays.

    The original Musser introsort also tracks recursion depth and falls back
    to heapsort beyond 2*log2(n) levels; that piece needs heaps (Part III)
    and is omitted here.
    """
    _introsort(items, 0, len(items), order, insertion_cutoff)


def _introsort[T](
    items: MutableSequence[T],
    lo: int,
    hi: int,
    order: Ordering[T],
    cutoff: int,
) -> None:
    if hi - lo <= cutoff:
        _insertion_sort_range(items, lo, hi, order)
        return
    pivot_idx = random.randint(lo, hi - 1)
    items[pivot_idx], items[hi - 1] = items[hi - 1], items[pivot_idx]
    p = partition(items, lo, hi, order)
    _introsort(items, lo, p, order, cutoff)
    _introsort(items, p + 1, hi, order, cutoff)
def _merge_range[T](
    items: MutableSequence[T],
    lo: int,
    mid: int,
    hi: int,
    order: Ordering[T],
) -> None:
    """Merge items[lo:mid] and items[mid:hi] in place. Both halves must be sorted."""
    left = list(items[lo:mid])
    right = list(items[mid:hi])
    i = j = 0
    k = lo
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
def timsort_lite[T](
    items: MutableSequence[T],
    order: Ordering[T] = default_order,
    min_run: int = 32,
) -> None:
    """Timsort-lite: bottom-up merge sort with insertion-sort runs.

    The real Timsort (Tim Peters, 2002) also detects natural runs in the
    input and uses a run-stack with merge invariants; both refinements are
    described in the chapter prose and omitted here.
    """
    n = len(items)
    if n < 2:
        return

    # Phase 1: sort fixed-size chunks with insertion sort.
    for start in range(0, n, min_run):
        end = min(start + min_run, n)
        _insertion_sort_range(items, start, end, order)

    # Phase 2: bottom-up merge of the sorted chunks.
    size = min_run
    while size < n:
        for left_start in range(0, n, 2 * size):
            mid = min(left_start + size, n)
            right_end = min(left_start + 2 * size, n)
            if mid < right_end:
                _merge_range(items, left_start, mid, right_end, order)
        size *= 2
