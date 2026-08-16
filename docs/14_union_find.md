# A forest where every element knows its root

You have a set of $n$ elements partitioned into some number of disjoint groups, and two operations: **`union(x, y)`** merges the groups containing $x$ and $y$, and **`connected(x, y)`** asks whether they're already in the same group. Sounds simple. The naive algorithm costs $O(n)$ per operation. Three optimizations bring it down to amortized $O(\alpha(n))$ — the inverse Ackermann function, at most 4 for any input you'll ever construct. The progression from naive to optimized is one of the most striking stories in algorithm design, and the destination is one of the most-used data structures in graph algorithms.

Each set is a tree: **a forest of parents**. The root of the tree names the set; every non-root element holds a pointer to its parent. `find` walks up to the root. `union` links two roots together. The whole story is about *making those trees flatter* — first by being clever about which root to link under which (union by rank), then by *retroactively* flattening the path you just walked (path compression). Together those two tricks collapse the trees so aggressively that the amortized cost per operation becomes the inverse Ackermann function. The result is a structure ready to plug into Kruskal's minimum-spanning-tree algorithm in Part V, where the union-find is the cycle-detection engine that makes the algorithm work at all.

## Merging groups, one at a time

The problem: maintain a partition of $\{0, 1, \ldots, n-1\}$ that starts in $n$ singleton sets and is gradually merged via `union` calls. At any moment, support `connected(x, y)` queries that ask whether $x$ and $y$ are in the same set.

The naive approach is to store each set as an explicit list of its members. `connected(x, y)` walks the list containing $x$ and checks for $y$ — $O(\text{set size})$. `union(x, y)` concatenates the two lists — $O(\text{smaller set size})$ if you're careful. Both operations grow expensive as sets get big.

Two cleaner approaches each fix one operation at the expense of the other.

## Quick-find: representative-as-label

The first idea: give every set a *representative* — a designated element that serves as the set's name — and store each element's representative in an array. Find the representative of $x$ in $O(1)$ by reading the array. To check connectivity, compare the two representatives in $O(1)$.

```python {export=src/codex/structures/union_find.py}
class QuickFind:
    def __init__(self, n: int) -> None:
        self._label = list(range(n))

    def find(self, x: int) -> int:
        return self._label[x]

    def connected(self, x: int, y: int) -> bool:
        return self._label[x] == self._label[y]
```

Initial state: element $i$ is its own representative (the array is $[0, 1, 2, \ldots, n-1]$). The contract is that two elements are in the same set iff they have the same label.

The cost is paid by `union`. To merge the set of $x$ into the set of $y$, every element currently labeled with $x$'s representative has to be relabeled with $y$'s — a linear sweep through the entire label array.

```python {export=src/codex/structures/union_find.py}
    def union(self, x: int, y: int) -> None:
        lx, ly = self._label[x], self._label[y]
        if lx == ly:
            return
        for i in range(len(self._label)):
            if self._label[i] == lx:
                self._label[i] = ly
```

$O(n)$ per `union`. That's the linear-sweep cost the data structure can't avoid: every element's representative is stored explicitly and independently, so every element has to be visited when the representative changes.

```python
from codex.structures.union_find import QuickFind

uf = QuickFind(n=10)
print(uf._label)                          # [0,1,2,3,4,5,6,7,8,9] — all singletons
uf.union(0, 1); uf.union(2, 3)
uf.union(0, 2)                            # merges {0,1} and {2,3}
print(uf._label)                          # everyone in {0,1,2,3} has the same label
print(uf.connected(1, 3))                 # True
print(uf.connected(1, 4))                 # False
```

Quick-find wins on `find` and loses on `union`. The naive partition-as-explicit-lists approach loses on both. The next variant flips the trade.

## Quick-union: forest of parents

The opposite idea: instead of storing each element's *representative*, store each element's *parent*. The representative of a set is the element at the root of its parent-tree: the one whose parent is itself. To find the representative of $x$, walk up the parent pointers until you hit a self-loop.

```python {export=src/codex/structures/union_find.py}
class QuickUnion:
    def __init__(self, n: int) -> None:
        self._parent = list(range(n))

    def find(self, x: int) -> int:
        while self._parent[x] != x:
            x = self._parent[x]
        return x

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)
```

