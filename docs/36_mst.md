# Spanning trees of minimum weight

A spanning tree of a connected graph is a subgraph that includes every vertex and enough edges to keep them connected, with no cycles. There are many spanning trees of most graphs — the complete graph on $n$ vertices has $n^{n-2}$ of them by Cayley's formula — but among all of them one question stands out: which spanning tree minimizes the total edge weight? Two algorithms answer it. Kruskal's algorithm scans the edge list sorted by weight and adds each edge that doesn't form a cycle, stopping when the tree has $n - 1$ edges. Prim's algorithm grows a single tree from one starting vertex, repeatedly adding the minimum-weight edge connecting a tree vertex to a non-tree vertex. Both give the same answer on any graph, and the reason both are correct — the reason *any* locally greedy spanning-tree algorithm is correct, under the right conditions — is a single theorem about graph cuts.

By the end of this chapter you will have implemented both algorithms, confirmed that they produce the same minimum spanning tree on the canonical graph from chapter 31, understood the cut property that makes both correct, and seen explicitly that Kruskal and Prim are the same proof read in two different orders. Kruskal uses the union-find structure from chapter 14 to decide in near-constant time whether adding an edge would close a cycle. Prim uses the heap from chapter 19 in the same role it plays in Dijkstra — as a priority queue that returns the cheapest candidate edge in $O(\log n)$ time. Both algorithms produce the $n - 1$ edges of a minimum spanning tree in total time $O(m \log m)$ for Kruskal and $\Theta((n + m) \log n)$ for Prim.

## The theorem both algorithms rest on

Here is the one result both algorithms depend on. A *cut* of a graph is any partition of its vertices into two non-empty sets $S$ and $V \setminus S$. An edge *crosses* the cut if one endpoint is in $S$ and the other is in $V \setminus S$. The cut property is the one theorem the whole chapter turns on:

**Cut property.** *For any cut $(S, V \setminus S)$ of a connected weighted graph with distinct edge weights, the minimum-weight edge crossing the cut belongs to every minimum spanning tree.*

The proof is short. Let $e = (u, v, w)$ be the minimum-weight edge crossing the cut, and let $T$ be any spanning tree that does not contain $e$. Since $T$ is a spanning tree, it has a path from $u$ to $v$. That path must cross the cut — it starts in $S$ (at $u$) and ends in $V \setminus S$ (at $v$) — so it uses at least one edge $e' = (u', v', w')$ that also crosses the cut. Since $e$ is the minimum-weight cut-crossing edge and $e' \ne e$, we have $w < w'$. Now swap $e'$ for $e$: the result is still a spanning tree (we removed one edge and added one that reconnects the two parts), and its total weight is strictly less than $T$'s. So $T$ is not a minimum spanning tree. Contradiction. Therefore every MST contains $e$.

The converse holds too: for any edge $e$ that is not the minimum-weight crossing edge for *any* cut, there exists an MST that doesn't contain $e$. The cut property completely characterizes which edges can and must appear in any MST.

What makes the cut property the right tool for analyzing both algorithms is that each algorithm's greedy local choice corresponds to finding a minimum-weight crossing edge for some cut. Kruskal's cut, at each step, is the partition into the two components that would be merged by the candidate edge. Prim's cut, at each step, is the partition into the current tree vertices and everything else. The greedy choices look different in code; in terms of the cut property they are the same choice, made in a different order.

## Sorting edges until the tree is built

Kruskal's algorithm is almost embarrassingly simple once you have the right data structure. Sort all edges by weight. Walk down the sorted list; for each edge, check whether its two endpoints are already in the same component. If yes, adding the edge would form a cycle — skip it. If no, add the edge and merge the two components. Stop when $n - 1$ edges have been added.

The component check and merge is exactly the problem the union-find from chapter 14 was built for. Each component is a set in the partition; `find` returns the set's representative; `connected` checks whether two vertices share a representative; `union` merges two sets. With path-compressed union-find, each check and merge costs $O(\alpha(n)) \approx O(1)$ amortized, making the dominant cost the initial sort: $O(m \log m)$.

