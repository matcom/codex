# Intervals as objects

Chapter 19's heap used index arithmetic over a flat array to keep one question cheap: where is the minimum? I want to push that "structure-implied-by-the-layout" idea further and answer a question the heap can't: given an array of numbers, what is the sum (or min, or max) of an arbitrary contiguous range, and how do I keep that answer cheap when the underlying values change?

**Every node owns an interval, and the answer to any range query is the sum of the $O(\log n)$ canonical intervals that tile it.** A segment tree is what you get when you stop thinking about array indices and start thinking about intervals as first-class objects. The structure gives point-update plus range-query in $O(\log n)$ per operation, and the harder case — range-update plus range-query — yields to **lazy propagation**, a technique that defers work until someone asks for it.

## Updates cheap or queries cheap — pick one

You have an array of $n$ numbers — call them $a_0, a_1, \ldots, a_{n-1}$ — and you need to support two operations in any order, any number of times.

1. **Update** one position: set $a_i$ to a new value.
2. **Query** a range: return the sum (or min, or max, or xor) of $a_l, a_{l+1}, \ldots, a_{r-1}$.

You have two naive approaches, each handling one operation beautifully and the other terribly.

**Approach 1: store the array as-is.** Updating $a_i$ is one assignment, $O(1)$. Querying a range walks the range, $O(r - l)$. Cheap update, expensive query.

**Approach 2: store prefix sums.** Maintain $P_k = a_0 + a_1 + \cdots + a_{k-1}$. Now a range sum is one subtraction, $O(1)$. But updating $a_i$ shifts every prefix sum from $P_{i+1}$ onward by the same delta, so you rewrite the right half of the array. $O(n)$ per update.

For a mixed workload of comparable updates and queries, both approaches degrade to $O(n)$ amortized per operation, which is the cost of doing nothing clever at all. The segment tree gives you $O(\log n)$ for **both**. On an array of a million elements, both update and query cost about twenty steps; on a billion, about thirty.

## Every node owns an interval

The array's index range $[0, n)$ is one big interval, recursively split in half. The root node owns $[0, n)$. Its left child owns $[0, n/2)$; its right child owns $[n/2, n)$. The recursion bottoms out at intervals of length one, where each leaf owns one array position and stores its value.

Every internal node stores the aggregate (sum, min, …) of the values in its interval. The root stores the aggregate over $[0, n)$; a node owning $[2, 5)$ stores $a_2 + a_3 + a_4$. The invariant I'll maintain is: **every internal node's stored value equals the aggregate of its two children's stored values.**

That recursive split is a balanced binary tree of height $\lceil \log_2 n \rceil$, with $n$ leaves and at most $n - 1$ internal nodes, so at most $2n - 1$ in total. I lay them out in an array the same way chapter 19's heap did: the root at index 1, the children of index `node` at `2 * node` and `2 * node + 1`. I use index 1 (not 0) so the child formula needs no `+1` corrections.

When $n$ isn't a power of two, the recursive split is still well-defined (you split at the midpoint of each interval), but the implicit-tree index range can exceed $2n - 1$. The safe over-allocation is $4n$ slots; that always fits, by a one-paragraph induction on the recursion depth. I use **half-open intervals** $[l, r)$ throughout, following Python's idiom (the convention `list[l:r]` follows), so the midpoint split partitions $[lo, mid) \cup [mid, hi)$ with no overlap.

A range query like "sum of $[3, 11)$" doesn't visit every leaf in $[3, 11)$ — that would be $O(n)$. It visits at most $O(\log n)$ internal nodes whose intervals together *tile* $[3, 11)$ exactly. Each visited node returns its stored aggregate in $O(1)$, and I sum them. The tiling is what makes the query logarithmic.

## Walking down to update, three cases to query

The constructor takes the data and an aggregation `op` with its identity element (0 for sum, $-\infty$ for max, etc.).

```python {export=src/codex/trees/segment.py}
from collections.abc import Sequence
from typing import Callable


class SegmentTree[T]:
    def __init__(
        self,
        data: Sequence[T],
        op: Callable[[T, T], T] | None = None,
        identity: T | None = None,
    ) -> None:
        if op is None:
            op = lambda a, b: a + b  # type: ignore[assignment,return-value]
        if identity is None:
            identity = 0  # type: ignore[assignment]
        self._n = len(data)
        self._op: Callable[[T, T], T] = op
        self._identity: T = identity  # type: ignore[assignment]
        self._tree: list[T] = [identity] * (4 * max(self._n, 1))  # type: ignore[list-item]
        if self._n > 0:
            self._build(1, 0, self._n, list(data))

    def __len__(self) -> int:
        return self._n
```

