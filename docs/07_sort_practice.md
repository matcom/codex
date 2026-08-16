# Sorting, in practice

Every algorithm in this book so far has been measured asymptotically — by how the cost grows with input size, ignoring constants. That's the right model for theoretical analysis and the wrong model for production code. By the time you call `sorted()` on a list of one thousand elements, the constants matter more than the asymptotic order, and the asymptotic order is a constraint, not a recipe.

This chapter is about what real implementations of sorting do, and it's a quiet vindication of the previous five chapters. The algorithms used in production — **introsort** in C++'s `std::sort`, **Timsort** in Python's `sorted()` and Java's `Arrays.sort` and Rust's `slice::sort` — aren't new inventions. They're compositions of the algorithms you already have. Insertion sort for small subarrays. Quicksort for the recursive divide. Merge sort for stable, predictable behavior. The art of practical sorting is knowing *which* move applies *where*, and stitching them together so each one operates only on inputs it's optimal for.

Two production-style sorting algorithms — a simplified introsort and a simplified Timsort — show how the techniques from chapters 3 through 5 compose for real-world performance. **A practical sort algorithm is a composition, not a choice.** You don't pick merge sort or quick sort or insertion sort. You pick which algorithm runs on which part of the input, and you let each one do what it's best at.

## Why insertion sort earns its place

Asymptotically, insertion sort is $O(n^2)$ and merge sort is $O(n \log n)$. For large $n$, merge sort wins. For small $n$, the asymptotic comparison lies to you.

The reason is the constant factor. Merge sort allocates auxiliary arrays, recurses, and does index bookkeeping; each of those operations costs real time per element. Insertion sort, on a list of 8 elements that's already nearly sorted, runs a tight loop of comparisons and a couple of swaps — no recursion, no allocation, almost nothing but linear walks through cache-warm memory. On a 16-element subarray, insertion sort beats merge sort and quicksort by a factor of 2 to 4 in real wall-clock time, despite being asymptotically slower.

The exact crossover point varies by language, hardware, and even the data being sorted, but a cutover threshold somewhere between 8 and 32 is the conventional sweet spot. CPython's Timsort uses 32. C++'s `std::sort` typically uses 16. The choice is empirical: every implementation benchmarks its own.

The practical recipe writes itself: when the recursion gets down to a small subarray, stop recursing and call insertion sort directly. The asymptotic order doesn't change — large inputs still need an $O(n \log n)$ algorithm — but the constant factor improves dramatically because every leaf of the recursion tree is now an efficient straight-line loop instead of an inefficient recursive call.

```python {export=src/codex/sort/practice.py}
from typing import MutableSequence
from codex.types import Ordering, default_order


def _insertion_sort_range[T](
    items: MutableSequence[T], lo: int, hi: int, order: Ordering[T]
) -> None:
    """In-place insertion sort on items[lo:hi]. Tight loop, no recursion."""
    for i in range(lo + 1, hi):
        j = i
        while j > lo and order(items[j], items[j - 1]) < 0:
            items[j], items[j - 1] = items[j - 1], items[j]
            j -= 1
```

This is the same insertion sort from chapter 3, parameterized to work on a sub-range instead of the whole array — which is what the recursive callers need. It's the building block for everything else in this chapter.

## Introsort: quicksort with safety nets

David Musser introduced introsort in 1997 to solve a real problem with quicksort: its $O(n^2)$ worst case, which random-pivot selection makes improbable but not impossible. The "intro" stands for *introspective*: introsort runs quicksort normally, watches its own recursion depth, and bails out to a different algorithm if the depth grows past a sane threshold — the signal that the pivot choices have been unlucky and the algorithm is degenerating toward quadratic behavior.

The full Musser algorithm has three pieces:

1. **Quicksort** as the main algorithm — top-down recursion, partition around a pivot, recurse on each side.
2. **Insertion sort** for small subarrays (the corner-cut from the previous section).
3. **Heapsort** as a fallback when the recursion depth exceeds $2 \log_2 n$ — a guarantee against $O(n^2)$.

