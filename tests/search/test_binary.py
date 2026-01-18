from codex.search.binary import binary_search

def test_binary_search():
    items = [0,1,2,3,4,5,6,7,8,9]

    assert binary_search(3, items) == 3
    assert binary_search(10, items) is None

from codex.search.binary import bisect_left, bisect_right

def test_bisection_boundaries():
    # Sequence with a "block" of 2s
    items = [1, 2, 2, 2, 3]

    # First index where 2 is (or could be)
    assert bisect_left(2, items) == 1

    # Index after the last 2
    assert bisect_right(2, items) == 4

    # If element is missing, both return the same insertion point
    assert bisect_left(1.5, items) == 1
    assert bisect_right(1.5, items) == 1

def test_bisection_extremes():
    items = [1, 2, 3]
    assert bisect_left(0, items) == 0
    assert bisect_right(4, items) == 3

