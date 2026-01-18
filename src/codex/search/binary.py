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

def bisect_left[T](x: T, items: Sequence[T], f: Ordering[T] = None) -> int:
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

def bisect_right[T](x: T, items: Sequence[T], f: Ordering[T] = None) -> int:
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

