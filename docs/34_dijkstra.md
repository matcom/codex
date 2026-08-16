# BFS with a heap

The skeleton from chapter 32 had one job. Pull the next vertex from the container, expand its neighbors, repeat. When the container was a FIFO queue, vertices came out in order of *fewest hops* from the source and the algorithm computed shortest paths in unweighted graphs. Swap the queue for a min-heap keyed on tentative distance, and the vertices come out in order of *smallest accumulated weight* from the source. That is the entire change. The five-line skeleton stays. The greedy choice — always expand the vertex closest to the source, not the one discovered earliest — is what Dijkstra's algorithm contributes, and the heap from chapter 19 is the data structure that makes the greedy choice cheap. By the end of this chapter you'll have implemented Dijkstra's algorithm as one tight loop, computed weighted shortest paths from `A` to every other vertex of the canonical graph from chapter 31, watched the heap-based priority queue evolve through a hand-traceable seven-iteration run, and seen exactly why the algorithm breaks the moment an edge can carry a negative weight.

The vocabulary developed here — *relaxation*, *finalization*, *the greedy choice* — is what chapter 35 reuses when it generalizes to negative-weight edges, what chapter 36 reuses for Prim's minimum-spanning-tree algorithm (which is Dijkstra with `dist[u] + w(u, v)` replaced by just `w(u, v)`), and what chapter 38 reuses inside the augmenting-path loop of the max-flow algorithm. Three later chapters of Part V live downstream of this one; getting the algorithm and its invariant clear here makes those chapters short.

## The relaxation step

The single move at the heart of Dijkstra is the *relaxation* of an edge. Maintain `dist[v]` as an upper bound on the true shortest-path distance from the source to `v` — initialized to infinity for every vertex other than the source, where it starts at zero. When the algorithm considers an edge $(u, v)$ with weight $w$, it asks: *is the path that goes from the source to `u` and then takes this one edge to `v` shorter than my current upper bound on `dist[v]`?* If yes, update the bound. If no, do nothing. That's the entire relaxation step: a three-line conditional comparing `dist[u] + w` against `dist[v]`.

```python
if dist[u] + weight < dist[v]:
    dist[v] = dist[u] + weight
    parent[v] = u
```

Dijkstra wraps this step in a specific traversal order. At any moment, the algorithm maintains two sets: *finalized* vertices, whose `dist` value is known to equal the true shortest-path distance, and *tentative* vertices, whose `dist` value is an upper bound that might still tighten. The algorithm repeatedly picks the tentative vertex with the smallest `dist`, moves it to the finalized set, and relaxes its outgoing edges. When every reachable vertex has been finalized, the algorithm halts and the `dist` dictionary holds the answer.

The *greedy choice* — picking the smallest-`dist` tentative vertex to finalize next — is what makes the algorithm work, and it's also what restricts it to non-negative weights. The correctness section shows exactly why; for now, take the algorithm on its terms and watch it run.

## Twenty lines around a heap

The greedy choice requires a data structure that returns the smallest tentative `dist` in better than $O(n)$ time per query. A linear scan over the tentative set would give an overall $\Theta(n^2)$ algorithm — fine for dense graphs, wasteful for sparse ones. The min-heap from chapter 19 returns the smallest-priority item in $O(\log n)$ per operation, and pushing each vertex once per `dist` improvement gives $\Theta((n + m) \log n)$ total. That's the bound this implementation hits.

I'll use `HeapPriorityQueue[float, V]` from `codex.trees.heap` as the priority queue. The keys are tentative distances; the values are vertices. The wrinkle: a binary heap doesn't support efficient *decrease-key*, so when the algorithm discovers a shorter path to an already-pushed vertex it can't lower that vertex's existing entry. The standard workaround is *lazy deletion* — push a new entry with the new smaller distance, and when the heap eventually returns one of the now-stale older entries, skip it. The `finalized` set is what makes the skip cheap: any popped entry whose vertex is already in `finalized` is stale and should be discarded.