```python {export=src/codex/graphs/mst.py}
from collections.abc import Callable, Hashable, Iterable
from math import inf
from codex.structures.union_find import UnionFind
from codex.trees.heap import HeapPriorityQueue

type WeightedEdge[V] = tuple[V, V, float]
type WeightedNeighborFn[V] = Callable[[V], Iterable[tuple[V, float]]]


def kruskal[V: Hashable](
    vertices: Iterable[V],
    edges: Iterable[WeightedEdge[V]],
) -> list[WeightedEdge[V]]:
    """Kruskal's minimum spanning tree. Sorts edges by weight and adds
    each one that doesn't form a cycle, using union-find for cycle
    detection. Returns the MST as a list of edges. On a disconnected
    graph, returns a minimum spanning forest (one tree per component).
    """
    vlist = list(vertices)
    index = {v: i for i, v in enumerate(vlist)}
    uf = UnionFind(len(vlist))
    mst: list[WeightedEdge[V]] = []
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        iu, iv = index[u], index[v]
        if not uf.connected(iu, iv):
            uf.union(iu, iv)
            mst.append((u, v, w))
    return mst
```

Twenty lines with the import and type alias. The body is the four-step description above, translated directly: sort, walk, check `connected`, call `union` and append. The `index` dictionary maps each vertex to its integer index in the union-find structure — the mapping exists because `UnionFind` from chapter 14 operates on integers 0 to $n - 1$, not on arbitrary vertex labels. Everything else in the code is the algorithm, unchanged.

Run it on the canonical graph.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.mst import kruskal

g = AdjacencyList[str](directed=False)
for u, v, w in [("A", "B", 5), ("A", "C", 3), ("B", "C", 2), ("B", "D", 6),
                ("C", "D", 1), ("C", "E", 4), ("D", "E", 2), ("D", "F", 3),
                ("E", "F", 5)]:
    g.add_edge(u, v, w)

mst = kruskal(g.vertices(), g.edges())

total = sum(w for _, _, w in mst)
print(f"MST total weight: {total}")
print("edges:")
for u, v, w in sorted(mst, key=lambda e: e[2]):
    print(f"  {u}—{v}  weight {w}")
```

Five edges for six vertices, total weight 11: `C—D(1)`, `B—C(2)`, `D—E(2)`, `A—C(3)`, `D—F(3)`. The algorithm added them in that order, skipping `A—B(5)`, `C—E(4)`, `B—D(6)`, and `E—F(5)` because each of those edges would have formed a cycle.

The cut-property reading of each decision: when `C—D(1)` is considered, the cut $(\\{C\\}, V \setminus \\{C\\})$ has `C—D` as its minimum-weight crossing edge, so the cut property says it must be in the MST. When `B—C(2)` is considered next, the relevant cut is $(\text{component}(B), V \setminus \text{component}(B)) = (\\{B\\}, \\{A, C, D, E, F\\})$, and `B—C(2)` is the cheapest crossing edge. Each Kruskal step is a local application of the cut property, and the global correctness follows. Prim's algorithm uses the same theorem but reads it from a different direction.

## Growing the tree from one vertex

Prim's algorithm starts at one vertex and grows the MST outward, one vertex at a time. At every step, it picks the cheapest edge connecting the current tree to a vertex not yet in the tree, adds that vertex, and continues. The loop body is exactly Dijkstra's loop body from chapter 34, with one substitution: instead of maintaining `dist[v] = dist[u] + w(u, v)` (path distance from source), it maintains `key[v] = w(u, v)` (weight of the single edge connecting $v$ to the current tree). The skeleton stays the same.

The substitution is the entire difference between Dijkstra and Prim. Dijkstra minimizes total path length from a fixed source; Prim minimizes the edge weight to the current tree. Both use a min-heap, both use lazy deletion to handle stale entries, both finalize each vertex exactly once. The cost shape is the same: $\Theta((n + m) \log n)$ with a binary heap.

```python {export=src/codex/graphs/mst.py}
def prim[V: Hashable](
    source: V,
    neighbors: WeightedNeighborFn[V],
) -> tuple[dict[V, float], dict[V, V | None]]:
    """Prim's minimum spanning tree. Grows the MST from source using
    a min-heap keyed on edge weight (not accumulated path distance).
    Returns (key, parent) where key[v] is the weight of the MST edge
    connecting v to the tree, and parent[v] is v's predecessor in the
    MST. source maps to (0.0, None). Unreachable vertices don't appear.
    """
    key: dict[V, float] = {source: 0.0}
    parent: dict[V, V | None] = {source: None}
    in_mst: set[V] = set()
    pq: HeapPriorityQueue[float, V] = HeapPriorityQueue()
    pq.push(0.0, source)
    while pq:
        k, u = pq.pop()
        if u in in_mst:
            continue
        in_mst.add(u)
        for v, w in neighbors(u):
            if v not in in_mst and w < key.get(v, inf):
                key[v] = w
                parent[v] = u
                pq.push(w, v)
    return key, parent
