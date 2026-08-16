# Throwing half away

You have a phone book — the kind people used to keep next to the phone, sorted alphabetically — and you need to find one name. You don't read it cover to cover. You open it somewhere in the middle, see whether the name you want comes before or after the page in front of you, then throw away half the book and open the remaining half in the middle. Repeat until you're holding the right page.

This is binary search. It has three forms: a straight "is $x$ in the sequence?" answer, a *bisection* that returns an insertion point, and — most usefully — a way to search the answer space of any problem with monotonic structure. That third form is the one that keeps paying off through the rest of the book.

**Every comparison cuts the search space in half.** For a sorted list of one million items, that's about twenty comparisons to find anything; for a billion items, about thirty. Doubling the input adds *one comparison*, not doubles the time. Linear search would scan all billion items. Binary search reads thirty of them and tells you the answer with certainty.

## The half-and-half algorithm

The mechanics are exactly the phone-book strategy. Keep two indices, `lo` and `hi`, marking the bounds of the part of the sequence you haven't ruled out yet. As long as the interval is non-empty, look at the middle and use one comparison to throw away one half.

```python {export=src/codex/search/binary.py}
from typing import Sequence
from codex.types import Ordering, default_order


def binary_search[T](
    x: T, items: Sequence[T], order: Ordering[T] = default_order
) -> int | None:
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        cmp = order(x, items[mid])
        if cmp == 0:
            return mid
        elif cmp < 0:
            hi = mid - 1
        else:
            lo = mid + 1
    return None
```

The three branches are doing exactly what the phone book was doing. If the middle item *is* the target, you're done. If the target is smaller, the right half (everything from `mid` onward) is ruled out, so `hi` moves to `mid - 1`. If the target is larger, the left half is ruled out, so `lo` moves to `mid + 1`. The loop exits when `lo > hi` — at that point the interval is empty and the target was never in the sequence to begin with.

```python
from codex.search.binary import binary_search

items = [1, 3, 5, 7, 9, 11, 13, 15]
print(binary_search(7, items))     # 3 — found at index 3
print(binary_search(8, items))     # None — not present
print(binary_search(1, items))     # 0 — first element, edge case
print(binary_search(15, items))    # 7 — last element
print(binary_search(5, []))        # None — empty input
```

`mid = (lo + hi) // 2` uses integer division, which always rounds toward `lo` — that's important for termination, because it guarantees `mid < hi` whenever `lo < hi`, so the `lo = mid + 1` branch makes real progress. The other detail is that the input *must* be sorted in the order that `order` defines. If you pass an unsorted list, binary search gives you garbage with confidence. There's no easy way for the algorithm to detect this — sorting is a precondition, not something the function checks. If you want a safety net, sort first and document the contract loudly.

## Finding insertion points: `bisect_left` and `bisect_right`

`binary_search` answers a yes-or-no question with a position attached. But there's a closely related question that turns out to be more useful in practice: **where *would* this item go, if I were to insert it while keeping the sequence sorted?**

That position exists whether or not the item is already present. If you're adding a new entry to an already-sorted list, you don't want "is it there?" — you want "where do I put it?" And if the item is *already* there in duplicates, you have a contract decision to make: do you return the position *before* the first equal element, or *after* the last one?

The standard convention — the one Python's `bisect` module uses, and the one I'll use here — gives you both. `bisect_left` returns the leftmost spot where the item could be inserted while keeping the list sorted. `bisect_right` returns the rightmost. For a list with no duplicates of the target, the two return the same answer; for a list with duplicates, they bracket the run.

```python {export=src/codex/search/binary.py}
def bisect_left[T](
    x: T, items: Sequence[T], order: Ordering[T] = default_order
) -> int:
    lo, hi = 0, len(items)
    while lo < hi:
        mid = (lo + hi) // 2
        if order(items[mid], x) < 0:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

The shape is recognizably binary search, but the loop condition is `lo < hi` (not `<=`) and `hi` shrinks to `mid` (not `mid - 1`). That's because the answer is now an *insertion index*, which can legally be one past the end of the list — so the search space is `[0, len(items)]`, and the loop converges when `lo == hi`.

`bisect_right` is the same skeleton with one comparison flipped.

```python {export=src/codex/search/binary.py}
def bisect_right[T](
    x: T, items: Sequence[T], order: Ordering[T] = default_order
) -> int:
    lo, hi = 0, len(items)
    while lo < hi:
        mid = (lo + hi) // 2
        if order(items[mid], x) <= 0:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

