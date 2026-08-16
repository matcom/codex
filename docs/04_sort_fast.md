# Fixing inversions, many at a time

Two algorithms, both $O(n \log n)$, both solving the same problem from opposite ends. Merge sort sorts each half recursively *first*, then weaves the two sorted halves together. Quick sort partitions the array around a pivot *first*, then sorts each side recursively. These two strategies aren't independent inventions. They're **duals** — two ways of attacking the same structural problem in opposite orders.

The lens that makes the duality visible is the distinction between **local** and **global** inversions. Once you have the lens, the two algorithms stop looking like rival inventions and start looking like the two natural strategies — fix the locals first, or fix the globals first — for any divide-and-conquer sort.

**Each merge step and each partition step fixes a number of inversions proportional to how much work the step did.** That linearity is the swap from one inversion per operation to as many inversions as the operation can see. The first cost you $O(n^2)$ in the previous chapter; the second buys you $O(n \log n)$ here. The factor of $\log n$ instead of $n$ between the two regimes is what divide-and-conquer buys you.

## Two kinds of inversions, two orders of attack

Take any array and split it in half at some midpoint $m$. Every inversion in the array — every pair $(i, j)$ with $i < j$ and $\text{items}[i] > \text{items}[j]$ — falls into exactly one of three buckets:

- **Local to the left half**: both $i$ and $j$ are in `items[0:m]`. Both elements live on the same side of the split.
- **Local to the right half**: both $i$ and $j$ are in `items[m:n]`. Same idea on the other side.
- **Global** (or **cross**): $i$ is in the left half, $j$ is in the right. The pair straddles the split.

Add the three counts up and you get the total inversion count of the array. To sort the array, you have to drive all three buckets to zero.

Here's the fact: **any divide-and-conquer sort that splits the array into two halves has to fix both kinds of inversion — local and global — and the algorithmic choice is which to fix first.**

- **Locals first.** Recursively sort each half, which fixes every local inversion (both halves end up sorted, with zero internal inversions). What's left is only cross-inversions. Then handle those in a linear sweep that combines the two sorted halves. This is **merge sort**.
- **Globals first.** Rearrange the array so every element of the left half is smaller than every element of the right half. That fixes every cross-inversion in one shot (there are now zero pairs straddling the split that are out of order). What's left is only local inversions within each side, which the recursive calls handle. This is **quick sort**.

The two algorithms aren't rival inventions. They're the two natural orders in which divide-and-conquer can resolve the inversion budget. Either order pays the same price: $O(n)$ work per level of recursion, $O(\log n)$ levels, total $O(n \log n)$. The work-per-level is linear because each merge or partition step is linear; the depth is logarithmic because each split halves the input. The product is the chapter.

## Merge sort: locals first, then weave

Start with the locals. Recursively sort the left half and the right half. After the two recursive calls return, both halves are sorted, which means **every local inversion has been resolved**. The only inversions that can still exist are cross-inversions — pairs that straddle the midpoint.

Now the conquer step. Two sorted sequences can be combined into one sorted sequence in linear time: keep one finger on the front of each, repeatedly compare the two fingers, pick the smaller one, and advance the finger that won. After at most $n$ comparisons you've consumed both lists.

```python {export=src/codex/sort/merge.py}
from typing import MutableSequence, Sequence
from codex.types import Ordering, default_order


def merge_sort[T](
    items: MutableSequence[T], order: Ordering[T] = default_order
) -> None:
    if len(items) <= 1:
        return
    mid = len(items) // 2
    left = list(items[:mid])
    right = list(items[mid:])
    merge_sort(left, order)
    merge_sort(right, order)
    merge(items, left, right, order)
```

