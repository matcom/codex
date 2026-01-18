from typing import Sequence
from codex.types import Ordering, default_order

def binary_search[T](
    x: T, items: Sequence[T], f: Ordering[T] = None
) -> int | None:
    if f is None:
        f = default_order

    l, r = 0, len(items)-1

    while l <= r:
        m = (l+r)//2

        if items[m] == x:
            return m
        elif x < items[m]:
            r = m - 1
        else:
            l = m + 1

    return None