The only change from `bisect_left` is the `<=` instead of `<`. When the middle item equals the target, `bisect_left` treats it as "the run starts here or earlier" and moves left; `bisect_right` treats it as "the run ends here or later" and moves right. One bit of difference, two different answers.

```python
from codex.search.binary import bisect_left, bisect_right

items = [1, 3, 3, 3, 5, 7]
print(bisect_left(3, items))       # 1 — leftmost spot for a 3 (before the run)
print(bisect_right(3, items))      # 4 — rightmost spot for a 3 (after the run)
print(bisect_left(4, items))       # 4 — between the 3s and the 5; same for both
print(bisect_right(4, items))      # 4
print(bisect_left(0, items))       # 0 — smaller than everything, goes at the start
print(bisect_right(8, items))      # 6 — larger than everything, goes at the end
```

The pair `(bisect_left, bisect_right)` doesn't just answer *where to insert*. It also gives you, almost for free, the **count** of an element in a sorted sequence — just subtract: `bisect_right(x, items) - bisect_left(x, items)`. That's $O(\log n)$ instead of the $O(n)$ count you wrote in the last chapter. Structure delivers twice.

## Searching the answer, not the data

So far I've used binary search to find something in a sequence. But the actual algorithm doesn't care whether you have a sequence at all. The only thing it needs is a *monotonic comparison* — a question whose answer flips from one value to another exactly once over the range you're searching. The "sequence" part was just one way to give that monotonic structure to a problem.

Here's the generalization. Suppose you have a predicate $P(k)$ — a function that takes an integer and returns a boolean — and you know that $P$ is **monotonic**: there's some threshold below which $P$ is `True` and above which $P$ is `False`. Binary search can find that threshold without you ever materializing a sequence.

```python {export=src/codex/search/binary.py}
from typing import Callable


def binary_search_predicate(
    predicate: Callable[[int], bool],
    lo: int,
    hi: int,
) -> int:
    """
    Return the largest integer in [lo, hi] for which predicate is True,
    assuming predicate is True on some prefix [lo, k] and False on [k+1, hi].
    Returns lo - 1 if no value satisfies the predicate.
    """
    while lo <= hi:
        mid = (lo + hi) // 2
        if predicate(mid):
            lo = mid + 1
        else:
            hi = mid - 1
    return hi
```

The body is almost identical to `binary_search` — same `lo`/`hi`/`mid` machinery, same halving — but instead of comparing the target to a sequence element, you evaluate the predicate at `mid` and use its boolean answer to decide which half to discard. The function returns `hi` at termination because, after the loop, `hi` ends up pointing at the largest satisfier (the search has narrowed past the boundary).

The canonical use is **integer square root** — the largest integer $k$ such that $k^2 \leq n$. The predicate is monotonic: as $k$ grows, $k^2 \leq n$ stays `True` until you cross the root, then stays `False` forever. Binary search finds the boundary.

```python {export=src/codex/search/binary.py}
def integer_sqrt(n: int) -> int:
    if n < 0:
        raise ValueError("integer_sqrt requires n >= 0")
    return binary_search_predicate(lambda k: k * k <= n, 0, n)
```

```python
from codex.search.binary import integer_sqrt

print(integer_sqrt(10))    # 3 — because 3*3 = 9 ≤ 10 < 16 = 4*4
print(integer_sqrt(16))    # 4 — exact square
print(integer_sqrt(0))     # 0 — boundary
print(integer_sqrt(2**40)) # 1048576 — works fine on huge inputs, ~40 iterations
```

For $n = 2^{40}$, the search range is $[0, 2^{40}]$, and the loop terminates in roughly $\log_2(2^{40}) = 40$ iterations. That's the binary-search speedup applied to a problem that never had a sorted sequence in the first place — just a question with monotonic structure.

This pattern shows up everywhere. *"What's the smallest server count that handles peak load?"* — monotonic. *"What's the largest learning rate that converges?"* — monotonic. *"What's the maximum bandwidth the network can sustain?"* — monotonic. Any time the answer to a yes/no question stays the same once it flips, binary search on the answer is in play.

## The three questions, applied

### Is it correct?

