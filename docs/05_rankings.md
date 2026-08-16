# Selection without sorting

You don't need to sort an array to find its median. You don't need to sort an array to find any rank — the smallest element, the largest, the 25th percentile, the 99th. Two algorithms find the $k$-th smallest element of an array in **linear time**, beating the $O(n \log n)$ cost of sorting by a full factor of $\log n$.

The local/global lens from the previous chapter still applies, with one twist. Quick sort, after partitioning around a pivot $p$, has to recurse on *both* sides — both halves need their local inversions fixed. Selection only has to recurse on *one* side: the side that contains the rank you're looking for. The other side stays unsorted forever and you don't care, because the answer you want isn't in it. Throwing away one of the two recursive calls collapses $O(n \log n)$ down to $O(n)$.

The first algorithm — quickselect — does this with a randomly chosen pivot and gets you to $O(n)$ on average, with a small probability of degenerating. The second — median of medians, also called BFPRT after its five inventors — chooses its pivot so carefully that it guarantees $O(n)$ even in the worst case. The contrast between them is the cleanest example I know of a recurring trade-off in algorithm design: randomization buys you simplicity; determinism buys you guarantees, at the cost of intricacy.

## Quickselect: only one side matters

Start with the partition step from the previous chapter. After `partition(items, lo, hi, order)` returns the pivot's final index $p$:

- Every element in `items[lo:p]` is smaller than `items[p]`.
- Every element in `items[p+1:hi]` is not smaller.
- `items[p]` is in its final sorted position.

The third fact is the one that matters here. If you're looking for the $k$-th smallest element of `items[lo:hi]`, and partition tells you the pivot landed at position $p$, you have three cases:

- $k = p$: the pivot *is* the answer. Return `items[p]` and you're done.
- $k < p$: the answer is somewhere in the left side, `items[lo:p]`. Recurse there.
- $k > p$: the answer is somewhere in the right side, `items[p+1:hi]`. Recurse there.

In two of the three cases, you recurse on only one side and ignore the other. That's the saving over quick sort, which always recurses on both.

I'll use a randomly chosen pivot — pick a uniformly random element from the interval and swap it into the last position before partitioning. This is the standard randomization trick for quickselect, and it's what makes the average-case analysis work out cleanly regardless of input distribution.

```python {export=src/codex/select/quick.py}
import random
from typing import MutableSequence
from codex.types import Ordering, default_order
from codex.sort.quick import partition


def quickselect[T](
    items: MutableSequence[T], k: int, order: Ordering[T] = default_order
) -> T:
    """Return the k-th smallest element of items (0-indexed).

    Modifies items in place as a side effect of partitioning. If you don't
    want that, pass list(items) instead of items.
    """
    if not 0 <= k < len(items):
        raise IndexError(f"k={k} out of range for sequence of length {len(items)}")
    return _quickselect(items, 0, len(items), k, order)
```

The public wrapper does the bounds check and kicks off the recursion. The recursion itself takes explicit `lo` and `hi` so it can work in place on shrinking sub-ranges without copying.

```python {export=src/codex/select/quick.py}
def _quickselect[T](
    items: MutableSequence[T], lo: int, hi: int, k: int, order: Ordering[T]
) -> T:
    if hi - lo == 1:
        return items[lo]
    # Random pivot: swap a random element into the last position.
    pivot_idx = random.randint(lo, hi - 1)
    items[pivot_idx], items[hi - 1] = items[hi - 1], items[pivot_idx]
    p = partition(items, lo, hi, order)
    if k == p:
        return items[p]
    elif k < p:
        return _quickselect(items, lo, p, k, order)
    else:
        return _quickselect(items, p + 1, hi, k, order)
```

The body is recognizably quick sort, with two recursive calls collapsed to one based on which side of the pivot the target rank $k$ falls on. The base case is a single element: if the interval has length 1, that element *is* the $k$-th smallest, by definition.

```python
import random
random.seed(42)  # make the output reproducible

from codex.select.quick import quickselect

items = [3, 1, 4, 1, 5, 9, 2, 6]
print(quickselect(list(items), 0))   # 1 — smallest element
print(quickselect(list(items), 3))   # 3 — 4th smallest (k=3 is 0-indexed)
print(quickselect(list(items), 7))   # 9 — largest element
print(quickselect(list(items), len(items) // 2))  # 4 — median (lower of two for even n)
```

