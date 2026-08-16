# Relaxation under negative weights and across all pairs

Every edge in Dijkstra's algorithm runs through the same three-line test: compare `dist[u] + w(u, v)` against `dist[v]`, tighten the bound if the new path is cheaper, do nothing otherwise. That test — *relaxation* — is correct under any weight sign. What breaks under negative weights is not the test but the order in which Dijkstra applies it. The heap imposes a greedy order: finalize the tentative vertex with the smallest `dist`, relax its edges, and trust that no future path can improve on it. Non-negative weights make that trust warranted. A negative edge anywhere in the graph can break it: a path discovered later, routing through that negative edge, might be cheaper than something the algorithm committed to many pops ago. Remove the greedy order and you're left with the relaxation step running under its own discipline, and two distinct algorithms emerge from choosing what that discipline is.

By the end of this chapter you will have implemented both. Bellman-Ford replaces the heap with brute force: relax every edge, $n - 1$ times, in any order. It handles negative-weight edges correctly and detects the one condition that makes shortest paths undefined — a negative-weight cycle reachable from the source. Floyd-Warshall drops the single-source constraint entirely and computes shortest paths between every ordered pair of vertices by growing the allowed set of intermediate vertices one step at a time, turning the problem into a three-line dynamic-programming loop. Both algorithms share the same per-edge relaxation step from chapter 34. The cost shape changes — from $\Theta((n + m) \log n)$ to $\Theta(nm)$ for Bellman-Ford and $\Theta(n^3)$ for Floyd-Warshall — and that difference is exactly the price of giving up the greedy finalization order.

## Why a negative edge defeats the greedy choice

Walk through a concrete failure. Four vertices: $A$, $B$, $C$, $D$. Edges: $A \to B$ with weight 3, $A \to C$ with weight 100, $B \to D$ with weight 1, $C \to B$ with weight $-200$. The true shortest paths from $A$ are $\text{dist}[B] = -100$ (via $A \to C \to B$, weight $100 - 200$) and $\text{dist}[D] = -99$ (via $A \to C \to B \to D$). Dijkstra's algorithm — with the negative-weight check from chapter 34 disabled — would proceed as follows. Pop $(0, A)$, push $(3, B)$ and $(100, C)$. Pop $(3, B)$, finalize $B$ at distance 3, push $(4, D)$. Pop $(4, D)$, finalize $D$ at distance 4. Pop $(100, C)$, finalize $C$, relax $C \to B$ and discover a path of weight $-100$... but $B$ is already in `finalized`. The skip fires. The algorithm returns $\text{dist}[B] = 3$, $\text{dist}[D] = 4$. Both are wrong by roughly a factor of a hundred.

The greedy choice bought its correctness from the guarantee that no detour can improve on a finalized vertex: any other tentative path would have to pass through some tentative vertex first, and those vertices all have distances at least as large, and extending forward by any non-negative edge can only increase the total. With a negative edge, that guarantee evaporates. A path that looks expensive early might become cheap when it hits the negative edge; the algorithm has no way to know, and once a vertex is finalized, the improvement that arrives later is ignored.

