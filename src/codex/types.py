from typing import Callable

type Ordering[T] = Callable[[T,T], int]