Now the cost analysis. With a random pivot, the expected pivot position is the middle of the interval. So on average each recursive call halves the interval size: $T(n) = T(n/2) + O(n)$. The $O(n)$ is the partition cost; the recursion does the same work on half the data.

Unroll the recurrence: $T(n) = O(n) + O(n/2) + O(n/4) + \cdots = O(n) \cdot (1 + 1/2 + 1/4 + \cdots) = O(2n) = O(n)$.

The geometric series is the magic. The first partition costs $n$; the second costs $n/2$; the third $n/4$; and so on. Sum the infinite geometric series and you get $2n$, which is still linear. **The recursion is logarithmic in depth but the total work is linear**, because the work at each level halves. The quick sort recurrence $T(n) = 2T(n/2) + O(n)$ doesn't collapse this way because the two recursive calls together do as much work as the parent, not half. Killing one of those calls is exactly the difference between $\log n$ levels of $n$ work (= $n \log n$) and $\log n$ levels of geometrically-shrinking work (= $n$).

That's the expected case. The worst case is unfortunately not so kind. If you keep picking the smallest element as pivot, the partition is unbalanced — one side has $n-1$ elements, the other has zero. The recursion becomes $T(n) = T(n-1) + O(n)$, which is $O(n^2)$. With a random pivot, this catastrophe requires an adversary to predict every random choice, which they can't, so the expected behavior dominates with overwhelming probability. But the worst case isn't $O(n)$; it's $O(n^2)$.

To get a *guaranteed* $O(n)$ worst case, you need to pick pivots in a way that can't be foiled by any input. That's median of medians.

## The pivot you can trust: median of medians

The problem with quickselect's worst case is the pivot. A "bad" pivot — one near the smallest or largest element — leaves an almost-everything-on-one-side partition, and the recursion does $\Theta(n)$ work on an interval barely smaller than the original. To get a guaranteed $O(n)$, you need a pivot that's *guaranteed* to lie somewhere in the middle of the array — say, between the 30th and 70th percentile — so that each recursive call sees an interval of at most $0.7n$ elements.

A median would be ideal, but finding a median is the problem you're trying to solve. That sounds circular, and it almost is. The trick — the elegant move of the BFPRT algorithm — is to find an *approximate* median that's *good enough* to be a pivot, using a recursive call on a *smaller* problem.

Here's the construction.

1. Group the array into chunks of 5.
2. Find the median of each chunk (constant work per chunk, since each has just 5 elements).
3. Collect the chunk-medians into a list of size $n/5$.
4. Recursively find the median of that list. Call it $p$.
5. Use $p$ as the pivot for partition.

The pivot $p$ is the *median of medians* — the middle element of the chunk-medians. It's not the true median of the original array, but it's close enough. The bound is:

**At least $30\%$ of the elements are smaller than $p$**, and **at least $30\%$ are larger.** So whichever side of the partition you have to recurse on, the recursive call sees at most $70\%$ of the elements you started with.

Why $30\%$? There are $n/5$ chunks. Half of them — that is, $n/10$ chunks — have their median smaller than $p$ (since $p$ is the median of the chunk-medians). In each of those chunks, the chunk-median is the third-smallest of its five elements, which means *two more* elements in that chunk are also smaller than the chunk-median, and hence smaller than $p$. So each such chunk contributes 3 elements that are smaller than $p$: $n/10$ chunks × 3 elements = $3n/10$, which is $30\%$. The symmetric argument gives $30\%$ larger.

That's the geometric guarantee. With pivot $p$ chosen this way, the recursion satisfies $T(n) = T(7n/10) + T(n/5) + O(n)$. The $T(n/5)$ is the recursive call to find the median of medians; the $T(7n/10)$ is the recursive selection on the larger of the two partition sides. Both fractions are constants, and their sum $7/10 + 1/5 = 9/10 < 1$, so the recurrence collapses to $O(n)$ — the same geometric trick as quickselect, just with the constant $9/10$ instead of $1/2$. The depth of the recursion is $O(\log n)$, but the work decays geometrically across levels and the total is linear.