`union` now becomes cheap: find both roots, point one at the other. Single pointer write.

```python {export=src/codex/structures/union_find.py}
    def union(self, x: int, y: int) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        self._parent[rx] = ry
```

The cost has moved from `union` to `find`. Both operations now cost $O(h)$, where $h$ is the height of the relevant tree. The catch is that $h$ can grow as large as $n$ in the worst case (*spaghetti trees*) if every union chains onto an already-tall tree.

A friendly union sequence wouldn't typically produce a chain — successive `union(i, i+1)` calls actually merge the trees flatly, because `union` always finds the root of each input tree before linking. The pathological shape happens when an adversarial sequence of operations always extends the same growing tree. To make the worst case visible, I'll bypass `union` and construct the chain by hand:

```python
from codex.structures.union_find import QuickUnion

uf = QuickUnion(n=10)
# manually construct a spaghetti chain: 0 → 1 → 2 → 3 → 4 → 5 → 6
for i in range(6):
    uf._parent[i] = i + 1

print(uf._parent[:7])                              # [1, 2, 3, 4, 5, 6, 6]
# find(0) walks 0 → 1 → 2 → 3 → 4 → 5 → 6 — six pointer hops
print(f"root of 0: {uf.find(0)}")                  # 6
```

That six-hop find is what happens when an adversary chains every union onto an existing root. The data structure is still correct, but it's been linearized. Each `find` walks the chain end-to-end.

The two optimizations in the next two sections — union by rank and path compression — each attack this failure mode. Either one alone improves the asymptotic bound dramatically. Together, they push it to inverse Ackermann.

## Union by rank: keeping the trees short

The first optimization is to track an upper bound on each tree's height — its **rank** — and always hang the lower-rank tree under the higher-rank root when merging. That keeps the resulting tree as short as possible.

If two trees have equal rank, the merged tree gains exactly one level (you have to pick one to be the new root), so its rank increments by 1. If their ranks differ, hanging the shorter under the taller leaves the rank unchanged — the merged tree is no taller than the taller of its two inputs was.

```python {export=src/codex/structures/union_find.py}
class UnionFind:
    def __init__(self, n: int) -> None:
        self._parent = list(range(n))
        self._rank = [0] * n
```

The constructor adds a parallel `_rank` array, initialized to zero (every singleton has rank 0). The `union` method becomes a three-way conditional on the rank comparison.

```python {export=src/codex/structures/union_find.py}
    def union(self, x: int, y: int) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self._rank[rx] < self._rank[ry]:
            self._parent[rx] = ry
        elif self._rank[rx] > self._rank[ry]:
            self._parent[ry] = rx
        else:
            self._parent[ry] = rx
            self._rank[rx] += 1
```

The rank-only optimization (without path compression) is enough to bound tree height by $\log_2 n$. The argument: a tree of rank $r$ contains at least $2^r$ elements. That's true at rank 0 (one element) and is preserved by `union` — two trees of equal rank $r$ merge into one of rank $r+1$ with at least $2^r + 2^r = 2^{r+1}$ elements. So a tree of rank $r$ has at least $2^r$ elements. Rank is bounded by $\log_2 n$, height by $\log_2 n$, and `find` runs in $O(\log n)$.

That alone is already a dramatic win over the chain-shaped worst case. The next optimization gets you to near-constant.

## Path compression: flattening as a side effect

When `find` walks from a node up to the root, it visits every node on the path. *None* of those nodes need to remain as deep as they were — they could all point directly at the root. So why not rewrite their parent pointers on the way back, after the walk has discovered the root?

The recursive implementation is a one-line trick. `find(x)` finds the root by recursing into `find(parent[x])`, and on the way back from the recursion, it writes the root into `parent[x]`. Every node on the original path ends up pointing directly at the root.

```python {export=src/codex/structures/union_find.py}
    def find(self, x: int) -> int:
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)
```

