# Efficient Sorting

This chapter marks our departure from the quadratic barrier. As we established previously, sorting is the process of eliminating inversions. While basic algorithms like Selection or Insertion sort remove inversions somewhat haphazardly or one at a time, **efficient sorting** relies on a structured, recursive strategy known as **Divide and Conquer**.

By imposing a rigid structure on how we approach these inversions, we can reduce the computational cost from $O(n^2)$ to the theoretical optimum of $O(n \log n)$.

To break the quadratic limit, we must find ways to fix multiple inversions with a single operation. The most effective way to do this is to stop looking at the sequence as a monolithic block and start viewing it as a composition of smaller, more manageable sub-problems.

## Merge Sort: Intuition through Order

The fundamental insight behind **Merge Sort** is that it is remarkably easy to combine two sequences that are *already sorted*. If we have two sorted lists, we can merge them into a single sorted list in linear time by simply comparing the heads of each list and picking the smaller one.

The "conquer" part of the algorithm is this linear merge. The "divide" part is the recursive leap: if we don't have two sorted halves, we simply split our current list in two and call Merge Sort on each piece until we reach the base case—a list of a single element, which is sorted by definition.

```python {export=src/codex/sort/efficient.py}
from typing import MutableSequence, List
from codex.types import Ordering, default_order

def merge_sort[T](
    items: MutableSequence[T], f: Ordering[T] = None
) -> None:
    if f is None:
        f = default_order

    if len(items) <= 1:
        return

    mid = len(items) // 2
    left = items[:mid]
    right = items[mid:]

    merge_sort(left, f)
    merge_sort(right, f)

    # Merge the sorted halves back into items
    i = j = k = 0
    while i < len(left) and j < len(right):
        if f(left[i], right[j]) <= 0:
            items[k] = left[i]
            i += 1
        else:
            items[k] = right[j]
            j += 1
        k += 1

    while i < len(left):
        items[k] = left[i]
        i += 1
        k += 1

    while j < len(right):
        items[k] = right[j]
        j += 1
        k += 1

```

In Merge Sort, the structural strategy is to **fix inversions within each half first**. We recursively dive deep into the sequence, sorting smaller and smaller sub-sequences. Only when the sub-sequences are internally free of inversions do we perform the merge step to fix the "global" inversions between the two halves.

Because the list is halved at each step, the recursion depth is . Since we perform  work at each level of the tree to merge the results, the total complexity is .

## Quick Sort: Sorting by Partitioning

While Merge Sort is elegant, it requires  extra space to store the temporary halves during the merge process. **Quick Sort** offers a narrative shift: instead of splitting the list blindly in the middle and merging later, we **rearrange the items first** so that no merge is ever necessary.

This is achieved through **partitioning**. We pick an element called a **pivot** and rearrange the sequence so that every element smaller than the pivot moved to its left, and every element larger than the pivot moved to its right.

```python {export=src/codex/sort/efficient.py}
def quick_sort[T](
    items: MutableSequence[T], f: Ordering[T] = None
) -> None:
    if f is None:
        f = default_order

    def _quick_sort(low: int, high: int):
        if low < high:
            p = _partition(low, high)
            _quick_sort(low, p)
            _quick_sort(p + 1, high)

    def _partition(low: int, high: int) -> int:
        pivot = items[(low + high) // 2]
        i = low - 1
        j = high + 1
        while True:
            i += 1
            while f(items[i], pivot) < 0:
                i += 1
            j -= 1
            while f(items[j], pivot) > 0:
                j -= 1
            if i >= j:
                return j
            items[i], items[j] = items[j], items[i]

    _quick_sort(0, len(items) - 1)

```

The striking difference here is the order of operations. Quick Sort **fixes inversions between both halves first**. By partitioning, we ensure that there are zero inversions between the left "half" and the right "half" (no item in the left is greater than an item in the right). Once this global structure is established, we recursively fix the remaining inversions **within** each half.

This approach allows Quick Sort to operate **in-place**, requiring only  auxiliary space for the recursion stack. While its worst-case is , its average-case performance is a highly efficient .

## Verification

We can verify both algorithms using the same test suite we established for basic sorting.

```python {export=tests/sort/test_efficient.py}
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

```

## Conclusion

Both Merge Sort and Quick Sort reaffirm our central theme: **structure matters**. By moving away from the unstructured swaps of Bubble Sort and adopting a rigorous divide-and-conquer strategy, we change how we interact with the "geometry of inversions."

Whether we fix local inversions first (Merge Sort) or global ones first (Quick Sort), the result is a massive leap in efficiency. We have traded the simplicity of a double-loop for the power of recursion and structural partitioning.