The chunk size of 5 isn't arbitrary. Smaller doesn't work: with chunks of 3, the analogous calculation gives $T(n) = T(2n/3) + T(n/3) + O(n)$, whose fractions sum to $1$, which fails to collapse and gives $O(n \log n)$. Chunks of 5 are the smallest odd size for which the sum of fractions is strictly less than $1$. Larger chunks would also work but make the constant factor worse — 5 hits the sweet spot.

Now the code. I'll write the selection function out of place — it returns a value rather than rearranging the input — because the pedagogical clarity is worth the $O(n)$ extra space. The move that matters is the recurrence, not the in-place trick.

```python {export=src/codex/select/deterministic.py}
from typing import Sequence
from codex.types import Ordering, default_order
from codex.sort.basic import insertion_sort


def select[T](
    items: Sequence[T], k: int, order: Ordering[T] = default_order
) -> T:
    """Return the k-th smallest element of items in worst-case O(n) time."""
    if not 0 <= k < len(items):
        raise IndexError(f"k={k} out of range for sequence of length {len(items)}")
    return _select(list(items), k, order)
```

The public wrapper validates `k` and copies the input (so the recursion can freely mutate it without surprising the caller). The recursion does the real work:

```python {export=src/codex/select/deterministic.py}
def _select[T](items: list[T], k: int, order: Ordering[T]) -> T:
    if len(items) <= 5:
        # Base case: sort and pick. Insertion sort is cheap on tiny inputs.
        insertion_sort(items, order)
        return items[k]

    # Find a good pivot via median of medians.
    pivot = _median_of_medians(items, order)

    # Three-way partition by value. Equality goes into its own bucket so the
    # k-equals-many-pivots case has a clean home.
    lo = [x for x in items if order(x, pivot) < 0]
    eq = [x for x in items if order(x, pivot) == 0]
    hi = [x for x in items if order(x, pivot) > 0]

    if k < len(lo):
        return _select(lo, k, order)
    elif k < len(lo) + len(eq):
        return pivot  # k falls inside the run of equal pivots
    else:
        return _select(hi, k - len(lo) - len(eq), order)
```

Three-way partition by *value* (using list comprehensions) rather than the Lomuto in-place partition from chapter 4. The three buckets are `lo` (strictly smaller than the pivot), `eq` (equal to it), and `hi` (strictly larger). The recursion then knows exactly which bucket contains rank $k$ and how to adjust $k$'s value for the recursive call.

The pivot itself comes from `_median_of_medians`, which is the heart of the algorithm:

```python {export=src/codex/select/deterministic.py}
def _median_of_medians[T](items: list[T], order: Ordering[T]) -> T:
    medians = []
    for start in range(0, len(items), 5):
        group = list(items[start:start + 5])
        insertion_sort(group, order)
        medians.append(group[len(group) // 2])
    if len(medians) == 1:
        return medians[0]
    # Recurse to find the median of the medians.
    return _select(medians, len(medians) // 2, order)
```