The recursion splits at the midpoint, allocates two new lists for the halves (because the recursive calls would otherwise overwrite each other's work), sorts each half, and then merges them back into the original storage. The `merge` helper is where the cross-inversions die.

```python {export=src/codex/sort/merge.py}
def merge[T](
    items: MutableSequence[T],
    left: Sequence[T],
    right: Sequence[T],
    order: Ordering[T],
) -> None:
    i = j = k = 0
    while i < len(left) and j < len(right):
        if order(left[i], right[j]) <= 0:
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

Three loops. The first walks both halves in parallel, picking the smaller front element each time. The second and third handle whatever's left over once one side runs out. Each iteration of the first loop costs one comparison and writes one element; the cleanup loops are pure copies. Total work: linear in the combined length.

```python
from codex.sort.merge import merge_sort

items = [3, 1, 4, 1, 5, 9, 2, 6]
merge_sort(items)
print(items)   # [1, 1, 2, 3, 4, 5, 6, 9]

# Merge sort is stable on equal keys — the <= in the comparison picks left first when tied
items = [(1, 'a'), (2, 'b'), (1, 'c'), (2, 'd')]
merge_sort(items, lambda x, y: -1 if x[0] < y[0] else (1 if x[0] > y[0] else 0))
print(items)   # [(1, 'a'), (1, 'c'), (2, 'b'), (2, 'd')] — relative order of equals preserved
```

Now the inversion story. Look at the `else` branch in `merge` — the branch that picks from the right side. When `right[j]` gets taken before `left[i]`, that means `right[j] < left[i]`. But `left` is already sorted (the recursive call took care of that), so `left[i] <= left[i+1] <= ... <= left[len(left)-1]`. Which means `right[j]` is smaller than *every remaining element in the left half*.

That's not one cross-inversion fixed. That's $\text{len(left)} - i$ cross-inversions fixed, in a single operation. The merge step processes every cross-inversion the moment it picks from the right side, and there are at most $O(n)$ such picks for an array of size $n$. The whole merge is linear, and it resolves *every cross-inversion* in one pass.

That's the locals-first strategy at work. The recursive calls eliminated all the local inversions before the merge ran. The merge takes a sorted-left + sorted-right input — an array whose only remaining inversions are cross — and kills them in $O(n)$. Linear work, all the remaining inversions fixed. That's the source of the $\log n$ improvement over basic sorting.

## Counting inversions, for free, in $O(n \log n)$

The brute-force `count_inversions` from chapter 3 walked every pair in $O(n^2)$ — fine as a teaching aid, useless at scale. Merge sort gives you a much better algorithm almost free.

The insight is the one from the previous section. Every time `merge` picks from the right side, it has fixed $\text{len(left)} - i$ cross-inversions. If you instrument the merge to *count* those fixes instead of just executing them, you've counted every global inversion in the array. Recurse on the halves to count their internal inversions (locals) the same way, and you've counted the total: local-left + local-right + global.

```python {export=src/codex/sort/inversions.py}
from typing import MutableSequence, Sequence
from codex.types import Ordering, default_order


def count_inversions_fast[T](
    items: Sequence[T], order: Ordering[T] = default_order
) -> int:
    """Count inversions in O(n log n) via merge sort.

    Does not modify items; sorts a working copy internally.
    """
    work = list(items)
    return _merge_sort_counting(work, order)


def _merge_sort_counting[T](
    items: MutableSequence[T], order: Ordering[T]
) -> int:
    if len(items) <= 1:
        return 0
    mid = len(items) // 2
    left = list(items[:mid])
    right = list(items[mid:])
    count = _merge_sort_counting(left, order)
    count += _merge_sort_counting(right, order)
    count += _merge_counting(items, left, right, order)
    return count


def _merge_counting[T](
    items: MutableSequence[T],
    left: Sequence[T],
    right: Sequence[T],
    order: Ordering[T],
) -> int:
    count = 0
    i = j = k = 0
    while i < len(left) and j < len(right):
        if order(left[i], right[j]) <= 0:
            items[k] = left[i]
            i += 1
        else:
            items[k] = right[j]
            j += 1
            count += len(left) - i   # cross-inversions fixed by this pick
        k += 1
    while i < len(left):
        items[k] = left[i]
        i += 1
        k += 1
    while j < len(right):
        items[k] = right[j]
        j += 1
        k += 1
    return count
```

The structure is identical to merge sort. The only addition is the line `count += len(left) - i` inside the `else` branch — the one line that records *"this right-pick just resolved this many cross-inversions."* The recursive calls handle the local inversions inside each half by counting their own cross-inversions one level deeper. At every level of the recursion, you account for the globals of *that* level; sum across levels and you have the total.

```python
from codex.sort.inversions import count_inversions, count_inversions_fast

items = [3, 1, 4, 1, 5, 9, 2, 6]
print(count_inversions(items))        # 11 — brute force, O(n²)
print(count_inversions_fast(items))   # 11 — same answer, O(n log n)

# For 10,000 random items, the brute force version is slow enough to feel
# the difference; the fast one is essentially instantaneous
import random
big = [random.randint(0, 10000) for _ in range(10000)]
print(count_inversions_fast(big))     # ~25 million inversions on a random input
```

The same algorithmic shape, the same single comparison per merge step — and you got an extra answer for free. This is a recurring pattern in algorithm design: when a procedure already has a useful structural property (here, *"every right-pick resolves a known number of cross-inversions"*), small modifications can extract additional answers without changing the asymptotic cost.

## Quick sort: globals first, then sort each side

Same goal as merge sort, opposite order of attack. Instead of fixing the local inversions first via recursion and then weaving the halves together, quick sort fixes the global inversions first by rearranging the array, then handles the locals via recursion.

The rearrangement is the **partition** step. Pick a pivot element (I'll use the last element of the interval), then walk through the rest and swap things so everything smaller than the pivot lands to the pivot's left, everything not smaller lands to its right.

```python {export=src/codex/sort/quick.py}
from typing import MutableSequence
from codex.types import Ordering, default_order


def partition[T](
    items: MutableSequence[T], lo: int, hi: int, order: Ordering[T]
) -> int:
    """
    Lomuto partition over items[lo:hi]. Treats items[hi - 1] as the pivot.
    Rearranges in place so items smaller than the pivot end up left of it,
    items not smaller end up right. Returns the pivot's final index.
    """
    pivot = items[hi - 1]
    i = lo
    for j in range(lo, hi - 1):
        if order(items[j], pivot) < 0:
            items[i], items[j] = items[j], items[i]
            i += 1
    items[i], items[hi - 1] = items[hi - 1], items[i]
    return i
```

Two indices do the work. `j` walks through the interval looking for elements smaller than the pivot. `i` marks the right edge of the "smaller" region — every element to the left of `i` is already known to be smaller than the pivot. Whenever `j` finds another smaller element, swap it into position `i` and advance `i`. After the scan finishes, swap the pivot itself into position `i`, where it belongs.

Here's the global-inversions story. After `partition` returns the pivot's final index $p$, every element in `items[lo:p]` is strictly less than `items[p]`, and every element in `items[p+1:hi]` is at least `items[p]`. Which means: **every cross-inversion between the future left half (items below $p$) and the future right half (items at $p$ or above) is gone.** No pair of elements that straddles $p$ is out of order. The global inversion count, relative to the split at $p$, is now zero.

That's a lot of inversions cleaned up by one linear pass. The partition did $O(n)$ comparisons and a small number of swaps; in exchange, it fixed every cross-inversion involving the pivot's "side." What remains is the inversions inside each side — the locals — and the recursive calls handle those.

```python {export=src/codex/sort/quick.py}
def _quick_sort[T](
    items: MutableSequence[T], lo: int, hi: int, order: Ordering[T]
) -> None:
    if hi - lo < 2:
        return
    pivot_index = partition(items, lo, hi, order)
    _quick_sort(items, lo, pivot_index, order)
    _quick_sort(items, pivot_index + 1, hi, order)


def quick_sort[T](
    items: MutableSequence[T], order: Ordering[T] = default_order
) -> None:
    _quick_sort(items, 0, len(items), order)
```

The public `quick_sort` is just a thin wrapper that initializes the recursion bounds. The `_quick_sort` helper takes explicit `lo` and `hi` so the recursion can work in place on sub-ranges without copying. The structure perfectly mirrors merge sort, but read it in reverse: partition (the global-killing step) comes before the recursive calls (the local-killing steps), not after.

```python
from codex.sort.quick import quick_sort, partition

items = [3, 1, 4, 1, 5, 9, 2, 6]
quick_sort(items)
print(items)   # [1, 1, 2, 3, 4, 5, 6, 9]

# partition is exposed because the next chapter reuses it for quickselect
items = [3, 1, 4, 1, 5, 9, 2, 6]
p = partition(items, 0, len(items), lambda a, b: -1 if a < b else (1 if a > b else 0))
print(f"after partition: {items}, pivot ended at index {p}, value {items[p]}")
# Every element before p is < items[p]; every element after is >= items[p].
# Zero cross-inversions between the two sides — the globals are gone in one pass.
```

One thing to flag, because it'll matter in the analysis. The version of quick sort above always picks the **last element** of the interval as the pivot. That's the simplest possible pivot choice, and on random inputs it works beautifully. But on certain pathological inputs — already-sorted, reverse-sorted, or all-equal — it's catastrophically bad. Picking the last element of a sorted interval is the worst possible choice: the partition splits the array into one piece of size $n-1$ and one piece of size zero, the recursion becomes effectively linear, and quick sort degenerates to $O(n^2)$.

The standard fix is **random pivot selection** — pick a pivot uniformly at random from the interval, then swap it into the last position before partitioning. This makes worst-case behavior require a worst-case input *and* a worst-case sequence of random choices, which together happen with vanishing probability. The next chapter (on selection) shows the randomized version in full; the version here is the clearest exposition of the partition idea, and I'm keeping it that way on purpose.

## The three questions, applied

### Is it correct?

Both algorithms have clean recursive correctness arguments built on the local/global decomposition. For **merge sort**, the inductive case is: assume the recursive calls produce sorted halves (zero local inversions in each), then `merge` correctly weaves them into a sorted whole because it always picks the smaller of the two fronts — so any remaining cross-inversion would have to put the larger element first, which the algorithm refuses to do.

For **quick sort**, the invariant of `partition` does the work: after partition returns index $p$, every element in `items[lo:p]` is smaller than `items[p]`, and every element in `items[p+1:hi]` is not smaller. So `items[p]` is in its final sorted position, and the two recursive calls handle the two sides — which can only contain local inversions — independently.

In both cases, the base case (a sequence of length zero or one) has no inversions of any kind.

### How efficient is it?

**Merge sort** is $O(n \log n)$ time and $O(n)$ extra space, on every input. The recursion has depth $\log_2 n$ (each level halves the interval), and each level does $O(n)$ total work across all the merges at that level. Combine and you get $n \log n$. The space cost comes from the auxiliary `left` and `right` lists allocated in each recursive call — at any moment up to $O(n)$ of extra storage is live.

**Quick sort** is $O(n \log n)$ time *on average* and $O(\log n)$ extra space *on average* (just the recursion stack). The recursion depth depends on the pivot quality: a balanced pivot (close to the median) gives $\log_2 n$ depth, an unbalanced pivot gives more. On a uniformly random input with last-element pivot, the average depth is $O(\log n)$ and the average total work is $O(n \log n)$. On the pathological inputs flagged above, the depth becomes $O(n)$ and the total work becomes $O(n^2)$. **Random pivot selection makes the bad case a probabilistic curiosity rather than a structural risk.**

On the average case the two tie. They diverge on stability (merge sort preserves the relative order of equal keys; quick sort does not, at least in this implementation) and on memory (merge sort needs $O(n)$ scratch space; quick sort gets by with $O(\log n)$ stack frames).

### Is it optimal?

This is the chapter's punch, and it's a big one. **The comparison-based sorting lower bound is $\Omega(n \log n)$.** No algorithm that learns about its input only by comparing pairs of elements can sort an arbitrary input in fewer than $\Omega(n \log n)$ comparisons in the worst case. Merge sort meets this bound exactly; quick sort meets it on average. Within the comparison model, you cannot do asymptotically better than what this chapter just showed you.

The argument is the **decision-tree lower bound** for sorting, the same shape that gave the $\Omega(\log n)$ bound for searching in the previous chapter, scaled up. Any comparison-based sort can be drawn as a binary decision tree: each internal node is a comparison ("is `items[i] < items[j]`?"), each leaf is one specific output permutation. To handle every possible input correctly, the tree needs at least $n!$ leaves — one per possible input ordering. A binary tree with $L$ leaves has depth at least $\log_2 L$, so the depth is at least $\log_2(n!)$. By Stirling's approximation — the fact that $n!$ grows like $(n/e)^n$, so $\log_2(n!) \approx n\log_2 n$ — that depth is $\Theta(n \log n)$. The worst-case path through any such tree is $\Omega(n \log n)$ comparisons.

That's a strong statement. It says: comparison-based sorting can never be linear, no matter how clever the algorithm. The factor of $\log n$ over linear is **the price you pay for not knowing anything about the input except how its elements compare**. The next two chapters explore both sides of that price: selection (chapter 5) shows you can get partial sorted information faster than full sorting, and linear-time sorting (chapter 6) shows you can break the lower bound entirely if you give up the comparison-only restriction.

## Two orders, one cost

Merge sort and quick sort are correct via clean recursive arguments — sorted halves combine into a sorted whole; partition places the pivot in its final position. Both run in $O(n \log n)$, merge sort always and quick sort on average. And both are optimal: the decision-tree lower bound says no comparison-based sort can do better than $\Omega(n \log n)$ in the worst case, and these algorithms meet that bound.

The local-vs-global duality is the move that generalizes. Any divide-and-conquer sort that splits its input into two halves has to fix two kinds of inversions — local ones inside each half, global ones straddling the split — and the algorithmic choice is which order to fix them in. Merge sort fixes locals first via recursion, then kills the globals in one linear merge. Quick sort kills the globals first via partition, then fixes the locals via recursion. Either order works. Both pay the same $\log n$ factor for recursion depth, and both benefit from the same many-at-once trick at each level. The two algorithms are reflections of each other across the local/global divide.

The same inversion-counting argument from chapter 3 generalizes. Basic sorts fix one inversion per swap, so they're stuck at $O(n^2)$ because there can be that many inversions. Efficient sorts fix inversions in *blocks proportional to the work being done at each level* — a merge step does $O(n)$ work and resolves $O(n)$ cross-inversions; a partition step does $O(n)$ work and resolves all the pivot's cross-inversions in one swap. The trick that turns $n^2$ into $n \log n$ is exactly the trick of being credited for *all* the inversions you can see at this level, instead of just the one pair you happened to swap.

In the next chapter, the question shifts: what if you don't need the whole array sorted, but only the $k$-th smallest element? Quick sort already places one element per partition step in its final position. Selection turns out to require only one recursive call per level — not two — and the cost collapses from $O(n \log n)$ to $O(n)$.

## Notes and further reading

Merge sort goes back to John von Neumann (1945) and is treated in CLRS (4th ed.) §2.3 (introduction) and §4.4–4.5 (recurrence analysis). Quick sort was Tony Hoare's 1959 invention and is in CLRS §7; Sedgewick's *Algorithms* (4th ed.) §2.3 gives the cleanest production-style treatment with three-way partitioning and pivot-selection variants. The decision-tree lower bound is CLRS §8.1 — Stirling's approximation is the punch that turns $\log_2(n!)$ into $n \log n$. The $O(n \log n)$ inversion-counting variant of merge sort is a folklore observation that shows up as an exercise in nearly every algorithms textbook; the cleanest derivation I know is in Kleinberg & Tardos's *Algorithm Design* §5.3. Hoare's original Quicksort paper (1962) is short, lucid, and worth reading as a piece of historical algorithm prose. The local-vs-global inversion framing isn't standard textbook vocabulary, but it's the cleanest organizing lens I know for seeing merge sort and quick sort as duals — both are present implicitly in any thorough treatment of divide-and-conquer sorting.
