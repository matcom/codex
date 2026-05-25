from typing import Sequence


def radix_sort(items: Sequence[int], base: int = 10) -> list[int]:
    """Sort non-negative integers in O(d * (n + base)) time.

    d = number of digits in the largest element when written in the given base.
    LSD (least significant digit first).
    """
    if not items:
        return []

    items = list(items)
    max_val = max(items)

    digit_place = 1  # ones, then base, then base^2, ...
    while max_val // digit_place > 0:
        items = _counting_sort_by_digit(items, digit_place, base)
        digit_place *= base

    return items
def _counting_sort_by_digit(
    items: list[int], digit_place: int, base: int
) -> list[int]:
    """One stable pass: sort by (x // digit_place) % base."""
    counts = [0] * base
    for x in items:
        counts[(x // digit_place) % base] += 1

    for i in range(1, base):
        counts[i] += counts[i - 1]

    output = [0] * len(items)
    for x in reversed(items):
        d = (x // digit_place) % base
        counts[d] -= 1
        output[counts[d]] = x

    return output
