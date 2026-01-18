from typing import MutableSequence, Callable, List
from codex.types import Ordering, default_order

def counting_sort(
    items: MutableSequence[int], k: int
) -> List[int]:
    """
    Sorts a sequence of integers in the range [0, k].
    This implementation is stable.
    """
    counts = [0] * (k + 1)
    for x in items:
        counts[x] += 1

    # Transform counts into starting indices
    for i in range(1, k + 1):
        counts[i] += counts[i - 1]

    output = [0] * len(items)
    # Iterate backwards to maintain stability
    for x in reversed(items):
        counts[x] -= 1
        output[counts[x]] = x

    return output

def radix_sort(items: MutableSequence[int], base: int = 10) -> List[int]:
    if not items:
        return items

    max_val = max(items)
    exp = 1
    output = list(items)

    while max_val // exp > 0:
        output = _counting_sort_by_digit(output, exp, base)
        exp *= base

    return output

def _counting_sort_by_digit(items: List[int], exp: int, base: int) -> List[int]:
    counts = [0] * base
    for x in items:
        digit = (x // exp) % base
        counts[digit] += 1

    for i in range(1, base):
        counts[i] += counts[i - 1]

    res = [0] * len(items)
    for x in reversed(items):
        digit = (x // exp) % base
        counts[digit] -= 1
        res[counts[digit]] = x
    return res

