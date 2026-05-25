from typing import Sequence
from codex.types import Ordering, default_order


def binary_search[T](
    x: T, items: Sequence[T], order: Ordering[T] = default_order
) -> int | None:
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        cmp = order(x, items[mid])
        if cmp == 0:
            return mid
        elif cmp < 0:
            hi = mid - 1
        else:
            lo = mid + 1
    return None
def bisect_left[T](
    x: T, items: Sequence[T], order: Ordering[T] = default_order
) -> int:
    lo, hi = 0, len(items)
    while lo < hi:
        mid = (lo + hi) // 2
        if order(items[mid], x) < 0:
            lo = mid + 1
        else:
            hi = mid
    return lo
def bisect_right[T](
    x: T, items: Sequence[T], order: Ordering[T] = default_order
) -> int:
    lo, hi = 0, len(items)
    while lo < hi:
        mid = (lo + hi) // 2
        if order(items[mid], x) <= 0:
            lo = mid + 1
        else:
            hi = mid
    return lo
from typing import Callable


def binary_search_predicate(
    predicate: Callable[[int], bool],
    lo: int,
    hi: int,
) -> int:
    """
    Return the largest integer in [lo, hi] for which predicate is True,
    assuming predicate is True on some prefix [lo, k] and False on [k+1, hi].
    Returns lo - 1 if no value satisfies the predicate.
    """
    while lo <= hi:
        mid = (lo + hi) // 2
        if predicate(mid):
            lo = mid + 1
        else:
            hi = mid - 1
    return hi
def integer_sqrt(n: int) -> int:
    if n < 0:
        raise ValueError("integer_sqrt requires n >= 0")
    return binary_search_predicate(lambda k: k * k <= n, 0, n)
