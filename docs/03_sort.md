# basic Sorting

As we discovered in the previous chapter, structure is the secret ingredient that makes computation efficient. Searching through an unordered collection is a tedious, linear process, but searching through an ordered one is exponentially faster.

Sorting is the process of establishing this order. Formally, we want to take a sequence of items and rearrange them into a new sequence where, for any two indices $i$ and $j$, if $i < j$, then $x_i < x_j$. In this chapter, we explore the most fundamental ways to achieve this, building our intuition from simple observation to a deeper structural analysis of the sorting problem itself.

## Selection Sort

The most intuitive way to sort a list is to think about the destination. If we are building a sorted sequence, the very first element (index 0) *must* be the minimum element of the entire collection. Once that is in place, the second element (index 1) *must* be the minimum of everything that remains, and so on.

In Selection Sort, we stand at each position in the array and ask: **"Which element belongs here?"** To answer, we scan the unsorted portion of the list, find the minimum, and swap it into our current position.

```python {export=src/codex/sort/basic.py}
from typing import MutableSequence
from codex.types import Ordering, default_order

def selection_sort[T](
    items: MutableSequence[T], f: Ordering[T] = None
) -> None:
    if f is None:
        f = default_order

    n = len(items)
    for i in range(n):
        # Find the index of the minimum element in the unsorted suffix
        min_idx = i
        for j in range(i + 1, n):
            if f(items[j], items[min_idx]) < 0:
                min_idx = j

        # Swap it into the current position
        items[i], items[min_idx] = items[min_idx], items[i]

```

We implement this by directly searching for the minimum index in each iteration rather than calling a helper function, keeping the logic self-contained. Because we must scan the remaining items for every single position in the list, we perform roughly $1 + 2 + 3 + ... (n-1) = n(n-1)/2$  comparisons, leading to a time complexity of $O(n^2)$.

## Insertion Sort

We can flip the narrative of Selection Sort. Instead of standing at a position and looking for the right element, we can take an element and look for its right position. This is how most people sort a hand of cards.

We assume that everything behind our current position is already sorted. We take the next element and ask: **"How far back must I move this element so that the sequence remains sorted?"** We shift it backward, swapping it with its predecessor, until it finds its rightful place.

```python {export=src/codex/sort/basic.py}
def insertion_sort[T](
    items: MutableSequence[T], f: Ordering[T] = None
) -> None:
    if f is None:
        f = default_order

    for i in range(1, len(items)):
        j = i
        # Move the element backward as long as it is smaller than its predecessor
        while j > 0 and f(items[j], items[j-1]) < 0:
            items[j], items[j-1] = items[j-1], items[j]
            j -= 1

```

The first element is sorted by definition. The second element either stays put or moves before the first. The third moves until it is in the correct spot relative to the first two. In the worst case (a reverse-sorted list), this also results again in $O(n^2)$ operations, but it is remarkably efficient for lists that are already "nearly sorted."

## The Geometry of Inversions

To understand why these algorithms are all quadratic in complexity, we need to look at the structure of "unsortedness." Whenever a list in unsorted, is because we can find at least a couple of elements that are out of place. This means some $x_i > x_j$ where $i < j$. We define an **inversion** as any pair of such items. A sorted list has zero inversions.

With this idea in place, we can see sorting as "just" the problem of reducing the number of inversions down to zero. Any algorithm that does progress towards reducing the number of inversions is actually sorting. And a crucial insight is that there can be *at most* $O(n^2)$ inversions in any sequence of size $n$.

Selection sort reduces up to $n$ inversions with each swap, that is, all inversions relative to the current minimum element. But every swap requires up to $n$ comparisons, so we get $O(n^2)$ steps. Insertion sort reduces at most one inversion each step, by moving one item forward, thus it will require $O(n^2)$ steps to eliminate that many inversions.

## Bubble Sort

Let's now build an algorithm based on this idea of eliminating inversions directly. A first guess could be, lets try to find a pair of inverted items and swap them. But we must be careful, if we do indiscrimantely, we might end up fixing one inversion but creating other inversions.

However, a powerful idea that we won't formally proof is that if a list has *any* inversions, there must be at least one inversion between two *consecutive* elements. If we fix these local inversions, we eventually fix them all. And fixing an inversion between consecutive elements cannot create new inversions. This is the heart of **Bubble Sort**: we repeatedly step through the list and swap adjacent items that are out of order.

```python {export=src/codex/sort/basic.py}
def bubble_sort[T](
    items: MutableSequence[T], f: Ordering[T] = None
) -> None:
    if f is None:
        f = default_order

    n = len(items)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            # If we find a consecutive inversion, fix it
            if f(items[j+1], items[j]) < 0:
                items[j], items[j+1] = items[j+1], items[j]
                swapped = True

        # If no swaps occurred, the list is already sorted
        if not swapped:
            break

```

## Verification

To ensure these three fundamental sorting approaches work as intended, we can run them against a set of standard cases.

```python {export=tests/sort/test_fundamentals.py}
import pytest
from codex.sort.basic import selection_sort, insertion_sort, bubble_sort

@pytest.mark.parametrize("sort_fn", [selection_sort, insertion_sort, bubble_sort])
def test_sorting_algorithms(sort_fn):
    items = [4, 2, 7, 1, 3]
    sort_fn(items)
    assert items == [1, 2, 3, 4, 7]

    # Already sorted
    items = [1, 2, 3]
    sort_fn(items)
    assert items == [1, 2, 3]

    # Reverse sorted
    items = [3, 2, 1]
    sort_fn(items)
    assert items == [1, 2, 3]

```

## Conclusion

Selection, Insertion, and Bubble sort are all $O(n^2)$ algorithms. The reason is structural: in the worst case, a list of size  can have $O(n^2)$ inversions. Since each swap in these algorithms only fixes one inversion at a time--in the best case--we are forced to perform a quadratic number of operations.

To break this  ceiling and reach the theoretical limit of $O(n^2)$, we need to be more clever. We need algorithms that can fix *many* inversions with a single operation. This "divide and conquer" approach will be the focus of our next chapter: **Efficient Sorting**.
