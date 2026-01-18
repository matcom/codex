# Rankings and Selection

This chapter addresses the problem of selecting the -th smallest element in a sequence—a task that lies at the heart of calculating medians, percentiles, and other order statistics. While one could simply sort the entire collection in  time and pick the element at index , we can do better by leveraging the same structural insights we gained from Quick Sort.

Finding the "rank" of an element—its position in a sorted version of the collection—is a fundamental operation in data analysis. The most common case is finding the **median**, the element that splits a set into two equal halves. By generalizing this, we look for the -th order statistic: the value that is greater than or equal to exactly  elements.

## Quick Select: Selection via Partitioning

The core of Quick Sort was the `partition` operation, which organized elements around a pivot. In Quick Sort, we recursively processed both sides of the partition. However, for selection, we only care about the side that contains our target index .

This leads to **Quick Select**. Because we discard one-half of the search space at every step, we aren't performing a "divide and conquer" so much as a "prune and search" strategy.

```python {export=src/codex/search/rank.py}
import random
from typing import MutableSequence
from codex.types import Ordering, default_order

def quick_select[T](
    items: MutableSequence[T], k: int, f: Ordering[T] = None
) -> T:
    if f is None:
        f = default_order

    if not 0 <= k < len(items):
        raise IndexError("Rank k is out of bounds")

    return _select(items, 0, len(items) - 1, k, f)

def _select[T](
    items: MutableSequence[T], low: int, high: int, k: int, f: Ordering[T]
) -> T:
    if low == high:
        return items[low]

    # Randomized pivot selection to ensure good average performance
    pivot_idx = random.randint(low, high)
    items[pivot_idx], items[high] = items[high], items[pivot_idx]

    p = _partition(items, low, high, f)

    if k == p:
        return items[p]
    elif k < p:
        return _select(items, low, p - 1, k, f)
    else:
        return _select(items, p + 1, high, k, f)

def _partition[T](
    items: MutableSequence[T], low: int, high: int, f: Ordering[T]
) -> int:
    pivot = items[high]
    i = low
    for j in range(low, high):
        if f(items[j], pivot) <= 0:
            items[i], items[j] = items[j], items[i]
            i += 1
    items[i], items[high] = items[high], items[i]
    return i

```

The probabilistic analysis of Quick Select is striking. In the worst case—where we consistently pick the worst possible pivot—the complexity is still . However, on average, the size of the search space follows a geometric series: , which converges to . This means that on average, Quick Select finds the -th order statistic in **** time.

## Median of Medians: Deterministic Selection

While randomization is practically robust, we can achieve a guaranteed  worst-case time using a clever, ad hoc approach to pivot selection known as the **Median of Medians** algorithm.

The goal is to find a pivot that is guaranteed to be "good enough"—meaning it is not too close to either end of the sorted sequence. We do this by:

1. Dividing the list into groups of five.
2. Finding the median of each small group.
3. Recursively finding the median of these medians.

This "median of medians" is then used as the pivot for a standard partition.

```python {export=src/codex/search/rank.py}
def median_of_medians[T](
    items: MutableSequence[T], k: int, f: Ordering[T] = None
) -> T:
    if f is None:
        f = default_order

    def _get_pivot(sub_items: MutableSequence[T]) -> T:
        if len(sub_items) <= 5:
            return sorted(sub_items, key=lambda x: x)[len(sub_items) // 2]

        chunks = [sub_items[i:i + 5] for i in range(0, len(sub_items), 5)]
        medians = [sorted(c, key=lambda x: x)[len(c) // 2] for c in chunks]
        return _get_pivot(medians)

    # TODO: Use the median of medians to partition and select
    # (Implementation follows standard select logic using the calculated pivot)
    # ...

```

The structural beauty of this algorithm lies in the constant `5`. It is the smallest odd number that ensures the recursive step prunes enough of the search space to maintain a linear recurrence.

## Verification

To ensure our selection logic holds, we test it by finding various ranks in both random and edge-case sequences.

```python {export=tests/search/test_rank.py}
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

```

## Conclusion

With the implementation of selection algorithms, we have completed our initial survey of searching and sorting. The progression from  linear search to  sorting, and finally back to  for selection, demonstrates the power of structured thinking. By understanding how to manipulate inversions and search spaces, we can find specific needles in increasingly large haystacks with mathematical precision.