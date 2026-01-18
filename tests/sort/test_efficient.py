import pytest
from codex.sort.efficient import merge_sort, quick_sort

@pytest.mark.parametrize("sort_fn", [merge_sort, quick_sort])
def test_efficient_sorting(sort_fn):
    items = [4, 2, 7, 1, 3]
    sort_fn(items)
    assert items == [1, 2, 3, 4, 7]

    # Handle duplicates and edge cases
    items = [2, 1, 2, 1]
    sort_fn(items)
    assert items == [1, 1, 2, 2]