The third piece needs heapsort, which I haven't introduced yet (it lands in Part III, where heaps get their proper treatment). For this chapter's simplified introsort, I'll skip the heapsort fallback and only implement the first two pieces. The result is "introsort without the safety net" — fine for inputs that aren't adversarially constructed, which is the vast majority of real-world inputs. The depth limit and heapsort fallback are a one-paragraph addition once you have a heap, and I'll add that pointer in the notes at the end.

```python {export=src/codex/sort/practice.py}
import random
from codex.sort.quick import partition


def introsort[T](
    items: MutableSequence[T],
    order: Ordering[T] = default_order,
    insertion_cutoff: int = 16,
) -> None:
    """Introsort-lite: quicksort with insertion-sort cutover for small subarrays.

    The original Musser introsort also tracks recursion depth and falls back
    to heapsort beyond 2*log2(n) levels; that piece needs heaps (Part III)
    and is omitted here.
    """
    _introsort(items, 0, len(items), order, insertion_cutoff)


def _introsort[T](
    items: MutableSequence[T],
    lo: int,
    hi: int,
    order: Ordering[T],
    cutoff: int,
) -> None:
    if hi - lo <= cutoff:
        _insertion_sort_range(items, lo, hi, order)
        return
    pivot_idx = random.randint(lo, hi - 1)
    items[pivot_idx], items[hi - 1] = items[hi - 1], items[pivot_idx]
    p = partition(items, lo, hi, order)
    _introsort(items, lo, p, order, cutoff)
    _introsort(items, p + 1, hi, order, cutoff)
```

The structure is exactly the quicksort from chapter 4 with two changes: a random pivot (since this is meant to be production-grade), and an insertion-sort cutover when the subarray is small.

```python
from codex.sort.practice import introsort

items = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4]
introsort(items)
print(items)   # sorted in place

# Large random input — the realistic case
import random as _random
_random.seed(0)
big = [_random.randint(0, 1000) for _ in range(10000)]
introsort(big)
print(big[:10], "...", big[-10:])   # sorted, ends with the largest values
```

C++'s `std::sort` has used a full introsort since around 1997, which is why C++ programmers can call it on any container without worrying about $O(n^2)$ behavior — the depth limit catches the pathological cases and switches to heapsort, which is $O(n \log n)$ guaranteed. The composition — quicksort + insertion sort + heapsort — covers every input regime: large gets quicksort, small gets insertion sort, pathological gets heapsort.

## Timsort: merge sort that sees the runs

Tim Peters wrote Timsort in 2002 for Python's `list.sort()`, after noticing two structural facts about real-world inputs that the comparison-based lower bound argument from chapter 4 ignored:

1. **Real data has runs.** Files arrive sorted by timestamp; database records arrive sorted by primary key; user-facing lists arrive partially sorted because users edit them incrementally. A genuinely random input is the rare case; the common case has long ascending (or descending, which you reverse) subsequences already in place.
2. **Bottom-up merge sort avoids recursion overhead.** Instead of recursively splitting until you reach single elements and then merging back up, start by treating each element (or each natural run) as already-sorted, and merge pairwise upward until one sorted whole remains.

Timsort combines both insights: identify the natural runs in the input, extend short ones with insertion sort to a minimum length, then merge the runs bottom-up using a careful merge strategy that keeps the run sizes balanced. The result is **$O(n)$ on already-sorted input** — Timsort detects the single big run and merges nothing — and $O(n \log n)$ on random input, with constants that benchmark beautifully on real-world data.

The full Tim Peters algorithm has more moving pieces than this chapter has room for: a run stack with invariants that govern when to merge, a galloping mode that — when one side of a merge keeps winning — jumps ahead in binary-search steps instead of advancing one element at a time, and careful handling of descending runs. I'll implement a simplified version that captures the two core ideas — insertion-sort for short chunks plus bottom-up merging — and skip the run-detection optimization, which I'll add a paragraph about at the end.

The merge step itself is the merge from chapter 4, retargeted to operate on a range of the array rather than two separate lists:

```python {export=src/codex/sort/practice.py}
def _merge_range[T](
    items: MutableSequence[T],
    lo: int,
    mid: int,
    hi: int,
    order: Ordering[T],
) -> None:
    """Merge items[lo:mid] and items[mid:hi] in place. Both halves must be sorted."""
    left = list(items[lo:mid])
    right = list(items[mid:hi])
    i = j = 0
    k = lo
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

The simplified Timsort itself has two phases. First, sort fixed-size chunks (the "min runs") with insertion sort. Second, merge the chunks pairwise, doubling the run size each time, until one sorted run remains.

```python {export=src/codex/sort/practice.py}
def timsort_lite[T](
    items: MutableSequence[T],
    order: Ordering[T] = default_order,
    min_run: int = 32,
) -> None:
    """Timsort-lite: bottom-up merge sort with insertion-sort runs.

    The real Timsort (Tim Peters, 2002) also detects natural runs in the
    input and uses a run-stack with merge invariants; both refinements are
    described in the chapter prose and omitted here.
    """
    n = len(items)
    if n < 2:
        return

    # Phase 1: sort fixed-size chunks with insertion sort.
    for start in range(0, n, min_run):
        end = min(start + min_run, n)
        _insertion_sort_range(items, start, end, order)

    # Phase 2: bottom-up merge of the sorted chunks.
    size = min_run
    while size < n:
        for left_start in range(0, n, 2 * size):
            mid = min(left_start + size, n)
            right_end = min(left_start + 2 * size, n)
            if mid < right_end:
                _merge_range(items, left_start, mid, right_end, order)
        size *= 2
```

```python
from codex.sort.practice import timsort_lite

items = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4]
timsort_lite(items)
print(items)   # sorted in place