The fix is to abandon finalization entirely: relax every edge in the graph, repeatedly, until nothing changes. The number of passes required is at most $n - 1$. A shortest simple path in a graph with $n$ vertices has at most $n - 1$ edges — if it had $n$ or more edges, some vertex would appear twice, forming a cycle, and that cycle either has positive weight (making it non-optimal, so the shortest path wouldn't include it) or negative weight (which is the case we detect and flag separately). After $k$ passes of relaxing every edge once, `dist[v]` holds the best path weight using at most $k$ edges. After $n - 1$ passes, that covers all simple paths.

## Relax every edge, over and over

The algorithm structure is three parts: initialize distances, run $n - 1$ relaxation passes over every edge, check for a negative-weight cycle with one additional pass. The implementation follows that outline directly.

```python {export=src/codex/graphs/relaxation.py}
from collections.abc import Hashable, Iterable
from math import inf

type WeightedEdge[V] = tuple[V, V, float]


def bellman_ford[V: Hashable](
    source: V,
    vertices: Iterable[V],
    edges: Iterable[WeightedEdge[V]],
) -> tuple[dict[V, float], dict[V, V | None]]:
    """Bellman-Ford single-source shortest paths. Handles negative-weight
    edges. Raises ValueError if a negative-weight cycle is reachable from
    source. Returns (dist, parent), where dist[v] is the shortest-path
    distance from source to v (inf if unreachable) and parent[v] is the
    predecessor of v on a shortest path.
    """
    dist: dict[V, float] = {v: inf for v in vertices}
    dist[source] = 0.0
    parent: dict[V, V | None] = {source: None}
    n = len(dist)
    edge_list = list(edges)
    for _ in range(n - 1):
        _relax_pass(edge_list, dist, parent)
    if _relax_pass(edge_list, dist, parent):
        raise ValueError("negative-weight cycle reachable from source")
    return dist, parent
```

The `list(edges)` materializes the edge iterator before the outer loop so that `_relax_pass` always iterates the same sequence in the same order. That matters for reproducibility and for the hand trace below. The outer loop runs exactly $n - 1$ times, where $n$ is the number of vertices. The negative-cycle detection is the $n$-th pass: if any distance still improves after $n - 1$ passes, a path using $n$ or more edges is shorter than any simple path, and the only explanation is a negative-weight cycle.

The helper that applies the full edge list once is the relaxation step from chapter 34, generalized to every edge at once:

```python {export=src/codex/graphs/relaxation.py}
def _relax_pass[V: Hashable](
    edges: list[WeightedEdge[V]],
    dist: dict[V, float],
    parent: dict[V, V | None],
) -> bool:
    """Relax every edge once. Return True if any distance improved."""
    improved = False
    for u, v, w in edges:
        d_u = dist.get(u, inf)
        if d_u + w < dist.get(v, inf):
            dist[v] = d_u + w
            parent[v] = u
            improved = True
    return improved
```

Twelve lines. The `dist.get(u, inf)` handles vertices not yet reachable: when `d_u` is `inf`, the expression `inf + w` stays `inf` for any finite `w`, so no update fires. The function returns a boolean flag — whether any distance improved — which is all the negative-cycle check needs: if the flag is `True` after $n - 1$ passes, some shortest path uses more than $n - 1$ edges, which implies a negative-weight cycle.

Run Bellman-Ford on the graph where Dijkstra was wrong.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.relaxation import bellman_ford

g = AdjacencyList[str](directed=True)
for u, v, w in [("A", "B", 3), ("A", "C", 100), ("B", "D", 1), ("C", "B", -200)]:
    g.add_edge(u, v, w)

dist, parent = bellman_ford("A", g.vertices(), g.edges())

print("vertex | dist | parent")
print("-------+------+-------")
for v in sorted(dist):
    p = str(parent.get(v))
    print(f"   {v}   | {dist[v]:>5.0f} | {p!s:>6}")
```

`dist[B] = -100`, `dist[D] = -99`. The path through the negative edge is now captured correctly: $A \to C \to B$ beats the direct $A \to B$ by 103 units, and that improvement carries forward to $D$.

The ordering of edges inside `_relax_pass` determines how quickly the distances converge, not whether they converge. A lucky ordering — one that processes edges in path order from the source — might converge in one pass. An unlucky ordering might need all $n - 1$. The algorithm is correct regardless, because after $k$ passes, `dist[v]` holds the shortest path weight using at most $k$ edges.

## Following the distances pass by pass

Here is a trace that needs more than one pass. Five vertices: $A$, $B$, $C$, $D$, $E$. Edges in the order `_relax_pass` will see them: $C \to D$ (weight 2), $B \to C$ (weight $-3$), $B \to E$ (weight 8), $A \to B$ (weight 4), $A \to C$ (weight 5).

The edges are deliberately ordered so that $C \to D$ appears before $B \to C$ — meaning $C$'s distance hasn't been tightened by the $B \to C$ relaxation when $C \to D$ fires in pass 1. This forces the pass count upward.

Initialize: `dist = {C: ∞, D: ∞, B: ∞, E: ∞, A: 0}`.

**Pass 1.**

- $C \to D$: $\infty + 2 = \infty$. No update ($C$ is unreachable).
- $B \to C$: $\infty + (-3) = \infty$. No update ($B$ is unreachable).
- $B \to E$: $\infty + 8 = \infty$. No update.
- $A \to B$: $0 + 4 = 4 < \infty$. `dist[B] = 4`.
- $A \to C$: $0 + 5 = 5 < \infty$. `dist[C] = 5`.

After pass 1: `{A: 0, B: 4, C: 5, D: ∞, E: ∞}`. The pass found $B$ and $C$ but couldn't use them to reach $D$ or update $C$ via $B$: $C \to D$ ran before $C$ was reachable, and $B \to C$ ran before $B$ was reachable.

**Pass 2.**

- $C \to D$: $5 + 2 = 7 < \infty$. `dist[D] = 7`.
- $B \to C$: $4 + (-3) = 1 < 5$. `dist[C] = 1`.
- $B \to E$: $4 + 8 = 12 < \infty$. `dist[E] = 12`.
- $A \to B$, $A \to C$: no improvement.

After pass 2: `{A: 0, B: 4, C: 1, D: 7, E: 12}`. `dist[D]` is still wrong: the pass saw $C \to D$ before $B \to C$ had a chance to tighten $C$ to 1, so $D$ was updated using the old $C = 5$. The cheaper path $A \to B \to C \to D$ of weight $4 - 3 + 2 = 3$ hasn't been assembled yet.

**Pass 3.**

- $C \to D$: $1 + 2 = 3 < 7$. `dist[D] = 3`.
- Everything else: no improvement.

After pass 3: `{A: 0, B: 4, C: 1, D: 3, E: 12}`. All distances are correct. The path $A \to B \to C \to D$ used three edges and took three passes to assemble in this edge ordering — exactly the correspondence the $n - 1$ bound captures.

Confirm with the actual implementation:

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.relaxation import bellman_ford

g = AdjacencyList[str](directed=True)
for u, v, w in [("C", "D", 2), ("B", "C", -3), ("B", "E", 8), ("A", "B", 4), ("A", "C", 5)]:
    g.add_edge(u, v, w)

dist, parent = bellman_ford("A", g.vertices(), g.edges())

print("vertex | dist | path from A")
print("-------+------+------------")
for v in sorted(dist):
    path, cur = [], v
    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)
    path.reverse()
    print(f"   {v}   |  {dist[v]:>2.0f} | {'→'.join(path)}")
```

Distances `{A:0, B:4, C:1, D:3, E:12}` with paths `A→B`, `A→B→C`, `A→B→C→D`, `A→B→E`. The parent reconstruction is the same logic as chapter 32's `reconstruct_path`, applied from each target back to the source. The next question is what happens when a $n$-th pass would still improve a distance — the negative-cycle case.

## One more pass reveals a negative cycle

Negative-weight cycles make shortest paths undefined: follow the cycle repeatedly and the path weight decreases without bound. The $n$-th Bellman-Ford pass is the witness. After $n - 1$ correct passes, any remaining improvement must come from a path using $n$ or more edges — the only way that happens is if a negative-weight cycle is reachable from the source.

The implementation raises `ValueError` rather than returning a silently wrong answer. The rationale is the same as Dijkstra's negative-weight check in chapter 34: a shortest-path distance of negative infinity is not a useful answer, and returning a large negative finite number in its place would mislead any caller who treats the output as a real distance.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.relaxation import bellman_ford

g_neg = AdjacencyList[str](directed=True)
for u, v, w in [("A", "B", 3), ("B", "C", -2), ("C", "A", -2)]:
    g_neg.add_edge(u, v, w)
# cycle A→B→C→A has weight 3 + (−2) + (−2) = −1

try:
    bellman_ford("A", g_neg.vertices(), g_neg.edges())
    print("no negative cycle detected")
except ValueError as e:
    print(f"caught: {e}")
```

The cycle $A \to B \to C \to A$ has weight $-1$. Traversing it once shaves a unit off every path that passes through it; traversing it $k$ times shaves $k$ units. Bellman-Ford correctly flags the graph rather than returning a finite answer.

The implementation detects whether *any* vertex reachable from the source is on or downstream of a negative cycle. If you need to know which specific vertices are affected — to mark them as "undefined" in the distance table rather than raising an exception — the standard extension is to run the $n$-th pass, collect all vertices whose distance improved, and then sweep reachability from those vertices forward through the graph. The implementation here keeps the detection minimal; the extension is one DFS away. Bellman-Ford has handled one source at a time throughout; the next algorithm drops that constraint entirely.

## Shortest paths between every pair of vertices

Single-source shortest paths answer "how far is every vertex from this one starting point?" All-pairs shortest paths answer a different question: "for any two vertices, what is the cheapest path between them?" The brute-force approach is to run Bellman-Ford from every vertex — $n$ single-source computations at $\Theta(nm)$ each, for a total of $\Theta(n^2 m)$. Floyd-Warshall solves the same problem in $\Theta(n^3)$, which is better whenever $m = \Omega(n)$. The gain comes from reusing intermediate shortest-path computations across multiple source-destination pairs instead of recomputing them from scratch for every source.

Here is the decomposition I want you to see. Fix two vertices $i$ and $j$ and ask: what is the shortest path from $i$ to $j$ using only vertices $\{v_1, v_2, \ldots, v_k\}$ as intermediates? The answer satisfies a recurrence: either the optimal path doesn't use $v_k$ as an intermediate (and the answer is the same as for $\{v_1, \ldots, v_{k-1}\}$), or it does (and the path goes from $i$ to $v_k$ optimally using $\{v_1, \ldots, v_{k-1}\}$ as intermediates, then from $v_k$ to $j$ optimally the same way). The minimum of those two cases is the answer:

$$\text{dist}_k[i][j] = \min\!\left(\text{dist}_{k-1}[i][j],\ \text{dist}_{k-1}[i][v_k] + \text{dist}_{k-1}[v_k][j]\right)$$

The base case is $k = 0$: $\text{dist}_0[i][j]$ is the weight of the direct edge $(i, j)$ if it exists, or $\infty$ if it doesn't (and 0 for $i = j$). When $k$ reaches $n$, every vertex is a possible intermediate and $\text{dist}_n[i][j]$ is the true all-pairs shortest path.

This recurrence has the shape of dynamic programming: a two-dimensional table, filled in a topological order (increasing $k$), where each cell depends only on cells from the previous layer. The edit-distance table from chapter 30 had the same shape with a different recurrence. Part VI will generalize the framework — subproblem structure, overlapping subproblems, optimal substructure — and Floyd-Warshall will appear there as a canonical example alongside edit distance. The intermediate-vertex recurrence produces the algorithm almost automatically: once you write down the DP, the code is three nested loops.

## The three-line loop that builds a matrix

Watch how cleanly the recurrence turns into an implementation. Initialize a two-dimensional distance table from the direct edge weights, then update it one intermediate vertex at a time.

```python {export=src/codex/graphs/relaxation.py}
def floyd_warshall[V: Hashable](
    vertices: Iterable[V],
    edges: Iterable[WeightedEdge[V]],
) -> dict[V, dict[V, float]]:
    """Floyd-Warshall all-pairs shortest paths. Returns dist where
    dist[u][v] is the shortest-path distance from u to v (inf if
    unreachable). Handles negative-weight edges. A negative-weight cycle
    is indicated by dist[v][v] < 0 for any vertex v after the call.
    """
    vlist = list(vertices)
    dist: dict[V, dict[V, float]] = {
        u: {v: (0.0 if u == v else inf) for v in vlist}
        for u in vlist
    }
    for u, v, w in edges:
        if w < dist[u][v]:
            dist[u][v] = w
    for k in vlist:
        _relax_via(vlist, dist, k)
    return dist
```

The initialization builds an $n \times n$ table: zeros on the diagonal, direct edge weights off-diagonal (keeping the minimum if parallel edges exist), and `inf` for all pairs with no direct edge. Then the outer loop runs once per vertex in `vlist` order, calling the helper that applies the recurrence for one intermediate vertex.

```python {export=src/codex/graphs/relaxation.py}
def _relax_via[V: Hashable](
    vertices: list[V],
    dist: dict[V, dict[V, float]],
    k: V,
) -> None:
    """Update dist[i][j] for all i, j by routing through intermediate k."""
    for i in vertices:
        for j in vertices:
            through_k = dist[i][k] + dist[k][j]
            if through_k < dist[i][j]:
                dist[i][j] = through_k
```

Seven lines. The inner double loop over all $(i, j)$ pairs is the entire cost driver: $n^2$ pairs, times $n$ outer iterations, gives $n^3$ relaxation steps in total, each $O(1)$. There is no heap, no visited set, no recursion. Just three nested loops over the vertex list.

The in-place update is correct for graphs without negative cycles. The standard argument: in the $k$-th outer iteration, reading `dist[i][k]` yields the shortest path from $i$ to $v_k$ using intermediates $\{v_1, \ldots, v_{k-1}\}$ — the same value the recurrence would compute for `dist[k-1][i][k]`. The reason is that `dist[i][k]` cannot be improved by using $v_k$ as an intermediate for the $i$-to-$v_k$ path, because that would require $v_k$ to appear twice, forming a cycle, and on a cycle-free shortest path that never happens. The same argument covers `dist[k][j]`. So the in-place reads are correct even though the table is being modified simultaneously.

This implementation does not reconstruct paths — it returns only the distance table. Adding path reconstruction requires a second $n \times n$ table `next[i][j]` initialized with the direct successor on each direct edge and updated alongside `dist`. For the pedagogical goal of this chapter, the distance table is enough; the reconstruction extension is one more table and one more update per inner-loop iteration.

Run the algorithm on a four-vertex directed graph with negative edges.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.relaxation import floyd_warshall
from math import inf

g = AdjacencyList[str](directed=True)
for u, v, w in [("A", "B", 3), ("B", "C", -2), ("C", "D", 2),
                ("D", "A", 5), ("A", "D", 10), ("B", "D", 8)]:
    g.add_edge(u, v, w)

dist = floyd_warshall(g.vertices(), g.edges())

vertices = sorted(dist.keys())
header = "     | " + " | ".join(f"  {v}  " for v in vertices)
sep = "-----+" + "------+" * len(vertices)
print(header)
print(sep)
for u in vertices:
    row = " | ".join(
        f"  {dist[u][v]:3.0f} " if dist[u][v] < inf else "  ∞  "
        for v in vertices
    )
    print(f"  {u}  | {row}")
```

The distance from $A$ to $C$ is 1: the path $A \to B \to C$ costs $3 + (-2) = 1$, cheaper than any direct edge. From $D$ to $C$ the distance is 6: the path $D \to A \to B \to C$ costs $5 + 3 - 2 = 6$. The negative edge $B \to C$ propagates its savings into all paths that route through $B$ and then continue to $C$ or beyond.

One entry worth checking against the trace above: $\text{dist}[C][B]$. There is no direct edge $C \to B$. The shortest path goes $C \to D \to A \to B$ with weight $2 + 5 + 3 = 10$. Floyd-Warshall assembles this in two steps: in the $D$-intermediate pass it discovers $\text{dist}[C][A] = 2 + 5 = 7$; in the $A$-intermediate pass it discovers $\text{dist}[C][B] = 7 + 3 = 10$. The recurrence does the composition one intermediate at a time, and the incremental structure is what avoids the $\Theta(n^2 m)$ cost of running Bellman-Ford from every vertex separately.

## The three questions, applied

### Is it correct?

Bellman-Ford's correctness follows from an inductive argument on pass count. **Invariant: after pass $k$, `dist[v]` holds the weight of the shortest path from `source` to `v` using at most $k$ edges.** The base case holds before any pass: `dist[source] = 0` (a zero-edge path) and `dist[v] = ∞` for all other vertices. For the inductive step: in pass $k$, when `_relax_pass` considers edge $(u, v, w)$, `dist[u]` is (by induction) the weight of the shortest path to $u$ using at most $k - 1$ edges. If `dist[u] + w < dist[v]`, a shorter path to $v$ using at most $k$ edges is recorded. Every such shorter path is found because `_relax_pass` examines every edge. After $n - 1$ passes the invariant gives the correct shortest-path weight for every vertex, since shortest simple paths have at most $n - 1$ edges.

The ordering of edges within each pass affects convergence speed but not correctness. A lucky ordering (edges processed in topological order from the source) converges in one pass; an unlucky ordering may use all $n - 1$. Either way the invariant holds.

Floyd-Warshall's correctness is the standard DP argument. The recurrence correctly covers both cases — path not through $v_k$, path through $v_k$ — for every pair $(i, j)$. The in-place update is correct for the reason given in the implementation section: `dist[i][k]` and `dist[k][j]` are not affected by updating `dist[i][j]` in the same $k$-pass, because using $v_k$ twice would create a cycle and shortest simple paths avoid cycles. For graphs with negative cycles, `dist[v][v]` becomes negative after the algorithm, which is the caller's signal that the distances are undefined.

### How efficient is it?

Bellman-Ford runs in $\Theta(nm)$ time and $\Theta(n + m)$ space. The outer loop runs $n - 1$ times plus one for the cycle check. Each pass iterates all $m$ edges in $\Theta(m)$ time. Total: $\Theta(nm)$. Space is dominated by the materialized edge list ($\Theta(m)$) and the `dist` and `parent` dictionaries ($\Theta(n)$ each).

As an optimization, the outer loop can terminate early if a pass produces no improvements — `_relax_pass` returning `False` means the distances are already optimal and no further passes are needed. On a graph where the shortest paths are short on average, this early termination makes Bellman-Ford much faster than the $\Theta(nm)$ worst case.

Floyd-Warshall runs in $\Theta(n^3)$ time and $\Theta(n^2)$ space regardless of graph structure. There are no shortcuts: the three nested loops always execute $n^3$ iterations. The $n^2$ space is the distance table itself. For sparse graphs, $m \ll n^2$, and running Bellman-Ford from every vertex in turn costs $\Theta(n^2 m) \ll \Theta(n^4)$; Floyd-Warshall at $\Theta(n^3)$ beats that. For very sparse graphs with negative-weight edges, Johnson's algorithm (reweight edges with a Bellman-Ford potential, then run Dijkstra from every vertex) achieves $\Theta(n^2 \log n + nm)$, which beats Floyd-Warshall on sparse graphs. Johnson's algorithm is the all-pairs algorithm production graph libraries use when the graph has negative weights and $m \ll n^2$.

### Is it optimal?

For single-source shortest paths with negative-weight edges, $\Theta(nm)$ is essentially tight in the comparison model. Any correct algorithm must examine every edge at least once (otherwise it could miss a negative edge that improves some distance), and on a graph where the shortest path uses $n - 1$ edges, a single pass is not enough. Bellman-Ford matches both lower bounds.

For all-pairs shortest paths, the output alone is $n^2$ values, so $\Omega(n^2)$ is a trivial lower bound. The best general upper bound is $\Theta(n^3)$ from Floyd-Warshall. Closing that gap is open: the fastest algorithms use $(\min, +)$-matrix multiplication and achieve $O(n^3 / \log^2 n)$ in theory, but the constant factors are large enough that $\Theta(n^3)$ with SIMD vectorization beats them in practice on any realistic graph size. For production purposes, Floyd-Warshall on dense graphs and Johnson's algorithm on sparse graphs are the state of the art, and the gap between them and the theoretical lower bound doesn't matter at any scale where the algorithm would actually be run.

## What this chapter teaches

**The relaxation step is the algorithm; the scheduling is a design choice.** Dijkstra, Bellman-Ford, and Floyd-Warshall all use the same three-line test — compare a proposed path weight against the current best, update if cheaper. The algorithms differ only in how they schedule that test: greedy heap order, brute-force pass-over-all-edges order, or DP intermediate-vertex order. When you encounter a new shortest-path algorithm, the useful question is not "what does it compute?" (they all compute shortest paths) but "what order does it relax edges in, and what assumption about the graph makes that order correct?" Answering that question immediately gives you the algorithm's correctness conditions and its cost shape.

**Generality costs a factor of $n / \log n$ off the greedy optimum.** Dijkstra on a sparse graph runs in $\Theta(m \log n)$; Bellman-Ford runs in $\Theta(nm)$. The extra factor is the cost of giving up the greedy finalization order. The greedy order is what makes Dijkstra visit each vertex exactly once; without it, you can't know when to stop relaxing, so you relax everything repeatedly until nothing moves. Any shortest-path algorithm whose correctness argument is "after $k$ passes, the answer uses paths of at most $k$ hops" will cost at least $\Theta(nm)$ — the $n - 1$ worst-case pass count is irreducible for adversarial edge orderings.

**Recognizing the DP recurrence in Floyd-Warshall opens the door to Part VI.** The intermediate-vertex recurrence $\text{dist}_k[i][j] = \min(\text{dist}_{k-1}[i][j], \text{dist}_{k-1}[i][v_k] + \text{dist}_{k-1}[v_k][j])$ is a textbook example of optimal substructure: the optimal solution to the $k$-intermediate problem decomposes into optimal solutions to the $(k-1)$-intermediate sub-problems. The edit-distance recurrence from chapter 30 had the same shape — optimal alignment of two strings decomposes into optimal alignments of their prefixes. Part VI will develop the framework explicitly, name the conditions (optimal substructure, overlapping sub-problems), and show that Floyd-Warshall and edit distance are instances of one design pattern. The SCC condensation from chapter 37 will turn a directed graph into a DAG on which DP runs in linear time, completing the feedback loop between graph algorithms and dynamic programming.

## Notes and further reading

Richard Bellman published the single-source negative-weight algorithm in 1958 in "On a Routing Problem" (*Quarterly of Applied Mathematics* 16(1):87–90). The same algorithm appeared independently in a RAND Corporation technical report by Lester Ford Jr. in 1956 (published 1958), which is why the algorithm is sometimes called Bellman-Ford-Moore — Edward Moore published a closely related traversal in 1959. The $\Theta(nm)$ analysis and negative-cycle detection via the $n$-th pass are standard across every treatment of the algorithm; CLRS chapter 24 gives the textbook version with explicit proofs.

Robert Floyd published the all-pairs algorithm in 1962 ("Algorithm 97: Shortest Path," *CACM* 5(6):345). Stephen Warshall had published a reachability-only variant one year earlier ("A Theorem on Boolean Matrices," *JACM* 9(1):11–12, 1962), computing whether paths exist rather than their weights. Peter Ingerman showed independently in 1962 that the same recurrence computes shortest-path weights; the combined Floyd-Warshall attribution names both the distance variant (Floyd) and the transitive-closure variant (Warshall). The DP derivation via the intermediate-vertex recurrence is due to Ingerman and is the framing CLRS chapter 25 uses.

Johnson's $\Theta(n^2 \log n + nm)$ algorithm for all-pairs shortest paths on sparse graphs with negative weights appeared in "Efficient Algorithms for Shortest Paths in Sparse Networks" (*JACM* 24(1):1–13, 1977). The reweighting trick it uses — compute a potential function via Bellman-Ford, add the potential to all edge weights to make them non-negative, run Dijkstra from every vertex, subtract the potentials — is an elegant composition of the two algorithms from this chapter. CLRS §25.3 presents it in detail.

The faster-than-$\Theta(n^3)$ algorithms for all-pairs shortest paths use $(\min, +)$-matrix multiplication — the algebraic structure where matrix "product" computes minimum-weight one-hop extensions instead of sums of products. The best known bound is $O(n^3 / \log^2 n)$ by Fredman (1976) and subsequent authors. The constant factors are large enough that these algorithms are never used in practice; hand-tuned Floyd-Warshall with SIMD vectorization achieves roughly an order-of-magnitude speedup over the naive triple loop while remaining algorithmically $\Theta(n^3)$.

Sedgewick and Wayne's *Algorithms* (4th ed.) §4.4 presents Bellman-Ford, Floyd-Warshall, and Dijkstra in the same chapter alongside each other, making the scheduling contrast explicit. For a unified treatment of the relaxation framework — in which Dijkstra, Bellman-Ford, Floyd-Warshall, and Prim are all instances of one meta-algorithm — Tarjan's *Data Structures and Network Algorithms* (SIAM, 1983) chapter 7 is the canonical reference.

In the next chapter I'll move from shortest paths to spanning trees. A minimum spanning tree — the cheapest subset of edges that keeps the graph connected — rests on a single theorem, the cut property, that looks different from the relaxation framework but turns out to share its structure. Kruskal's algorithm processes edges sorted by weight and adds each one that doesn't form a cycle; Prim's algorithm grows a tree from a single vertex using the same heap from this chapter and the same greedy finalization order from Dijkstra. Both are the cut property applied in two different orderings.