```python {export=src/codex/graphs/dijkstra.py}
from collections.abc import Callable, Hashable, Iterable
from math import inf
from codex.trees.heap import HeapPriorityQueue

type WeightedNeighborFn[V] = Callable[[V], Iterable[tuple[V, float]]]


def dijkstra[V: Hashable](
    source: V, neighbors: WeightedNeighborFn[V]
) -> tuple[dict[V, float], dict[V, V | None]]:
    """Dijkstra's single-source shortest-path algorithm. Returns
    (dist, parent), where dist[v] is the weighted shortest-path distance
    from source to v (math.inf if v is unreachable), and parent[v] is
    the predecessor of v on a shortest path. Requires every edge weight
    returned by neighbors to be non-negative; raises ValueError on a
    negative weight.
    """
    dist: dict[V, float] = {source: 0.0}
    parent: dict[V, V | None] = {source: None}
    finalized: set[V] = set()
    pq: HeapPriorityQueue[float, V] = HeapPriorityQueue()
    pq.push(0.0, source)
    while pq:
        d, u = pq.pop()
        if u in finalized:
            continue
        finalized.add(u)
        for v, w in neighbors(u):
            if w < 0:
                raise ValueError(f"Dijkstra cannot handle negative edge weight {w}")
            new_d = d + w
            if new_d < dist.get(v, inf):
                dist[v] = new_d
                parent[v] = u
                pq.push(new_d, v)
    return dist, parent
```

Twenty lines, including the docstring. The structure is the BFS skeleton from chapter 32 with three changes: the queue is a priority queue keyed by distance, the `seen` set is replaced by a `finalized` set (a vertex is "seen" the first time it's pushed but only `finalized` when it's popped for the first time), and the relaxation conditional has replaced the simple "v not in seen" gate. Every push has the same `(new_d, v)` shape, every pop checks `finalized` and skips stale entries, every relaxation either tightens the bound or does nothing. There's no other state.

The negative-weight check is a hard runtime error rather than a silent return of wrong answers. It's the kind of defensive validation worth keeping because the failure mode is so dangerous — without it, Dijkstra on a negative-weight graph would return *plausible-looking* but *wrong* distances, and silently. Chapter 35 will introduce Bellman-Ford, which handles negative weights correctly; until then, the check makes the failure visible.

The next section runs the algorithm against the canonical graph from chapter 31 and watches the heap evolve one pop at a time.

## A run, traced by hand

Take the canonical six-vertex graph from chapter 31, with the weights I assigned there. Run Dijkstra from `A` and watch the heap and the `dist` dictionary evolve through each pop.

Initialization: `dist[A] = 0`, all other vertices implicit at $\infty$. The priority queue holds `(0, A)`.

**Pop `(0, A)`.** Finalize `A`. Relax `A`'s edges: `A → B` with weight 5 updates `dist[B] = 5`, `A → C` with weight 3 updates `dist[C] = 3`. Push `(5, B)` and `(3, C)`.

**Pop `(3, C)`.** Finalize `C`. Relax `C`'s edges: `C → A` would tighten `dist[A]`, but `A` is already finalized, so the relaxation is harmless (the conditional refuses to update because $0 + 3 = 3$ isn't less than $0$). `C → B` offers $3 + 2 = 5$, which isn't an improvement over the current `dist[B] = 5`. `C → D` offers $3 + 1 = 4$, an improvement: `dist[D] = 4`, push `(4, D)`. `C → E` offers $3 + 4 = 7$: `dist[E] = 7`, push `(7, E)`.

**Pop `(4, D)`.** Finalize `D`. Relax: `D → B` offers $4 + 6 = 10$, worse. `D → C` blocked by finalization. `D → E` offers $4 + 2 = 6$, an improvement over the current 7: `dist[E] = 6`, push `(6, E)`. `D → F` offers $4 + 3 = 7$: `dist[F] = 7`, push `(7, F)`. The heap now holds `(5, B)`, `(6, E)`, `(7, E)`, `(7, F)` — note that *two* entries for `E` are alive in the heap, one stale (the `(7, E)` from earlier) and one current. Lazy deletion will sort it out.

**Pop `(5, B)`.** Finalize `B`. Relax: `B`'s neighbors are `A`, `C`, `D` — all already finalized, so nothing to do.

**Pop `(6, E)`.** Finalize `E`. Relax `E`'s edges: `C` and `D` finalized; `E → F` offers $6 + 5 = 11$, worse than the current 7.

**Pop `(7, E)`.** `E` is in `finalized` already. Skip — this was the stale entry from the third pop. The lazy-delete trick costs one $O(\log n)$ pop plus an $O(1)$ skip; that's the price of avoiding a real decrease-key implementation.

**Pop `(7, F)`.** Finalize `F`. Relax: `D` and `E` finalized; nothing to do.