My defaults (addition and zero) make `SegmentTree(data)` a sum-aggregate tree out of the box. Anything else (min, max, xor, gcd) needs its own `op` and `identity` passed in. The build walks the implicit tree top-down, splitting each interval at its midpoint until the leaves hold the array values; on the way back up, each internal node aggregates its two children.

```python {export=src/codex/trees/segment.py}
    def _build(self, node: int, lo: int, hi: int, data: list[T]) -> None:
        if hi - lo == 1:
            self._tree[node] = data[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, data)
        self._build(2 * node + 1, mid, hi, data)
        self._tree[node] = self._op(self._tree[2 * node], self._tree[2 * node + 1])
```

The recursion visits each of the $\le 2n - 1$ nodes once with $O(1)$ work apiece, so I get a $\Theta(n)$ build. Linear in the data size, not in the tree's height.

To update position $i$, I walk from the root down to the leaf owning that position, then back up, recomputing each ancestor's aggregate from its now-corrected children.

```python {export=src/codex/trees/segment.py}
    def update(self, i: int, value: T) -> None:
        self._update(1, 0, self._n, i, value)
```

The recursive helper figures out whether $i$ falls in the left half or the right half and recurses into that half only; I leave the other half untouched. After the recursive call returns, I recompute the current node's aggregate from its two children.

```python {export=src/codex/trees/segment.py}
    def _update(
        self, node: int, lo: int, hi: int, i: int, value: T
    ) -> None:
        if hi - lo == 1:
            self._tree[node] = value
            return
        mid = (lo + hi) // 2
        if i < mid:
            self._update(2 * node, lo, mid, i, value)
        else:
            self._update(2 * node + 1, mid, hi, i, value)
        self._tree[node] = self._op(self._tree[2 * node], self._tree[2 * node + 1])
```

You can see the walk visits exactly one node per level, descending into the half containing $i$ and ignoring the other. Tree height is $O(\log n)$, so update is $O(\log n)$ time and $O(\log n)$ stack frames. Updating one position in a million-element tree touches about twenty nodes.

To compute the range-query aggregate over $[l, r)$ from a node owning $[lo, hi)$, three cases come up. **Disjoint**: the two intervals don't overlap, so the node contributes nothing; return the identity. **Contained**: the node's interval lies entirely inside the query, so the stored aggregate is exactly what I want. **Crossing**: partial overlap, so recurse on both children and combine.

```python {export=src/codex/trees/segment.py}
    def query(self, l: int, r: int) -> T:
        return self._query(1, 0, self._n, l, r)

    def _query(self, node: int, lo: int, hi: int, l: int, r: int) -> T:
        if r <= lo or hi <= l:
            return self._identity
        if l <= lo and hi <= r:
            return self._tree[node]
        mid = (lo + hi) // 2
        left_val = self._query(2 * node, lo, mid, l, r)
        right_val = self._query(2 * node + 1, mid, hi, l, r)
        return self._op(left_val, right_val)
```

The three-case split is the heart of the algorithm. Disjoint lets me prune whole subtrees that contribute nothing. Contained stops the recursion at the deepest node still entirely inside the query; that node *is* a canonical tile. Crossing is the only case that descends, and it only happens on the $O(\log n)$ nodes along the *boundaries* of the query range.

A power-of-two array of eight values, with queries before and after a point update:

```python
from codex.trees.segment import SegmentTree

data = [1, 3, 5, 7, 9, 11, 13, 15]
st: SegmentTree[int] = SegmentTree(data)

# Whole-array sum — one node visited, the root
print(f"query(0, 8) = {st.query(0, 8)}")    # 64 — the root's value, one tile

# A three-element interior range — sum of positions 2, 3, 4
print(f"query(2, 5) = {st.query(2, 5)}")    # 21 = 5 + 7 + 9

# A single-element "range" — query of [0, 1)
print(f"query(0, 1) = {st.query(0, 1)}")    # 1 — the leaf for position 0

# Update position 3 from 7 to 100; the change propagates up to the root
st.update(3, 100)
print(f"after update(3, 100), query(2, 5) = {st.query(2, 5)}")  # 114 = 5 + 100 + 9
```

You see three queries with different shapes (the whole array, an interior range, a single element), each answered in $O(\log n)$ time. The update touched the leaf for position 3 and recomputed the four ancestors back up to the root.