# Stability check — equal keys preserve their relative order
pairs = [(1, 'a'), (3, 'b'), (1, 'c'), (3, 'd'), (2, 'e'), (1, 'f')]
timsort_lite(pairs, lambda x, y: -1 if x[0] < y[0] else (1 if x[0] > y[0] else 0))
print(pairs)   # (1, 'a'), (1, 'c'), (1, 'f'), (2, 'e'), (3, 'b'), (3, 'd')
```

The real Timsort goes further on a single dimension that matters enormously in practice. Before phase 1, it walks the input once looking for **natural runs** — maximal ascending sequences that are already in the data. Each natural run becomes a unit; only short runs get extended by insertion sort to the minimum length. The merge phase then operates on a mix of natural runs (potentially much longer than `min_run`) and forced-min-run chunks, and the run-stack with merge invariants keeps the merge tree balanced. The result is **adaptive**: input that's already sorted runs in $O(n)$ time, input that's reverse-sorted runs in $O(n)$ (because reverse runs get detected and flipped), and input with even a small amount of structure runs faster than random input. CPython, OpenJDK, and Rust all ship versions of the full algorithm.

## The three questions, applied

### Is it correct?

Both algorithms reduce to compositions of correct algorithms from previous chapters. **Introsort** is quicksort with an insertion-sort fallback for small subarrays. Quicksort's correctness (chapter 4) covers the recursive case; insertion sort's correctness (chapter 3) covers the base case. The cutover threshold doesn't affect correctness — only performance. **Timsort-lite** is insertion sort on the first level of small chunks, followed by stable bottom-up merging. Insertion sort's correctness covers phase 1; merge's correctness (chapter 4) covers phase 2; the stability of merge ensures that each level of merging preserves the order that the previous level established.

Stability splits the two. Introsort isn't stable — quicksort isn't, and the insertion-sort cutover doesn't restore it — but Timsort-lite is, because insertion sort and merge are both stable. The full Timsort is stable for the same reason.

### How efficient is it?

**Introsort-lite** is $O(n \log n)$ expected with the random pivot, $O(n^2)$ in the unlikely worst case (which the full Musser introsort upgrades to $O(n \log n)$ worst-case via heapsort fallback). Space is $O(\log n)$ for the recursion stack. The insertion-sort cutover doesn't change the asymptotic complexity; it improves the constant factor by reducing the per-recursion overhead at the leaves of the recursion tree.

**Timsort-lite** is $O(n \log n)$ worst-case and $O(n)$ on already-sorted input (because the first level of merging finds adjacent chunks already in order and the merge has no work to do beyond the linear scan). Space is $O(n)$ — the merge phase allocates auxiliary buffers proportional to the chunk size at each level. The full Timsort retains the $O(n \log n)$ worst-case and improves the best-case behavior on partially-structured input through the run-detection mechanism.

In production code, the asymptotic order ($O(n \log n)$) tells you what doesn't change as inputs scale; the constants tell you what does. Practical sorts win by attacking the constants — by using insertion sort where its tiny constant beats merge sort's overhead, by going bottom-up to skip recursion frames, by detecting natural runs to skip work entirely. The asymptotic analysis from chapter 4 didn't disappear; it became the floor, not the ceiling.

### Is it optimal?

Within the comparison model, both algorithms hit the $\Omega(n \log n)$ lower bound from chapter 4. Neither is asymptotically better than merge sort or quick sort. **What introsort and Timsort are *optimal at* is real-world wall-clock performance** — they pay attention to constants, cache behavior, and input structure that the asymptotic analysis didn't see. They're optimal in a richer model than the comparison model: a model that includes constant factors, branch prediction, and the long pre-sorted runs that real data tends to contain.

That's the chapter's punch. The comparison lower bound is a theoretical constraint, but practice operates inside a much richer cost model than the comparison model captures. Production sorting wins by exploiting structure the theoretical analysis ignored.

## Compose, don't choose

Introsort and Timsort are correct because they're compositions of algorithms you've already verified. Both run in $O(n \log n)$, with Timsort hitting $O(n)$ on inputs that are already sorted. Both improve the constant factor of theoretical sorts by orders of magnitude in practice, by using insertion sort where it wins on small inputs and by exploiting the structure of real-world data that the theoretical lower bound doesn't see.

In production code you don't pick *an* algorithm; you compose several — insertion sort for the leaves, quicksort for the divide, merge sort for stability, heapsort as the safety net. Each one runs only on the regime it's best for. The practitioner's skill is recognizing which technique applies where and composing them without scrambling each one's invariants.

This idea — that asymptotic optimality is necessary but not sufficient — is going to come back throughout the rest of the book. Hash tables in Part II use open addressing, chaining, or both, depending on load factor. Balanced trees in Part III use rotations to keep the worst case bounded while running fast on average. Graph search in Part V uses different traversal orders depending on the question being asked. In every case, the theoretical algorithm is the starting point, not the destination. Real software stitches the moves together for the inputs it sees.

The next short essay takes inventory of what Part I taught — structure as the secret ingredient, the cynosure of inversions, recursion and randomization as design weapons, lower bounds belonging to models, and the composition principle this chapter just landed.

## Notes and further reading

Introsort was introduced by David Musser in 1997 in *"Introspective Sorting and Selection Algorithms,"* Software: Practice and Experience 27(8). The paper is short and worth reading; the depth-limited fallback to heapsort is the genuinely original idea. C++'s `std::sort` adopted introsort soon after, which is why C++ programmers since the late 1990s have had a single sort function with $O(n \log n)$ worst-case guarantees.

Timsort was developed by Tim Peters for CPython in 2002. Peters wrote a long [design document](https://github.com/python/cpython/blob/main/Objects/listsort.txt) that's still in the CPython source tree and remains the best primary reference. The full algorithm — with run detection, merge-stack invariants, and galloping mode — is also implemented in OpenJDK (since Java 7) and Rust's standard library. Timsort was famously the subject of a formal-verification effort: de Gouw et al. (2015) used the KeY theorem prover to verify Java's Timsort implementation and discovered a real bug in the merge-stack invariant maintenance, which had been hiding in production code in three major language runtimes for years. The bug-fix patch was 4 lines.

CLRS doesn't cover practical sorting in any depth; its focus is the theoretical lower bound. Sedgewick & Wayne's *Algorithms* (4th ed.) §2.3 has a production-flavored quicksort treatment that hints at introsort. The CPython source — `Objects/listobject.c` and `Objects/listsort.txt` — is the canonical reference for Timsort details if you want to see how the full algorithm looks in idiomatic C.