Group the array into chunks of 5, sort each chunk with insertion sort (which is genuinely the right tool for a 5-element list — chapter 3's analysis of insertion sort on near-sorted small inputs shows up here as the right tool), collect the medians, and recursively select the median of that list. The recursion bottoms out when there are five or fewer chunk-medians, at which point the base case of `_select` sorts and returns.

```python
from codex.select.deterministic import select

items = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4]
print(select(items, 0))                  # 1 — smallest
print(select(items, len(items) - 1))     # 9 — largest
print(select(items, len(items) // 2))    # 5 — median

# Deterministic — no randomness, every call returns the same answer
print(select(items, 7))   # 4 — same answer every time
print(select(items, 7))   # 4
```

## The three questions, applied

### Is it correct?

Both algorithms are correct via a straightforward inductive argument. Assume the recursive call returns the correct answer on the smaller subproblem; then **quickselect** is correct because after partition, the pivot's final position $p$ tells you exactly which side of the array contains rank $k$, and the recursion descends into that side with the rank unchanged (or adjusted, in the right-side case, to account for the elements being skipped). **Median of medians** is correct by the same argument applied to its three-way partition: rank $k$ is either in `lo` (recurse, unchanged $k$), or in the equal bucket (the pivot is the answer), or in `hi` (recurse with $k$ shifted by `len(lo) + len(eq)`). The base case (a single element or a list of $\leq 5$) is trivially correct.

### How efficient is it?

**Quickselect** is $O(n)$ expected time, with $O(n^2)$ worst case in the unlucky event of consistently bad pivots. Space is $O(\log n)$ on average — the recursion stack — because each recursive call works on a sub-interval of the same array.

In plain words for the expected case: each level of recursion does work proportional to the *current* interval size, and the expected interval size halves each level. Sum $n + n/2 + n/4 + \ldots = 2n$. Linear, with a constant factor of about 2. The "2" is the sum of the geometric series — it's why halving works and tripling doesn't.

**Median of medians** is $O(n)$ worst-case. The recurrence is $T(n) = T(n/5) + T(7n/10) + O(n)$, and since $1/5 + 7/10 = 9/10 < 1$, the geometric sum converges and gives $T(n) = O(n)$. The constant factor is much larger than quickselect's — roughly 10×, because the algorithm does the partition, *plus* the median-of-medians computation, *plus* the recursive selection. In practice, you use quickselect; median of medians exists for the worst-case question.

Space is $O(n)$ for the out-of-place version implemented here (the three-way partition creates new lists). An in-place version exists but is intricate enough that it would have obscured the recurrence at the centre of the algorithm. The asymptotic time complexity is the same either way.

### Is it optimal?

Yes, and the argument is the cheapest in the chapter: **any algorithm that finds the $k$-th smallest element of an array must inspect every element**, because if it didn't, an adversary could place the answer at the position it missed. Same argument as the adversary argument for linear search in chapter 1. So $\Omega(n)$ is the lower bound; $O(n)$ is what both quickselect (on average) and median of medians (worst case) achieve. Tightly optimal in both senses.

## Recurse on one side

Quickselect and median of medians are correct via clean recursive arguments — partition + recurse on the side containing $k$, base case is trivial. Quickselect runs in expected $O(n)$ with a small chance of $O(n^2)$; median of medians runs in worst-case $O(n)$ with a larger constant factor. Both are optimal — you cannot find the $k$-th smallest element of an array without inspecting every element.

When you can recurse on only one side instead of two, the cost collapses from $O(n \log n)$ to $O(n)$. The same partition operation — same $O(n)$ work, same local-vs-global inversion structure — gives you $O(n \log n)$ if you recurse on both sides (sorting) and $O(n)$ if you recurse on only one (selection). The difference between $T(n) = 2T(n/2) + O(n)$ and $T(n) = T(n/2) + O(n)$ is exactly the difference between log-linear and linear. The geometric sum that the second recurrence produces is the cleanest expression of *"do the work, then do strictly less of it, recursively"* — and it shows up again and again in the rest of the book, every time an algorithm gets to throw away most of its remaining work after a constant-fraction reduction.

Quickselect is short, readable, fast in practice; the price is a tiny probability of going quadratic. Median of medians is intricate, careful, and guaranteed; the price is a 10× constant factor in real-world cases. Most production code uses quickselect (or some hybrid). Most algorithm courses teach median of medians, because the existence of a worst-case linear selection algorithm is one of the most surprising results in the field. They're both worth knowing.

In the next chapter, the question shifts again. So far every algorithm in this book has been *comparison-based* — the only thing it knows about its input is how to compare two elements. The decision-tree lower bound from chapter 4 said that comparison-based sorting can't be faster than $\Omega(n \log n)$. The next chapter shows you can sort in *linear* time if you're willing to give up the comparison-only restriction — by using the values themselves as positions in memory. It's the cleanest example in the book of how a model's constraint dictates its lower bound.

## Notes and further reading

Quickselect is Tony Hoare's 1961 invention, published as a companion piece to quick sort. Median of medians is the **BFPRT algorithm**, named for its five inventors: Manuel Blum, Robert Floyd, Vaughan Pratt, Ron Rivest, and Robert Tarjan, who published the worst-case linear selection result in 1973 — a paper still worth reading for the elegance of the proof. CLRS (4th ed.) §9.2 covers quickselect; §9.3 covers median of medians. Sedgewick's *Algorithms* (4th ed.) §2.5 covers quickselect in production-friendly form. The expected-linear-time analysis of randomized quickselect via the partition-size recurrence is in CLRS §9.2; Motwani and Raghavan's *Randomized Algorithms* (1995) gives a more thorough probabilistic treatment. The choice of group size 5 in median-of-medians is famously the smallest odd group that makes the recursive fractions sum to less than 1; group size 3 fails, group size 7 works but with a worse constant.