```

Twenty-two lines. Compare with Dijkstra's twenty lines: the differences are the variable names (`key` instead of `dist`, `in_mst` instead of `finalized`) and the one-line change from `new_d = d + w; if new_d < dist.get(v, inf)` to `if w < key.get(v, inf)`. The heap push is `pq.push(w, v)` instead of `pq.push(new_d, v)`. That's the entire algorithmic difference. Everything else — the lazy-deletion skip on `in_mst`, the parent recording, the early-termination condition, the outer loop — is identical.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.mst import prim

g = AdjacencyList[str](directed=False)
for u, v, w in [("A", "B", 5), ("A", "C", 3), ("B", "C", 2), ("B", "D", 6),
                ("C", "D", 1), ("C", "E", 4), ("D", "E", 2), ("D", "F", 3),
                ("E", "F", 5)]:
    g.add_edge(u, v, w)

key, parent = prim("A", g.weighted_neighbors)

total = sum(key[v] for v in key if parent[v] is not None)
print(f"MST total weight: {total}")
print("edges:")
for v in sorted(key):
    if parent[v] is not None:
        print(f"  {parent[v]}—{v}  weight {key[v]:.0f}")
```

Total weight 11, same MST edges as Kruskal. The specific edges: `A—C(3)`, `C—B(2)`, `C—D(1)`, `D—E(2)`, `D—F(3)`. The edges are identical to Kruskal's output; the order in which they were discovered differs (Prim adds them in the order vertices join the tree starting from `A`, while Kruskal adds them in global weight order), but the MST is the same. The section below shows exactly what makes the two orderings equivalent.

## Two algorithms, one theorem

The structural parallel between Kruskal and Prim is easier to see once you write down what cut each step uses.

**Kruskal, step by step.** After processing the first $k$ edges, there are some number of components. When the algorithm considers edge $(u, v, w)$, the cut is $(\text{component}(u), V \setminus \text{component}(u))$. Among all edges crossing that cut that haven't already been added, $(u, v, w)$ is the one with minimum weight — because the edges are processed in sorted order and any earlier edge that crossed the same cut would have already been added (it would have connected two different components). The cut property says $(u, v, w)$ must be in some MST.

**Prim, step by step.** After adding $k$ vertices to the tree, the current set is $S$. The algorithm pops the vertex $v$ with the smallest `key[v]`, which records the weight of the edge $(parent[v], v)$ connecting $v$ to the current tree. The cut is $(S, V \setminus S)$. Among all edges crossing the cut, $(parent[v], v, \text{key}[v])$ is the minimum-weight one — because the heap gives the minimum across all candidates, and `key[v]` records the best edge from $v$ to the tree. The cut property says this edge must be in some MST.

In both cases the greedy choice is "pick the minimum-weight edge crossing some cut." The difference is which cut: Kruskal uses the cut defined by a single component, applied globally to all components; Prim uses the cut defined by the entire current tree, applied locally to one candidate vertex. They discover the same MST edges in a different order.

This also explains when the algorithms have different performance profiles. Kruskal needs to sort all $m$ edges up front: $O(m \log m)$ before the first edge is added. On a dense graph ($m = \Theta(n^2)$) this dominates everything else and gives $\Theta(n^2 \log n)$. On a sparse graph ($m = O(n)$) the sort is $O(n \log n)$ and the union-find operations barely register, making Kruskal fast. Prim starts immediately from one vertex and pays $O(\log n)$ per edge relaxation via the heap. On a dense graph where most edges are relaxed, $m = \Theta(n^2)$ heap operations give $\Theta(n^2 \log n)$ — same as Kruskal asymptotically, but with a worse constant because the heap operations dominate. In practice, on sparse graphs Kruskal is competitive because its inner loop is simpler; on dense graphs the right choice is the $O(n^2)$ adjacency-matrix Prim (linear scan instead of heap, same greedy logic), not either of the algorithms in this chapter.

