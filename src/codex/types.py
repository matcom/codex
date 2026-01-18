from typing import Callable

type Ordering[T] = Callable[[T,T], int]

def default_order(x, y):
    if x < y:
        return -1
    elif x == y:
        return 0
    else:
        return 1