The priority queue is now empty. The algorithm halts. Final distances: `dist[A] = 0`, `dist[B] = 5`, `dist[C] = 3`, `dist[D] = 4`, `dist[E] = 6`, `dist[F] = 7`.

Run the actual implementation against the trace.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.dijkstra import dijkstra

g = AdjacencyList[str](directed=False)
for u, v, w in [("A", "B", 5), ("A", "C", 3), ("B", "C", 2), ("B", "D", 6),
                ("C", "D", 1), ("C", "E", 4), ("D", "E", 2), ("D", "F", 3),
                ("E", "F", 5)]:
    g.add_edge(u, v, w)

dist, parent = dijkstra("A", g.weighted_neighbors)

print("vertex | dist | parent")
print("-------+------+-------")
for v in sorted(dist):
    print(f"   {v}   |  {dist[v]:>3.0f} |   {parent[v]}")
```

Same numbers as the hand trace. The parent dictionary records the predecessor on the chosen shortest path, which `reconstruct_path` from chapter 32 turns back into a source-first path.

```python
from codex.graphs.bfs import reconstruct_path

for target in ["B", "D", "E", "F"]:
    path = reconstruct_path(parent, target)
    weight = dist[target]
    print(f"   shortest path A -> {target} (weight {weight:.0f}): {path}")