The same structure handles arbitrary associative aggregates; sum is just the default. Pass `op=max` and an identity safe for max (`float('-inf')` when values are non-negative), and the same nodes, walks, and three-case query give you range maximum.

```python
import math
from codex.trees.segment import SegmentTree

data = [1, 3, 5, 7, 9, 11, 13, 15]

# Same data, but ask for range maximum. The op flips from + to max,
# and the identity flips from 0 to -infinity (the max-identity element).
st_max: SegmentTree[float] = SegmentTree(data, op=max, identity=-math.inf)

# Max over the interior range — should be 9, the largest of 5, 7, 9
print(f"max query(2, 5) = {st_max.query(2, 5)}")    # 9

# Max over the whole array — the last element
print(f"max query(0, 8) = {st_max.query(0, 8)}")    # 15
```

The aggregate flipped from sum to max with one argument. The segment tree isn't a sum tree, it's an *associative-monoid* tree. Anything you can combine with an associative operation that has an identity (sum, min, max, xor, gcd, bitwise-and, matrix product) plugs straight in. Only the per-node combine step changes.

## Range update, point query — flip the roles

The dual problem swaps the roles. Updates are now over ranges (say, "add 5 to every element in $[l, r)$") and queries ask for a single element. A segment tree handles this in $O(\log n)$ per operation too: each node stores a **delta** ("this much should be added to every element in my interval"), a range update adds the delta to each tile of the canonical decomposition, and a point query at position $i$ sums the deltas along the root-to-leaf path.

The lazy version below subsumes this case; call `query(i, i+1)` for point-query semantics.

## Defer the work until somebody asks

The combined problem (range update *and* range query, both $O(\log n)$) is where the segment tree earns its complexity. Both operations need to touch many tree nodes, and the trick is to make the touching cheap.

The idea is **lazy**. When a range update fully contains a node's interval, I want to record "every element under this node should be increased by `delta`" and stop, rather than walk down to the leaves. So I add a parallel array, `lazy[node]` per node, that records pending updates not yet pushed down. `tree[node]` is kept in sync with the current aggregate *assuming the lazy values above the node have been applied*; `lazy[node]` records updates that affect the subtree but haven't been propagated to the children yet.

The invariant: **`tree[node]` is the correct aggregate for the node's interval, accounting for all lazy values at this node and at every ancestor, but not yet for any lazy values stored at descendants.** Every operation that descends through a node pushes its lazy value down first.

```python {export=src/codex/trees/segment.py}
class LazySegmentTree:
    def __init__(self, data: Sequence[int]) -> None:
        self._n = len(data)
        size = 4 * max(self._n, 1)
        self._tree: list[int] = [0] * size
        self._lazy: list[int] = [0] * size
        if self._n > 0:
            self._build(1, 0, self._n, list(data))

    def __len__(self) -> int:
        return self._n

    def _build(self, node: int, lo: int, hi: int, data: list[int]) -> None:
        if hi - lo == 1:
            self._tree[node] = data[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, data)
        self._build(2 * node + 1, mid, hi, data)
        self._tree[node] = self._tree[2 * node] + self._tree[2 * node + 1]
```

I'm committing this lazy variant to sum-with-range-add. Generalizing to arbitrary monoids with arbitrary range updates is possible but delicate, because the update has to commute with the aggregate in a specific way. Sum-and-add is the cleanest case.

Two small helpers do the lazy machinery. `_apply` adds a `delta` to a node, updating its stored aggregate by `delta * interval_length` (the sum over an interval of length $k$ increases by $\delta k$) and stacking the delta into the node's lazy slot. `_push_down` flushes a node's lazy value into its two children before recursing into either.

```python {export=src/codex/trees/segment.py}
    def _apply(self, node: int, lo: int, hi: int, delta: int) -> None:
        self._tree[node] += delta * (hi - lo)
        self._lazy[node] += delta

    def _push_down(self, node: int, lo: int, hi: int) -> None:
        if self._lazy[node] != 0:
            mid = (lo + hi) // 2
            self._apply(2 * node, lo, mid, self._lazy[node])
            self._apply(2 * node + 1, mid, hi, self._lazy[node])
            self._lazy[node] = 0
```

`_push_down` is the only place the lazy slot gets cleared. After it, the parent's aggregate is still correct (the parent already accounted for the delta), and the children's aggregates plus their new lazy slots reflect the pending update.

