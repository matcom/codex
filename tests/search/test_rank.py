import pytest
from codex.search.rank import quick_select

def test_selection():
    items = [3, 1, 2, 4, 0]
    # Finding the median (rank 2)
    assert quick_select(items[:], 2) == 2
    # Finding the minimum (rank 0)
    assert quick_select(items[:], 0) == 0
    # Finding the maximum (rank 4)
    assert quick_select(items[:], 4) == 4

def test_duplicates():
    items = [1, 2, 1, 2, 1]
    assert quick_select(items, 0) == 1
    assert quick_select(items, 4) == 2

