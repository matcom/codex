from typing import Sequence


def counting_sort(items: Sequence[int], k: int) -> list[int]:
    """Sort a sequence of integers in [0, k] in O(n + k) time. Stable."""
    counts = [0] * (k + 1)
    for x in items:
        counts[x] += 1

    # Prefix sums: counts[i] becomes the number of elements <= i.
    for i in range(1, k + 1):
        counts[i] += counts[i - 1]

    # Place each element, walking the input in reverse to preserve stability.
    output = [0] * len(items)
    for x in reversed(items):
        counts[x] -= 1
        output[counts[x]] = x

    return output