```

Compare the paths to BFS from chapter 32. BFS reported the path `A → B → D → F` with three hops; Dijkstra reports `A → C → D → F` with weight 7, a fundamentally different route. BFS optimizes hop count, blind to weights. Dijkstra optimizes weighted distance, blind to hop count. The same canonical graph hides two different "shortest" paths depending on what metric you care about.

The `A → B → D → F` path that BFS picked has weight $5 + 6 + 3 = 14$. Twice Dijkstra's cost for the same hop count. If the weights model road distances or transit fares or processing time, the BFS path is the wrong answer. If they model just hop count or one-step costs, the BFS path is fine.

That correctness depends on one assumption the BFS comparison quietly ignored: no edge in the graph carried a negative weight.

## Why non-negative weights

Here is where the non-negativity assumption does its work. Dijkstra's correctness rests on the *greedy choice property*: when the algorithm picks the smallest-`dist` tentative vertex `u` and finalizes it, the current `dist[u]` is already the true shortest-path distance. No path discovered later could be shorter. This holds because every other tentative vertex has `dist` $\ge$ `dist[u]`, and any path from the source that doesn't go through `u` directly has to pass through some other tentative vertex first — and from there, extending by even one more non-negative edge can only increase, not decrease, the total weight. So no detour through any other tentative vertex could beat the path the algorithm has already found.

The non-negativity assumption is exactly what makes that argument work. Allow even a single negative-weight edge and the property collapses. Consider a tiny graph with three vertices `A`, `B`, `C`, edges `A → B` with weight 5, `A → C` with weight 3, and `C → B` with weight $-10$. The shortest path from `A` to `B` is `A → C → B` with weight $3 - 10 = -7$. Dijkstra from `A` would pop `(0, A)`, finalize `A`, then pop `(3, C)`, finalize `C`, then pop `(5, B)`, finalize `B` with `dist[B] = 5`. That answer is wrong: at the moment `B` was finalized, the relaxation `dist[B] = 3 + (-10) = -7` was still pending in the future, but the greedy choice had already fired and committed to 5.

The implementation refuses to run on negative weights for exactly this reason. Bellman-Ford in chapter 35 handles the negative case by abandoning the greedy choice — it relaxes every edge in every iteration, $n - 1$ times, paying $\Theta(nm)$ for the privilege.

A more subtle issue: even *zero*-weight edges work fine for Dijkstra (the argument above only requires $w \ge 0$, not $w > 0$). A useful sanity check on any Dijkstra implementation is to verify that zero-weight edges don't cause infinite loops, double-counting, or any other pathology — the algorithm should simply treat a zero-weight edge as "instant teleport" and finalize the destination as soon as the source is finalized. The implementation above does that correctly because the lazy-deletion skip ignores re-finalized vertices.

## The three questions, applied

### Is it correct?

The correctness invariant is **when Dijkstra finalizes vertex `u` (i.e., pops it from the heap for the first time), `dist[u]` equals the true shortest-path distance from the source to `u`.** The proof is induction on the order of finalization. The source is finalized first with `dist[source] = 0`, which is correct. For any later vertex `u` finalized at distance `d`, consider the true shortest path $P$ from the source to `u`. The first vertex of $P$ that hasn't been finalized at the moment `u` is popped is `u` itself, by the structure of the algorithm — every prefix of $P$ up to but not including `u` consists of finalized vertices, because otherwise there'd be a tentative vertex on $P$ with `dist` strictly less than `d`, contradicting the greedy choice. So $P$ is the path-from-source-to-`u`-through-finalized-vertices, and Dijkstra has already relaxed every edge of $P$ in the order they appear; by induction the relaxations recorded the true distance of each prefix, and the final relaxation set `dist[u]` to the true distance of $P$.

The one step the whole argument turns on is "any prefix of $P$ has `dist` $\le$ d at the moment `u` is popped." Non-negative weights are what make this true: extending any finalized vertex's distance by one more edge weight can only increase, not decrease, the result. With a negative-weight edge in the picture, the prefix-distance bound fails and the greedy choice produces wrong answers.

The lazy-deletion skip preserves correctness because a vertex that's already in `finalized` has, by the invariant above, its true shortest-path distance recorded; any later pop that names the same vertex with a larger distance is a stale upper bound that the algorithm can safely discard.

### How efficient is it?

Dijkstra runs in $\Theta((n + m) \log n)$ time and $\Theta(n + m)$ space on an adjacency-list graph using a binary-heap priority queue. The heap holds at most $m$ entries total over the course of the algorithm (one per edge relaxation that improved a distance), with each `push` and `pop` costing $O(\log m) = O(\log n)$ amortized (since $m \le n^2$). The outer loop runs at most once per heap entry, so the total work is $\Theta(m \log n)$ for the heap operations plus $\Theta(n + m)$ for the constant-time relaxation conditionals. The two add to $\Theta((n + m) \log n)$.

Space is dominated by the heap, the `dist` and `parent` dictionaries, and the `finalized` set — each $O(n)$ in the worst case where every vertex is reachable. The heap can temporarily hold $\Theta(m)$ stale entries before they're popped and skipped; this is the lazy-deletion overhead. A version with explicit decrease-key (using a Fibonacci heap or a pairing heap) eliminates the stale entries and tightens the bound to $\Theta(n \log n + m)$, but the constant factors are bad enough that production implementations almost always stick with the binary heap.

For a dense graph with $m = \Theta(n^2)$, the binary-heap version is $\Theta(n^2 \log n)$, slightly worse than the $\Theta(n^2)$ achievable with a linear-scan implementation. A reasonable implementation picks the algorithm by density: linear scan for $m = \Omega(n^2 / \log n)$, binary heap otherwise. Most graphs in practice are sparse enough that the binary heap is the right call by a wide margin.

### Is it optimal?

For single-source shortest paths in graphs with non-negative weights, the lower bound depends on the model. In the comparison-based model (the algorithm can compare edge weights but not, say, sort them in linear time using radix), $\Omega(n \log n + m)$ is tight: you need at least $n \log n$ to maintain the priority queue across $n$ extract-min operations, and you need at least $m$ to examine every edge. Dijkstra with a Fibonacci heap matches this bound. Dijkstra with a binary heap is $O(\log n)$ off for the dense case but within a constant factor for sparse graphs.

In a stronger model where the edge weights are bounded integers, Thorup's 1999 algorithm runs in $O(n + m)$ time — *linear* in the graph size, no $\log n$ factor — but the constant factors and the implementation complexity are large enough that it's almost never used in practice. For real workloads, the binary-heap Dijkstra is the algorithm production graph libraries ship, and the constant factors are good enough that the asymptotic suboptimality rarely matters.

For graphs with negative-weight edges, $\Omega(nm)$ is the lower bound in the comparison model (Bellman-Ford in chapter 35 matches this), and no asymptotic improvement is possible. Dijkstra's advantage over Bellman-Ford — a factor of $n/\log n$ — is bought entirely by the non-negativity assumption.

## What this chapter teaches

**First, the container at the center of the loop is the algorithm.** This is the third time Part V has made the point. A queue gave BFS and shortest paths in hops; a stack gave DFS and structural decomposition; a heap gives Dijkstra and weighted shortest paths. The skeleton — visit, mark, expand, repeat — is the same in all three. The data structure is what changes, and the algorithm's character changes with it. The pattern is so reliable that the right way to design a new graph algorithm is often to ask: *what discipline at the container would compute the answer I want?* If you can answer that, the rest of the algorithm usually writes itself.

**Second, relaxation is the unifying technique.** Dijkstra is one of four shortest-path-family algorithms that all share the same per-edge step: compare `dist[u] + w(u, v)` against `dist[v]`, update if smaller. Bellman-Ford in chapter 35 does the same relaxation but applies it $n - 1$ times to every edge instead of using a heap. Floyd-Warshall in chapter 35 generalizes the relaxation to all pairs of vertices, with the intermediate vertex set growing one vertex at a time. Prim's MST in chapter 36 uses the same relaxation step with `dist[u] + w(u, v)` replaced by just `w(u, v)`. Four algorithms, one inner loop body.

**The greedy choice property is the algorithm's correctness, and the choice of greedy criterion is what restricts the algorithm's applicability.** Dijkstra's greedy choice — finalize the smallest-`dist` tentative vertex — works because non-negative weights guarantee that detours can only make paths longer. Other greedy graph algorithms have their own greedy choices and their own correctness properties: Kruskal's MST in chapter 36 picks the smallest-weight edge that doesn't form a cycle; Prim's MST in chapter 36 picks the smallest-weight edge crossing the cut between the current tree and the rest of the graph. In each case, naming the greedy criterion is half the algorithm; proving it correct is the other half. The pattern recurs throughout the algorithm literature, and getting comfortable with it here makes the rest of Part V's greedy algorithms — and Part VI's dynamic-programming alternatives, which arise precisely when no greedy choice works — easier to read.

## Notes and further reading

Edsger Dijkstra published the algorithm in his 1959 paper "A Note on Two Problems in Connexion with Graphs" (*Numerische Mathematik* 1:269–271). The paper is three pages long and contains two unrelated graph algorithms — the shortest-path algorithm and an MST algorithm — both presented as elegant solutions to problems Dijkstra encountered while testing the ARMAC computer in Amsterdam. The original paper's data structure was a linear-scan tentative set, not a heap; the $\Theta((n + m) \log n)$ heap-based variant came later, and the Fibonacci-heap variant that matches the comparison-model lower bound is due to Fredman and Tarjan's 1984 paper "Fibonacci heaps and their uses in improved network optimization algorithms" (*JACM* 34(3):596–615).

CLRS chapter 24 covers Dijkstra with the same lazy-deletion technique used here and the same correctness argument, plus a treatment of decrease-key-capable priority queues (Fibonacci heaps, pairing heaps) that this chapter has skipped. Sedgewick and Wayne's *Algorithms* (4th ed.) §4.4 presents Dijkstra alongside Prim and shows the structural parallel explicitly — the same code with one substitution. For a deeper treatment of the algorithm's role in the shortest-path family, Robert Tarjan's *Data Structures and Network Algorithms* (SIAM, 1983) chapter 7 develops the relaxation framework and shows Dijkstra, Bellman-Ford, and Floyd-Warshall as variations on a single template.

For applications: Dijkstra powers OSPF (Open Shortest Path First, the dominant routing protocol on the Internet's interior gateways), every modern GPS routing service in some form (usually augmented with bidirectional search and contraction hierarchies, neither of which change the asymptotic complexity but make the constant factors dramatically better for road-network graphs), and the SCION inter-domain routing architecture's path selection. A* search (Russell and Norvig, *AIMA* chapter 3) is Dijkstra with a heuristic added to the priority — if the heuristic is admissible (never overestimates the true remaining distance), A* finds the same optimal paths Dijkstra finds, often expanding far fewer vertices.

For the bidirectional Dijkstra variant that runs the algorithm from both source and target simultaneously and meets in the middle, the canonical reference is Dantzig's 1960 monograph *Linear Programming and Extensions* §17.4; the technique is a $\sqrt{n}$-factor improvement on the explored-vertex count when both endpoints are known up front, and is the standard form in production routing engines.

In the next chapter I'll lift the non-negativity restriction. Bellman-Ford handles negative edges and detects negative-weight cycles; Floyd-Warshall pushes the relaxation framework to all-pairs shortest paths. Both are *relaxation* algorithms in the sense Dijkstra is — the per-edge step is identical — and the next chapter develops the family explicitly. The cost shape changes from $\Theta((n + m) \log n)$ to $\Theta(nm)$ for Bellman-Ford and $\Theta(n^3)$ for Floyd-Warshall, which is the price of giving up the greedy choice.