Three lines for the `find`. The first checks the base case (the node is its own parent, so it's the root). The second recursively finds the root *and* writes it into `_parent[x]`, mutating the tree on the return path. The third returns the root.

Path compression doesn't always change the *height* of the tree — the root and its direct children might be unchanged. But it flattens the *path you just walked*, and every subsequent `find` on any node along that path is now $O(1)$. The effect compounds over many operations.

Watch path compression do its thing on a deliberately-bad starting state:

```python
from codex.structures.union_find import UnionFind

uf = UnionFind(n=8)
# manually construct a spaghetti tree: 7 → 6 → 5 → 4 → 3 → 2 → 1 → 0
for i in range(1, 8):
    uf._parent[i] = i - 1

print(f"before find: parent = {uf._parent}")     # [0,0,1,2,3,4,5,6]
uf.find(7)                                        # walks 7→6→5→4→3→2→1→0, compresses
print(f"after find:  parent = {uf._parent}")     # everyone on the path → 0
```

One `find` call, eight pointer rewrites. After it, the tree's deep chain has collapsed to a star — every formerly-on-the-path node points directly at the root. The next seven `find` calls on any of those nodes will be $O(1)$.

The combined effect of union by rank and path compression is what gives the structure its near-constant amortized cost. Each optimization alone would still be polynomial; together they break out of polynomial entirely. Tarjan's 1975 analysis showed the combined operations have amortized cost $O(\alpha(n))$ — the inverse Ackermann function.

## Inverse Ackermann is at most 4

The Ackermann function grows fast. Faster than exponential, faster than tower-of-exponentials, faster than any primitive recursive function. $A(4, 4)$ already exceeds the number of atoms in the observable universe. The *inverse* — $\alpha(n)$, the smallest $m$ such that $A(m, m) \ge n$ — grows so slowly that $\alpha(n) \le 4$ for any $n \le 2^{2^{16}} = 2^{65536}$, a number with twenty thousand digits.

So when this chapter says $O(\alpha(n))$ amortized, the operational meaning is "effectively constant for any input you can construct on any computer ever built." The bound is not literally $O(1)$ — there's a real function in there — but the function is so close to a constant that the distinction has no engineering consequence.

The reason it's not literally $O(1)$ is the structural payoff. The deep result (Fredman & Saks 1989) is that $\Omega(\alpha(n))$ is the *true* lower bound for this problem in the cell-probe model: there's no implementation, however clever, that can do better in the worst case. That makes path-compression-plus-union-by-rank tight at the inverse-Ackermann level, a striking achievement for a structure built from "child points at parent."

```python
import time
import random
from codex.structures.union_find import QuickFind, QuickUnion, UnionFind


def benchmark(cls, n: int, ops_count: int) -> float:
    uf = cls(n)
    random.seed(42)
    start = time.perf_counter()
    for _ in range(ops_count):
        x = random.randint(0, n - 1)
        y = random.randint(0, n - 1)
        uf.union(x, y)
    return time.perf_counter() - start


n, ops = 1000, 5000
for name, cls in [
    ("QuickFind", QuickFind),
    ("QuickUnion", QuickUnion),
    ("UnionFind", UnionFind),
]:
    t = benchmark(cls, n, ops)
    print(f"{name:>10}: {t * 1000:>7.1f} ms")
```

The differences widen with input size. QuickFind is dominated by its $O(n)$ union cost; its union cost is the bottleneck. QuickUnion does better on random sequences that happen to produce balanced trees on average. The optimized UnionFind is fastest of all, by the amortized constant factor the inverse-Ackermann bound predicts. Run the same benchmark at $n = 10\,000$ and the gap between QuickFind and the other two becomes orders of magnitude: the practical face of amortized $O(\alpha(n))$ beating worst-case $O(n)$.

## The three questions, applied

### Is it correct?

All three implementations satisfy the partition contract: `connected(x, y)` returns `True` iff `x` and `y` are in the same set after the sequence of `union` calls executed so far. The shared invariant is that **every element belongs to exactly one set**, and the representative of each set is uniquely determined by the structure (the label in `QuickFind`, the root of the tree in the other two).

`QuickFind` is correct because the label array directly stores each element's set identity; the linear-sweep `union` keeps the array consistent. `QuickUnion` is correct because every element can reach its set's root by walking parents, and the root is invariant under `find`. `UnionFind` is correct because path compression preserves which root each element reaches (it just shortens the path), and union by rank preserves the parent-forest structure (it just picks the shorter tree to hang).

### How efficient is it?

The cost table:

| Structure | `find` | `union` | `connected` |
|-----------|--------|---------|-------------|
| `QuickFind` | $O(1)$ | $\Theta(n)$ | $O(1)$ |
| `QuickUnion` (worst) | $\Theta(n)$ | $\Theta(n)$ | $\Theta(n)$ |
| `QuickUnion` (random) | $O(\log n)$ avg | $O(\log n)$ avg | $O(\log n)$ avg |
| `UnionFind` (PC + rank) | $O(\alpha(n))$ amortized | $O(\alpha(n))$ amortized | $O(\alpha(n))$ amortized |

Space is $\Theta(n)$ for all three — one or two arrays of $n$ integers each.

The amortization argument for the optimized version is non-trivial — Tarjan's original proof is several pages of careful potential-function bookkeeping — but the operational claim is straightforward: across any sequence of $m$ union and find operations on $n$ elements, the total work is $O(m \cdot \alpha(n))$, even though individual operations can occasionally cost as much as $O(\log n)$.

### Is it optimal?

Yes, in a deeply specific sense. Fredman and Saks proved in 1989 that any data structure supporting `union` and `find` on $n$ elements must use $\Omega(\alpha(n))$ amortized time per operation in the cell-probe model — the most permissive model of computation, where you only count memory accesses. That lower bound matches Tarjan's upper bound exactly. The optimized union-find is *tight at the inverse-Ackermann level* — no implementation, however clever, can be asymptotically faster.

That tightness is unusual. Most structures in this book sit within a constant factor of their lower bound; union-find lands *on* it. The match exists because the lower bound itself is sophisticated — it took Fredman and Saks to discover that the inverse Ackermann was inevitable, not a quirk of the algorithm.

## A forest, an amortization, and a bound that's almost constant

Three claims survive the chapter. **The right data structure is sometimes a forest, not a tree:** the partition is a set of trees, with the root naming each set, and the elegance of the optimizations comes from this multi-tree view. **Amortized analysis pays for self-modification:** path compression rewrites the tree as a side effect of querying it, and the rebuilding cost is paid for by the cheaper queries it enables downstream. **Near-constant time bounds aren't $O(1)$ but might as well be:** once a bound is below $\alpha(n) \le 4$ for any realistic input, the distinction stops being engineering.

The three versions of union-find walk through the same progression: identify the bottleneck operation, restructure the data to make it cheap, watch the cost shift to the other operation, restructure again, find the optimization that makes both cheap at once. The quick-find-to-quick-union flip moves the cost from `union` to `find`. Union by rank bounds tree height by $\log n$. Path compression makes individual paths near-constant after the first walk.

In Part V, Kruskal's minimum-spanning-tree algorithm is *just* sort the edges by weight, then walk them in order, adding each edge whose endpoints aren't already in the same set. The cycle check is `connected(u, v)`. The "add this edge" step is `union(u, v)`. The whole algorithm is a wrapper around a union-find, plus a sort.

## Notes and further reading

The disjoint-set / union-find data structure is treated in CLRS (4th ed.) §19, including a clean exposition of the amortized analysis. The original combined union-by-rank-plus-path-compression algorithm and its $O(m \alpha(n))$ amortization is Robert Tarjan's 1975 *Journal of the ACM* paper "Efficiency of a Good But Not Linear Set Union Algorithm." The matching lower bound is Fredman and Saks's 1989 STOC paper "The Cell Probe Complexity of Dynamic Data Structures." Sedgewick & Wayne's *Algorithms* (4th ed.) §1.5 has the cleanest pedagogical treatment of the three implementations side-by-side and is the basis for this chapter's structure. For the recursive path-compression implementation versus the iterative two-pass alternative ("path splitting" and "path halving"), see Tarjan and van Leeuwen's 1984 *JACM* paper "Worst-Case Analysis of Set Union Algorithms," which proves that all three variants give the same asymptotic bound.