Range update is the disjoint / contained / crossing trichotomy again, with contained using `_apply` to mark the subtree lazily.

```python {export=src/codex/trees/segment.py}
    def update(self, l: int, r: int, delta: int) -> None:
        self._update(1, 0, self._n, l, r, delta)

    def _update(
        self, node: int, lo: int, hi: int, l: int, r: int, delta: int
    ) -> None:
        if r <= lo or hi <= l:
            return
        if l <= lo and hi <= r:
            self._apply(node, lo, hi, delta)
            return
        self._push_down(node, lo, hi)
        mid = (lo + hi) // 2
        self._update(2 * node, lo, mid, l, r, delta)
        self._update(2 * node + 1, mid, hi, l, r, delta)
        self._tree[node] = self._tree[2 * node] + self._tree[2 * node + 1]
```

The contained case is what makes my range update logarithmic: `_apply` marks the subtree in $O(1)$ and the recursion stops. Crossing only happens along $O(\log n)$ nodes near the update range's boundaries.

Range query is structurally identical to the non-lazy version, with one new line: push down before descending.

```python {export=src/codex/trees/segment.py}
    def query(self, l: int, r: int) -> int:
        return self._query(1, 0, self._n, l, r)

    def _query(self, node: int, lo: int, hi: int, l: int, r: int) -> int:
        if r <= lo or hi <= l:
            return 0
        if l <= lo and hi <= r:
            return self._tree[node]
        self._push_down(node, lo, hi)
        mid = (lo + hi) // 2
        left = self._query(2 * node, lo, mid, l, r)
        right = self._query(2 * node + 1, mid, hi, l, r)
        return left + right
```

The push-down inside `_query` keeps the invariant intact: before descending into a child, the parent's pending update has to land there, so whatever the child reports is consistent with every update issued so far.

Range-add plus range-sum on a fresh array of eight ones:

```python
from codex.trees.segment import LazySegmentTree

# All ones — initial sum over the whole array is 8
lst = LazySegmentTree([1, 1, 1, 1, 1, 1, 1, 1])
print(f"initial query(0, 8) = {lst.query(0, 8)}")   # 8

# Add 5 to every element in [3, 7) — that's positions 3, 4, 5, 6
lst.update(3, 7, 5)

# Whole-array sum is now 8 + 4*5 = 28
print(f"after add 5 to [3, 7): query(0, 8) = {lst.query(0, 8)}")   # 28

# A range fully inside the updated region — two elements, each now 6
print(f"query(3, 5) = {lst.query(3, 5)}")   # 12 = 6 + 6

# A range outside the updated region — positions 0, 1, 2 are still 1 each
print(f"query(0, 3) = {lst.query(0, 3)}")   # 3

# A range crossing the updated boundary — positions 6 (updated) and 7 (not)
print(f"query(6, 8) = {lst.query(6, 8)}")   # 7 = 6 + 1
```

The range update touched $O(\log n)$ canonical-tile nodes and stopped. Subsequent queries pushed lazy values down only along the paths they descended, never the whole tree. Five operations, all $O(\log n)$, all correct.

## The three questions, applied

### Is it correct?

The non-lazy `SegmentTree` is correct because the invariant "every internal node's stored value is the aggregate over its interval" is maintained by every operation. `_build` establishes it bottom-up. `_update` walks down to one leaf and recomputes ancestors on the way back up; every visited ancestor's children are now consistent. `_query` uses the three-case split — disjoint contributes the identity, contained returns the stored aggregate, crossing recurses — and the three cases tile the query range exactly once, by induction on tree depth.

The `LazySegmentTree` is correct because its invariant ("`tree[node]` reflects every lazy update at this node or above it, none strictly below") is maintained pointwise. `_apply` updates `tree[node]` and `lazy[node]` together. `_push_down` clears `lazy[node]` by applying it to both children; afterward the children reflect what the parent's lazy slot demanded. Both `_update` and `_query` push down before descending, so descents see children consistent with every update the parent knew about. The contained case in `_update` is where the laziness earns its keep: it marks the subtree with one $O(1)$ step, and any future descent into that subtree will push the mark down before doing anything else, so no stale aggregate ever escapes.

### How efficient is it?

The cost table for an array of $n$ elements:

| Operation | Time | Extra space |
|-----------|------|-------------|
| `SegmentTree(data)` (build) | $\Theta(n)$ | $\Theta(n)$ |
| `update(i, v)` | $O(\log n)$ | $O(\log n)$ stack |
| `query(l, r)` | $O(\log n)$ | $O(\log n)$ |
| `LazySegmentTree.update(l, r, d)` | $O(\log n)$ | $O(\log n)$ |
| `LazySegmentTree.query(l, r)` | $O(\log n)$ | $O(\log n)$ |

The $O(\log n)$ bound on query has a tight argument. A range query at $[l, r)$ visits a tree node if the node's interval overlaps the query but isn't contained in it (crossing), or if it contributes directly (contained). The contained nodes form the canonical tile decomposition; at most 4 per level can appear (two near the left boundary, two near the right), for at most $4 \log n$ total. Crossing nodes are their ancestors, also $O(\log n)$. Per-node work is $O(1)$.

On a million-element array both operations touch about $4 \log_2(10^6) \approx 80$ tree nodes; on a billion, about 120. Storage is $\Theta(n)$: the $4n$ over-allocation absorbs index slack for non-power-of-two $n$, and the lazy variant doubles that with the `_lazy` array.

### Is it optimal?

For the point-update + range-query workload, $O(\log n)$ per operation is asymptotically optimal in the cell-probe model. A structure supporting $n$ updates and $n$ queries must do $\Omega(n \log n)$ total work (Patrascu and Demaine, 2006); if a single operation were $o(\log n)$, $2n$ operations would do $o(n \log n)$, contradicting the bound. The same argument applies to range update + range query, and the lazy segment tree matches it.

You can sometimes do better with extra assumptions. If updates are *only* increments and queries are *only* sums, a **Fenwick tree** (chapter 22) matches the same $O(\log n)$ bound with half the code and a smaller constant. If queries only ever cover the whole array, the problem trivializes to a counter. The segment tree's $O(\log n)$ is the price of supporting *arbitrary* ranges with *arbitrary* associative aggregates and *arbitrary* updates; drop any of those and a more specialized structure can do better.

## The layout is the algorithm

Every node owns an interval, and the answer to any range query is the sum of the $O(\log n)$ canonical intervals that tile it. Once that lands the rest is bookkeeping.

The right abstraction is sometimes an interval, not an index. The naive approaches think about indices; the segment tree gives every interval a node, and range queries become one lookup instead of $n$. The shift from "which position?" to "which interval?" is what turns a linear-time scan into a logarithmic-time descent.

Laziness is a structural technique, not just a syntactic one. A range update marks $O(\log n)$ tiles and stops; the marks only propagate when a subsequent query forces them. The same idea powers garbage collection, copy-on-write file systems, and database query planners — deferred work that materializes only on demand.

A segment tree is a flat array under index arithmetic, chapter 19's trick again. What changes is what each slot stores. The implicit-binary-tree-over-flat-array pattern has been the backbone of three consecutive chapters; chapter 22 makes it four.

Chapter 22 takes the segment tree's range-sum capability and asks: can the same workload be solved with half the code? The answer is yes, by giving up generality. A **Fenwick tree** handles prefix sums (and therefore range sums by subtraction) in $O(\log n)$, using a single array of size $n$ and a bit-manipulation trick on the lowest set bit.

## Notes and further reading

The segment tree was introduced by Jon Louis Bentley in 1977 in his Stanford technical report on computational geometry, though Bentley's original application was *interval stabbing* (given a query point, find all stored intervals containing it), not the range-aggregate problem of this chapter. The transposition to range aggregates is folklore in the competitive-programming community and doesn't have a canonical paper. CLRS doesn't cover segment trees directly, and neither does Sedgewick & Wayne's *Algorithms* (4th ed.); the structure is treated as specialized in the canonical undergraduate textbooks. The actual canon is the competitive-programming literature: the CP-Algorithms encyclopedia entry at [cp-algorithms.com/data_structures/segment_tree.html](https://cp-algorithms.com/data_structures/segment_tree.html) is the definitive reference, covering the basic structure, lazy propagation, the iterative bottom-up variant, persistent segment trees, and several advanced extensions. The Codeforces tutorials on the platform's "EDU" section work through the same material with problem sets. For the lower-bound argument above, see Mihai Patrascu and Erik Demaine's 2006 "Logarithmic Lower Bounds in the Cell-Probe Model" (*SIAM Journal on Computing* 35(4):932–963). The Fenwick tree's lowest-bit trick that chapter 22 builds on is Peter Fenwick's 1994 *Software: Practice and Experience* paper "A New Data Structure for Cumulative Frequency Tables."