`binary_search` is correct because of an invariant the loop preserves: **if $x$ is anywhere in `items`, it's somewhere in `items[lo:hi+1]`**. That's true at the start, when the interval is the whole sequence. Each iteration looks at `items[mid]`, and the three branches preserve the invariant: if `items[mid] == x`, the function returns; if `x < items[mid]`, then $x$ (if present) can't be at index $\geq \text{mid}$, so `hi = mid - 1` is still a valid invariant; symmetric for the other branch. When the loop exits with `lo > hi`, the interval is empty — which, by the invariant, means $x$ was never in `items`.

The same loop-invariant argument carries over to `bisect_left` (the invariant is *"the leftmost insertion point is in `[lo, hi]`"*) and to `binary_search_predicate` (the invariant is *"the threshold is in `[lo - 1, hi]`"*). One algorithmic shape, three closely related contracts.

### How efficient is it?

Every iteration cuts the interval in half. The interval starts at length $n$ and shrinks geometrically: after $k$ iterations, its length is at most $n / 2^k$. The loop exits when the length hits zero, which happens once $2^k \geq n$ — that is, $k \geq \log_2 n$. So the loop runs at most $\lceil \log_2 n \rceil$ times, giving $O(\log n)$ time. Space is $O(1)$ — just the two indices and the loop locals.

The tactile re-statement: binary search makes one comparison per *doubling of the input*. A million-item list takes about 20 comparisons; a billion takes about 30; a quintillion takes about 60. The logarithm is the answer to *"how many times do I have to double 1 before I reach n?"* — and for the inputs you care about in real life, that answer is always small.

### Is it optimal?

This is the chapter's punch. **No comparison-based search algorithm on a sorted array can do better than $\lceil \log_2(n+1) \rceil$ comparisons in the worst case**, and binary search hits that bound exactly.

The argument is the **decision-tree lower bound**. Any algorithm that makes only comparisons can be drawn as a binary decision tree: each internal node is a comparison, and each leaf is one of the possible outcomes the algorithm distinguishes. There are $n + 1$ possible outcomes here — the target is at index 0, or at index 1, …, or at index $n - 1$, or not present at all. A binary tree of depth $k$ has at most $2^k$ leaves, so to fit $n + 1$ leaves you need depth $\geq \lceil \log_2(n + 1) \rceil$. That's the worst-case path through the tree, and therefore the worst-case number of comparisons any comparison-based algorithm must make.

Binary search achieves $\lceil \log_2(n + 1) \rceil$ comparisons in the worst case. It's tightly optimal — within the comparison model on a sorted sequence, there is no better algorithm waiting to be discovered.

## Information per comparison

Binary search is correct because the invariant *"if $x$ is in the sequence, it's still in the current interval"* survives every iteration. It runs in $O(\log n)$ time and $O(1)$ space. And it's optimal: the decision-tree lower bound says no comparison-based algorithm on a sorted array can do better than $\lceil \log_2(n+1) \rceil$ comparisons in the worst case, and binary search meets that bound exactly.

The principle that goes beyond binary search itself: **every useful comparison must rule out a constant fraction of the remaining possibilities**. Linear search rules out one element per comparison, a fraction that shrinks to zero as $n$ grows. Binary search rules out half — a constant fraction, independent of $n$. The first gives you $O(n)$; the second gives you $O(\log n)$. The gap between them is exactly the gap between *information per comparison* and *information per element*.

That principle is going to come back. Every $O(\log n)$ algorithm in the rest of the book — the balanced trees in Part III, the heap operations, the segment-tree queries — earns its logarithm by ruling out a constant fraction of remaining work per step. Binary search is the simplest case; recognising the same shape elsewhere is most of the skill.

The next chapter flips the question: how do you create the order that binary search exploited?

## Notes and further reading

Binary search is treated formally in CLRS (4th ed.) §2.3 in its recursive divide-and-conquer form; the iterative form used here is the one Knuth analyzes in *The Art of Computer Programming* Vol. 3 §6.2.1, where he famously notes that the first correct published binary search appeared in 1962, sixteen years after the first published incorrect one. Python's `bisect` module in the standard library is the canonical reference implementation for `bisect_left` and `bisect_right` — worth reading the CPython source for the off-by-one details. The predicate-based variant under the name "binary search on the answer" is the standard competitive-programming idiom; the CP-Algorithms website's article on binary search is a good catalogue of its variants.