## The three questions, applied

### Is it correct?

Both algorithms are correct by the cut property. For Kruskal: when the algorithm adds edge $(u, v, w)$, no earlier edge connected `component(u)` to `component(v)`, so $(u, v, w)$ is the minimum-weight edge crossing the cut $(\text{component}(u), V \setminus \text{component}(u))$ among edges not yet committed to cycles. By the cut property, it's in some MST. Repeating this argument for each added edge shows that the entire set of added edges belongs to some common MST.

For Prim: when the algorithm adds vertex $v$ with parent $p$ and key weight $w$, $(p, v, w)$ is the minimum-weight edge from the current tree $S$ to $V \setminus S$. By the cut property, this edge belongs to every MST. Repeating for each added vertex gives the full MST.

The cut property's proof assumed distinct edge weights. In practice, graphs frequently have ties. The cut property generalizes to non-distinct weights if you replace "every MST" with "some MST": for any cut, a minimum-weight crossing edge is in *some* MST, though not necessarily all of them. Both algorithms still return a valid MST on graphs with ties; they may return different ones depending on tie-breaking order.

### How efficient is it?

Kruskal runs in $O(m \log m)$ time, dominated by the initial sort. The union-find operations cost $O(m \alpha(n))$ amortized total, where $\alpha$ is the inverse Ackermann function — for all practical purposes, $O(m)$. The sort is the bottleneck. Space is $O(n + m)$ for the union-find structure and the sorted edge list.

Prim runs in $\Theta((n + m) \log n)$ time with a binary heap. Each vertex is popped from the heap at most once ($\Theta(n \log n)$ total), and each edge is relaxed at most twice (once per endpoint, $\Theta(m \log n)$ total). Space is $O(n + m)$ for the heap and the `key`/`parent` dictionaries. With a Fibonacci heap the bound improves to $\Theta(n \log n + m)$, which beats Kruskal on dense graphs, but the constant factors of Fibonacci heaps make the practical crossover point larger than most real graphs.

For the specific comparison: on sparse graphs ($m = O(n \log n)$), both algorithms are $O(n \log n)$. On dense graphs ($m = \Theta(n^2)$), both are $O(n^2 \log n)$ — but a simple $O(n^2)$ adjacency-matrix Prim with linear scan replaces the heap beats both. In practice, Kruskal is the first choice for sparse graphs (simpler implementation, one sort, union-find nearly free); adjacency-matrix Prim is the first choice for dense graphs.

### Is it optimal?

For MST computation in the comparison model, the lower bound is $\Omega(m \log n)$, which Kruskal matches on sparse graphs and Prim matches in general. The bound comes from the fact that MST computation must determine for each edge whether it belongs to the MST, which requires at least $\Omega(m)$ comparisons, and the tree structure requires distinguishing $\Omega(n)$ possibilities, costing $\Omega(\log n)$ per vertex.

The optimal MST algorithm remains an open problem: Borůvka's 1926 algorithm achieves $O(m \log n)$; Fredman and Tarjan's 1987 Fibonacci-heap Prim achieves $O(m + n \log n)$; the current best general algorithm is a randomized algorithm by Karger, Klein, and Tarjan (1995) that runs in expected $O(m)$ time. The $O(m)$ bound is also achievable deterministically for integer weights. Whether a deterministic $O(m)$ algorithm exists for general weights is open, making this one of the few classical algorithm problems whose optimal complexity remains unresolved.

## What this chapter teaches

**The cut property unifies the greedy argument.** Two algorithms that look structurally different — one sorts all edges up front, the other grows a tree vertex by vertex — are both instances of the same theorem. Every greedy spanning-tree algorithm that can be described as "repeatedly pick the minimum-weight edge crossing some cut" is correct. The cut property is the precise statement of why greedy works here when it fails for, say, the shortest-path problem on graphs with negative cycles: the cut structure of the graph constrains which edges can be in any MST, and the greedy local choice never conflicts with the global constraint.

