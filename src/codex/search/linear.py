from typing import Sequence

def find[T](x:T, items: Sequence[T]) -> bool:
    for y in items:
        if x == y:
            return True

    return False

def index[T](x: T, items: Sequence[T]) -> int | None:
    for i,y in enumerate(items):
        if x == y:
            return i

    return None

def count[T](x: T, items: Sequence[T]) -> int:
    c = 0

    for y in items:
        if x == y:
            c += 1

    return c

from codex.types import Ordering

def minimum[T](items: Sequence[T], f: Ordering[T]) -> T:
    m = None

    for x in items:
        if m is None or f(x,m) <= 0:
            m = x

    return m

def maximum[T](items: Sequence[T], f: Ordering[T]) -> T:
    return minimum(items, lambda x,y: f(y,x))

