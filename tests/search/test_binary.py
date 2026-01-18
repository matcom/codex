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

from codex.search.binary import find_first, integer_sqrt

def test_find_first():
    # Predicate: is the number >= 7?
    nums = [1, 3, 5, 7, 9, 11]
    # find_first returns the index
    idx = find_first(0, len(nums) - 1, lambda i: nums[i] >= 7)
    assert idx == 3
    assert nums[idx] == 7

def test_integer_sqrt():
    assert integer_sqrt(16) == 4
    assert integer_sqrt(15) == 3
    assert integer_sqrt(17) == 4
    assert integer_sqrt(0) == 0
    assert integer_sqrt(1) == 1
    assert integer_sqrt(10**20) == 10**10