**Union-find earns its keep.** The union-find structure from chapter 14 was introduced for disjoint-set operations in abstract terms. Here it does a specific job: cycle detection in Kruskal's inner loop. Without it, testing whether edge $(u, v)$ forms a cycle would require a DFS or BFS from $u$ to $v$ in the current MST forest, costing $O(n)$ per edge and making the total algorithm $O(nm)$. Path-compressed union-find reduces that to $O(\alpha(n))$ per operation — essentially constant — and the sort dominates. The chapter shows the payoff of a data structure studied in isolation: it enters a new algorithmic context and the cost shape of a well-known algorithm changes by a factor of $n$.

**The Dijkstra—Prim parallel is exact.** Dijkstra maintains `dist[v]` as the distance from source to `v` via the cheapest known path; Prim maintains `key[v]` as the weight of the cheapest known edge from the current tree to `v`. Both use a min-heap keyed on that value, both use lazy deletion, both finalize each vertex once. The one-line difference between the two implementations — `new_d = d + w` versus `w` directly — is the difference between "shortest path" and "cheapest tree edge." Recognizing this parallel makes the next algorithm in the chapter easier to read: if you understand Dijkstra, Prim is one substitution.

## Notes and further reading

Otakar Borůvka described the minimum spanning tree problem and the first algorithm for solving it in 1926, motivated by an electrical network design problem in Moravia. Borůvka's algorithm processes components in parallel — each component simultaneously selects its minimum-weight outgoing edge, then all selected edges are added and components merged — and runs in $O(m \log n)$ time. It predates Kruskal's and Prim's algorithms by three decades and is still used in practice for parallel MST computation.

Joseph Kruskal published his algorithm in 1956 ("On the Shortest Spanning Subtree of a Graph and the Traveling Salesman Problem," *Proceedings of the American Mathematical Society* 7(1):48–50). Robert Prim published the vertex-growing algorithm in 1957 ("Shortest Connection Networks and Some Generalizations," *Bell System Technical Journal* 36(6):1389–1401), though Vojtech Jarník had described the same algorithm independently in 1930. The heap-based variant of Prim's algorithm, as presented in this chapter, is due to Dijkstra (1959) and Fredman-Tarjan (1987).

The cut property as a unified framework for MST algorithms appears in CLRS chapter 23, where it is called the "generic MST algorithm" — a meta-algorithm that adds safe edges (minimum-weight edges crossing some cut of the current forest) one at a time. Kruskal and Prim are two implementations of this meta-algorithm. Sedgewick and Wayne's *Algorithms* (4th ed.) §4.3 presents both alongside the cut property and makes the connection explicit.

For a broader treatment of greedy algorithms and matroids — the algebraic structure that explains exactly when greedy algorithms work for optimization problems — Lawler's *Combinatorial Optimization: Networks and Matroids* (1976) is the canonical reference. The graphic matroid of a graph is the structure that makes Kruskal's greedy choice correct: the set of edges forms a matroid, and the greedy algorithm applied to a matroid always produces an optimal independent set. The matroid framework extends to weighted interval scheduling, transversal matching, and other problems where greedy algorithms are known to work.

Regarding the open problem on MST optimality: Karger, Klein, and Tarjan's 1995 randomized linear-time algorithm appears in "A Randomized Linear-Time Algorithm to Find Minimum Spanning Trees" (*JACM* 42(2):321–328). The current best deterministic bound, due to Chazelle (2000), is $O(m \alpha(n))$ — nearly linear — but a deterministic $O(m)$ MST algorithm is open.

In the next chapter I'll turn to structural questions about directed graphs. Topological sorting asks for an ordering of vertices such that every edge goes from earlier to later — possible exactly when the graph has no cycle, which DFS from chapter 33 can check in $\Theta(n + m)$. Strongly connected components ask for the maximal subsets of vertices that can all reach each other — again the answer falls out of DFS, but the argument is more subtle. Both algorithms are direct applications of the DFS vocabulary built in chapter 33.
