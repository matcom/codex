from typing import Sequence
from codex.types import Ordering, default_order

def binary_search[T](
    x: T, items: Sequence[T], f: Ordering[T] = None
) -> int | None:
    if f is None:
        f = default_order

    l, r = 0, len(items)-1

    while l <= r:
        m = (l + r) // 2
        res = f(x, items[m])

        if res == 0:
            return m
        elif res < 0:
            r = m - 1
        else:
            l = m + 1

def bisect_left[T](
    x: T, items: Sequence[T], f: Ordering[T] = None
) -> int:
    if f is None:
        f = default_order

    l, r = 0, len(items)

    while l < r:
        m = (l + r) // 2
        if f(items[m], x) < 0:
            l = m + 1
        else:
            r = m

    return l

def bisect_right[T](
    x: T, items: Sequence[T], f: Ordering[T] = None
) -> int:
    if f is None:
        f = default_order

    l, r = 0, len(items)

    while l < r:
        m = (l + r) // 2
        if f(x, items[m]) < 0:
            r = m
        else:
            l = m + 1

    return l

from typing import Callable

def find_first(
    low: int, high: int, p: Callable[[int], bool]
) -> int | None:
    """
    Finds the first index in [low, high] for which p(index) is True.
    Assumes p is monotonic: if p(i) is True, p(i+1) is also True.
    """
    ans = None
    l, r = low, high

    while l <= r:
        m = (l + r) // 2
        if p(m):
            ans = m
            r = m - 1
        else:
            l = m + 1

    return ans

def integer_sqrt(n: int) -> int:
    if n < 0:
        raise ValueError("Square root not defined for negative numbers")
    if n < 2:
        return n

    # Find the first x such that x*x > n
    first_too_big = find_first(1, n, lambda x: x * x > n)

    return first_too_big - 1

