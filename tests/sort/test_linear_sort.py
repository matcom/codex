import pytest
from codex.sort.linear import counting_sort, radix_sort

def test_counting_sort():
    items = [4, 1, 3, 4, 3]
    # Range is [0, 4]
    assert counting_sort(items, 4) == [1, 3, 3, 4, 4]

def test_radix_sort():
    items = [170, 45, 75, 90, 802, 24, 2, 66]
    expected = [2, 24, 45, 66, 75, 90, 170, 802]
    assert radix_sort(items) == expected

