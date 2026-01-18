# Efficient Search

Now that we have started considering ordered sets, we can introduce what is arguably _the most beautiful algorithm in the history of Computer Science_: **binary search**. A quintessential algorithm that shows how a well-structured search space is exponentially easier to search than an arbitrary one.

To build some intuition for binary search, let's consider we have an _ordered_ sequence of items; that is, we always have that if `i < j`, then `l[i] <= l[j]`. This simple constraint introduces a very powerful condition in our search problem: if we are looking for `x`, and `x < y`, then we know no item after `y` in the sequence can be `x`.

Convince yourself of this simple truth before moving on.

This fundamentally changes how fast we can search. Why? Because now every test that we perform--every time we ask whether `x < y` for some `y`--we gain _a lot_ of information, not only about `y`, but about _every other item greater or equal than `y`_.

This is the magical leap we always need in order to write a fast algorithm--fast as in, it doesn't need to check _every single thing_. We need a way to gather more information from every operation, so we have to do less operations. Let's see how we can leverage this powerful intuition to make search not only faster, but _exponentially faster_ when items are ordered.

Consider the set of items $x_1, ..., y, ..., x_n$. We are searching for item $x$, and we choose to test whether $x \leq y$. We have two choices, either $x \leq y$, or, on the contrary, $x > y$. We want to gain the maximum amount of information in either case. The question is, how should we pick $y$?

If we pick $y$ too close to either end, we can get lucky and cross off a large number of items. For example if $y$ is in the last 5% of the sequence, and it turns out $x > y$, we have just removed the first 95% of the sequence without looking at it! But of course, we won't get _that_ lucky too often. In fact, if $x$ is a random input, it could potentially be anywhere in the sequence. Under the fairly mild assumption that $x$ should be uniformly distributed among all indices in the sequences, we will get _this_ lucky exactly 5% of the time. The other 95! we have almost as much work to do as in the beginning.

It should be obvious by now that the best way to pick $y$ either case is to choose the middle of the sequence. In that way I always cross off 50% of the items, regardless of luck. This is good, we just removed a huge chunk. But it gets even better.

Now, instead of looking for $x$ linearly in the remaining 50% of the items, we do the exact same thing again! We take the middle point of the current half, and now we can cross off another 25% of the items. If we keep repeating this over and over, how fast will we be left with just one item? Keep that thought in mind.

## Binary Search

Before doing the math, here is the most straightforward implemenation of binary search. We will use two indices, `l(eft)` and `r(ight)` to keep track of the current sub-sequence we are analyzing. As long as `l <= r` there is at least one item left to test. Once `l > r`, we must conclude `x` is not in the sequence.

Here goes the code.

```python {export=src/codex/search/binary.py}
from typing import Sequence
from codex.types import Ordering, default_order

def binary_search[T](
    x: T, items: Sequence[T], f: Ordering[T] = None
) -> int | None:
    if f is None:
        f = default_order

    l, r = 0, len(items)-1

    while l <= r:
        m = (l + r) // 2
        res = f(x, items[m])

        if res == 0:
            return m
        elif res < 0:
            r = m - 1
        else:
            l = m + 1

```

Here is a minimal test.

```python {export=tests/search/test_binary.py}
from codex.search.binary import binary_search

def test_binary_search():
    items = [0,1,2,3,4,5,6,7,8,9]

    assert binary_search(3, items) == 3
    assert binary_search(10, items) is None

```

## Bisection

Standard binary search is excellent for determining if an element exists, but it provides no guarantees about which index is returned if the sequence contains duplicates. In many applications—such as range queries or maintaining a sorted list—we need to find the specific boundaries where an element resides or where it should be inserted to maintain order.

This is the problem of **bisection**. We define two variants: `bisect_left` and `bisect_right`.

The `bisect_left` function finds the first index where an element `x` could be inserted while maintaining the sorted order of the sequence. If `x` is already present, the insertion point will be before (to the left of) any existing entries. Effectively, it returns the index of the first element that is not "less than" `x`.

```python {export=src/codex/search/binary.py}
def bisect_left[T](
    x: T, items: Sequence[T], f: Ordering[T] = None
) -> int:
    if f is None:
        f = default_order

    l, r = 0, len(items)

    while l < r:
        m = (l + r) // 2
        if f(items[m], x) < 0:
            l = m + 1
        else:
            r = m

    return l

```

The logic here is subtle: instead of returning immediately when an element matches, we keep narrowing the window until `l` and `r` meet. By setting `r = m` when `items[m] >= x`, we ensure the right boundary eventually settles on the first occurrence.

Conversely, `bisect_right` (sometimes called `bisect_upper`) finds the last possible insertion point. If `x` is present, the index returned will be after (to the right of) all existing entries. This is useful for finding the index of the first element that is strictly "greater than" `x`.

```python {export=src/codex/search/binary.py}
def bisect_right[T](
    x: T, items: Sequence[T], f: Ordering[T] = None
) -> int:
    if f is None:
        f = default_order

    l, r = 0, len(items)

    while l < r:
        m = (l + r) // 2
        if f(x, items[m]) < 0:
            r = m
        else:
            l = m + 1

    return l

```

In this variant, we only move the left boundary `l` forward if `x >= items[m]`, which pushes the search toward the end of a block of identical values.

Since both functions follow the same halving principle as standard binary search, their performance characteristics are identical:

* **Time Complexity**: $O(\log n)$, as we halve the search space in every iteration of the `while` loop.
* **Space Complexity**: $O(1)$, as we only maintain two integer indices regardless of the input size.

To ensure these boundaries are calculated correctly, especially with duplicate elements, we use the following test cases:

```python {export=tests/search/test_binary.py}
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

```

## Conclusion

Searching is arguably the most important problem in Computer Science. In this first chapter, we have only scratched the surface of this vast field, but in doing so, we have discovered one of the fundamental truths of computation: structure matters--a lot.

When we know nothing about the structure of our problem or the collection of items we are searching through, we have no choice but to rely on exhaustive methods like linear search. In these cases, we must check every single item to determine if it is the one we care about.

However, as soon as we introduce some structure--specifically, some *order*--the landscape changes completely. Binary search allows us to exploit this structure to find an element as fast as is theoretically possible, reducing our workload from a linear progression to a logarithmic one.

This realization that we can trade a bit of organizational effort for a massive gain in search efficiency is the perfect segue for our next chapter. If searching is easier when items are ordered, then we must understand the process of establishing that order. We must talk about **sorting**.
