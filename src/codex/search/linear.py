from typing import Sequence


def find[T](x: T, items: Sequence[T]) -> bool:
    for y in items:
        if x == y:
            return True
    return False
def index[T](x: T, items: Sequence[T]) -> int | None:
    for i, y in enumerate(items):
        if x == y:
            return i
    return None
def count[T](x: T, items: Sequence[T]) -> int:
    c = 0
    for y in items:
        if x == y:
            c += 1
    return c
from codex.types import Ordering, default_order


def minimum[T](items: Sequence[T], order: Ordering[T] = default_order) -> T:
    m = items[0]
    for x in items:
        if order(x, m) < 0:
            m = x
    return m
def maximum[T](items: Sequence[T], order: Ordering[T] = default_order) -> T:
    return minimum(items, lambda x, y: order(y, x))
