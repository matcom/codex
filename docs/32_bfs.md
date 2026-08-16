# Expanding the frontier, one ring at a time

The queue from chapter 11 wanted a problem. The adjacency list from chapter 31 wanted an algorithm. Breadth-first search is what happens when you point them at each other. Start at one vertex; put its neighbors in a queue; pop the next vertex off the queue, push its unvisited neighbors; repeat until the queue is empty. That five-line discipline does four useful things at once: it visits every vertex reachable from the source, it visits them *in order of distance from the source*, it builds a shortest-path tree along the way, and it does all of that in $\Theta(n + m)$ time on any graph small enough to fit in memory and many that aren't.

By the end of this chapter you will have implemented BFS as a queue-driven sweep over an adjacency-list graph, augmented it to record distances and parent pointers, used those pointers to reconstruct shortest paths in unweighted graphs, partitioned a disconnected graph into its connected components, and run BFS against an *implicit* graph — a maze whose cells exist only as a neighbor function — to find the shortest passable path between two squares. The pattern recurs across the rest of the part. Dijkstra (chapter 34) replaces the queue with a priority queue and the same skeleton solves weighted shortest paths. Edmonds-Karp (chapter 38) finds augmenting paths in flow networks via BFS in the residual graph. The layered-frontier idea you'll build here is the skeleton every later chapter reuses.

## The five-line skeleton

BFS keeps two pieces of state: a queue of vertices waiting to be expanded, and a set of vertices already seen. Both are initialized with the source vertex. The main loop pops the front of the queue, walks each of the popped vertex's neighbors, and for any neighbor that hasn't been seen yet, marks it seen and pushes it onto the back of the queue. When the queue empties, every reachable vertex has been visited exactly once.

The detail that earns most of the bugs: **mark a vertex as seen the moment you enqueue it, not when you dequeue it.** If you delay the marking, a vertex with two parents in the BFS tree gets enqueued twice — and the second visit either does redundant work or, in the path-reconstruction variant later in this chapter, corrupts the parent pointer. Mark on enqueue, never on dequeue.

Here's the skeleton with distance bookkeeping folded in. The output is a dictionary mapping each reachable vertex to its distance (in edges) from the source. Unreachable vertices simply don't appear in the dictionary.

```python {export=src/codex/graphs/bfs.py}
from collections.abc import Hashable, Iterator
from codex.graphs.implicit import NeighborFn
from codex.structures.queue import LinkedQueue


def bfs_distances[V: Hashable](source: V, neighbors: NeighborFn[V]) -> dict[V, int]:
    """Return a dict mapping each vertex reachable from source to its
    distance in edges. Unreachable vertices are absent.
    """
    dist: dict[V, int] = {source: 0}
    queue: LinkedQueue[V] = LinkedQueue()
    queue.enqueue(source)
    while queue:
        u = queue.dequeue()
        for v in neighbors(u):
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.enqueue(v)
    return dist
```

Twelve lines. The signature deliberately takes a `NeighborFn[V]` rather than a graph instance — chapter 31 left the implicit-graph case calling for exactly this shape, and accepting a function means the same BFS runs against `AdjacencyList.neighbors`, against `AdjacencyMatrix.neighbors`, against `grid_neighbors`, against a closure that fetches a webpage to discover its outlinks. The graph object never has to exist as a concrete data structure.

The `dist` dictionary doubles as the "seen" set. A vertex is in `dist` if and only if it's already been enqueued, so checking `v not in dist` is the same as asking "have I seen $v$ yet?" The first time a vertex enters `dist`, it gets its true shortest-path distance — and that distance is correct by construction, because the queue's FIFO discipline guarantees that all vertices at distance $k$ are enqueued before any vertex at distance $k + 1$. Take the invariant on trust for the moment and watch the algorithm work on the canonical graph from chapter 31; I'll prove it in the "three questions" section.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.bfs import bfs_distances

g = AdjacencyList[str](directed=False)
for u, v, _ in [("A", "B", 5), ("A", "C", 3), ("B", "C", 2), ("B", "D", 6),
                ("C", "D", 1), ("C", "E", 4), ("D", "E", 2), ("D", "F", 3),
                ("E", "F", 5)]:
    g.add_edge(u, v)

dist = bfs_distances("A", g.neighbors)
for v in sorted(dist):
    print(f"   distance(A -> {v}) = {dist[v]}")
```

Six vertices, all reachable from `A`, distances 0 through 3 in edges. `B` and `C` are direct neighbors of `A`; `D` and `E` are two hops away; `F` is three hops, the farthest from `A` in this graph. The weights I assigned in chapter 31 are silently ignored — BFS treats every edge as cost 1, which is the right answer when you want shortest paths in *number of hops*, the wrong answer when edge weights matter, and the reason chapter 34 will need a different algorithm for the weighted case.

Distances alone tell you *how far*; the next thing the chapter needs is the actual route.

A subtle point worth flagging: the BFS distance from `A` to `D` is 2, but in chapter 31's weighted graph the cheapest weighted path from `A` to `D` is `A → C → D` with cost 4 (versus `A → B → D` with cost 11). BFS won't tell you that — its concept of "shortest" is *fewest edges*, full stop. Dijkstra's algorithm in chapter 34 generalizes BFS to weighted edges; the skeleton stays nearly the same but the queue gets upgraded to a priority queue.

## Recording the path home

To recover the *path* — the actual sequence of vertices from source to target — I need one more piece of bookkeeping: a parent pointer. When BFS first discovers a vertex $v$ via an edge from $u$, it remembers that $u$ is the vertex it came from. Chasing parent pointers backward from any reachable vertex reconstructs the shortest path to the source.

The augmented BFS returns two dictionaries instead of one: `dist` as before, plus `parent`, mapping each non-source reachable vertex to the vertex it was discovered from. The source itself maps to `None`.

```python {export=src/codex/graphs/bfs.py}
def bfs[V: Hashable](
    source: V, neighbors: NeighborFn[V]
) -> tuple[dict[V, int], dict[V, V | None]]:
    """Run BFS from source. Return (dist, parent) where dist maps each
    reachable vertex to its distance and parent maps each non-source
    reachable vertex to the vertex it was first discovered from. The
    source maps to None in parent.
    """
    dist: dict[V, int] = {source: 0}
    parent: dict[V, V | None] = {source: None}
    queue: LinkedQueue[V] = LinkedQueue()
    queue.enqueue(source)
    while queue:
        u = queue.dequeue()
        for v in neighbors(u):
            if v not in dist:
                dist[v] = dist[u] + 1
                parent[v] = u
                queue.enqueue(v)
    return dist, parent
```

Same structure, one extra dictionary, one extra write per vertex discovery. The dictionaries are kept in lockstep — every vertex in `dist` is also in `parent` and vice versa, so the check `v not in dist` could equally be `v not in parent`. Using one of the two as the "seen" predicate and keeping the other purely for return is conventional; mixing them confuses the bookkeeping for no benefit.

Now reconstruction. Starting from any reachable target, follow parent pointers backward until you reach the source. Reversing the resulting list gives the shortest path from source to target in source-first order.

```python {export=src/codex/graphs/bfs.py}
def reconstruct_path[V: Hashable](
    parent: dict[V, V | None], target: V
) -> list[V] | None:
    """Walk parent pointers backward from target to the source (the
    vertex whose parent is None). Return the path in source-first order,
    or None if target is not in parent (i.e., unreachable).
    """
    if target not in parent:
        return None
    path: list[V] = []
    current: V | None = target
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path
```

Twelve lines, one allocation, one in-place reverse. The path length is the number of vertices, which equals the distance in edges plus one — a useful invariant for sanity-checking the result.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.bfs import bfs, reconstruct_path

g = AdjacencyList[str](directed=False)
for u, v, _ in [("A", "B", 5), ("A", "C", 3), ("B", "C", 2), ("B", "D", 6),
                ("C", "D", 1), ("C", "E", 4), ("D", "E", 2), ("D", "F", 3),
                ("E", "F", 5)]:
    g.add_edge(u, v)

dist, parent = bfs("A", g.neighbors)

for target in ["B", "D", "F"]:
    path = reconstruct_path(parent, target)
    print(f"   path A -> {target}: {path}  (length {dist[target]})")
```

Three paths reconstructed in source-first order. `A → B` is one hop; `A → C → D` (or `A → B → D`, depending on neighbor-iteration order) is two; `A → C → D → F` is three. BFS returns *one* shortest path per target, not all of them. In this graph there are two shortest paths from `A` to `D` (one through `B`, one through `C`) and BFS picks the one whose intermediate vertex was enqueued first — which depends on the iteration order of the adjacency dictionary. The choice is arbitrary but deterministic for a given dictionary insertion order. Enumerating *all* shortest paths is a different algorithm with cost $\Theta(\text{number of paths})$ on top of the BFS itself; I'll skip it here.

## The layered frontier

There's a second way to organize the same algorithm, and I find it more honest about what BFS actually computes. Expand the frontier one *layer* at a time, where layer $k$ is the set of vertices at distance exactly $k$ from the source. The level-by-level emission pattern is what gave BFS its name: "breadth-first" means expanding the full breadth of the frontier before moving outward.

The layered formulation is sometimes more natural than the queue-based formulation. For problems like "find all vertices within distance $k$" or "what's the diameter of this graph?" or "what does the BFS tree look like, level by level?", emitting layers directly is cleaner than reconstructing them from distance values. The implementation keeps two lists — the current frontier and the next frontier — and swaps them at the end of each layer.

```python {export=src/codex/graphs/bfs.py}
def bfs_layers[V: Hashable](
    source: V, neighbors: NeighborFn[V]
) -> Iterator[list[V]]:
    """Yield each BFS layer as a list, starting with [source] at layer 0.
    Layer k is the set of vertices at distance exactly k from source.
    """
    seen: set[V] = {source}
    frontier: list[V] = [source]
    while frontier:
        yield frontier
        next_frontier: list[V] = []
        for u in frontier:
            for v in neighbors(u):
                if v not in seen:
                    seen.add(v)
                    next_frontier.append(v)
        frontier = next_frontier
```

No queue this time. The current layer is held as a list (its ordering doesn't matter for correctness), and at the end of each round the next layer takes over as the frontier. The total work is the same $\Theta(n + m)$ — each vertex enters the seen set once, each edge is walked once — but the structure of the computation is now level-synchronous rather than vertex-synchronous. The same idea reappears in parallel BFS implementations on multi-core machines, where each layer can be expanded by many threads in parallel and the synchronization happens once per layer rather than once per vertex.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.bfs import bfs_layers

g = AdjacencyList[str](directed=False)
for u, v, _ in [("A", "B", 5), ("A", "C", 3), ("B", "C", 2), ("B", "D", 6),
                ("C", "D", 1), ("C", "E", 4), ("D", "E", 2), ("D", "F", 3),
                ("E", "F", 5)]:
    g.add_edge(u, v)

for k, layer in enumerate(bfs_layers("A", g.neighbors)):
    print(f"   layer {k} (distance {k} from A): {sorted(layer)}")
```

Four layers, each one ring farther from the source. Layer 0 is just the source. Layer 1 is `A`'s direct neighbors. Layer 2 is the vertices reachable in two hops but not in one. Layer 3 is `F`, the most-distant vertex in the graph. The graph's *diameter from `A`* — the longest shortest-path distance — is 3, which you read off as the last non-empty layer.

The layered view also makes BFS's bipartite-check pay off cheap. A graph is bipartite iff its vertex set can be split into two color classes with no edges within a class — equivalently, iff a BFS from any starting vertex produces no edges that connect two vertices of the same parity layer. Walk the graph with `bfs_layers`, alternate colors layer by layer, and on each edge check that the endpoints have different colors. If any edge violates the rule, the graph isn't bipartite; if no edge does, it is. The check is $\Theta(n + m)$, same as BFS itself.

What if the graph isn't connected? BFS from one source can't reach everything; you need a sweep.

## One BFS per island

BFS from a single source visits everything reachable from that source — which on a disconnected graph is only the source's connected component. To enumerate *all* connected components, sweep over the vertex set: pick any unvisited vertex, run BFS from it, mark its whole component as visited, repeat until no unvisited vertices remain. Each component is one BFS, each BFS visits its component exactly once, and the total work across all components is $\Theta(n + m)$ because every vertex and every edge gets touched exactly once over the whole sweep.

```python {export=src/codex/graphs/bfs.py}
def connected_components[V: Hashable](
    vertices: Iterator[V] | list[V] | set[V],
    neighbors: NeighborFn[V],
) -> list[set[V]]:
    """Sweep BFS over the vertex set. Return a list of components, each
    as a set of vertices. The component containing vertex u is the set
    of vertices reachable from u via the undirected closure of neighbors.
    """
    seen: set[V] = set()
    components: list[set[V]] = []
    for start in vertices:
        if start in seen:
            continue
        component: set[V] = {start}
        queue: LinkedQueue[V] = LinkedQueue()
        queue.enqueue(start)
        while queue:
            u = queue.dequeue()
            for v in neighbors(u):
                if v not in component:
                    component.add(v)
                    queue.enqueue(v)
        seen |= component
        components.append(component)
    return components
```

Same skeleton as the basic BFS, wrapped in an outer loop. The `seen` set is shared across components — once a vertex enters any component it can't enter another — but inside one component the local `component` set is the seen-predicate. Returning a list of sets makes downstream queries cheap: "is `u` connected to `v`?" is one membership check per component until you find one containing both, or you reach the end.

For directed graphs, this routine computes *weakly connected* components — the components you'd get if you ignored edge directions. *Strongly connected* components are a different question requiring DFS-based discovery and finish times; chapter 37 handles that.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.bfs import connected_components

# Build a graph with three components: {1,2,3,4} chain, {5,6} pair, {7} singleton
g = AdjacencyList[int](directed=False)
for u, v in [(1, 2), (2, 3), (3, 4), (5, 6)]:
    g.add_edge(u, v)
g.add_vertex(7)

components = connected_components(g.vertices(), g.neighbors)
print(f"number of components: {len(components)}")
for i, comp in enumerate(sorted(components, key=lambda c: min(c))):
    print(f"   component {i + 1}: {sorted(comp)}")
```

Three components: the 4-chain, the pair, and the isolated vertex. The cost of computing this on a million-vertex graph is the same as one BFS from a single source — the work is shared across the components, not multiplied.

## BFS on a graph that doesn't exist

This is the section I most wanted to write, and the one chapter 31 spent its closing pages setting up. BFS accepts a `NeighborFn[V]` and doesn't care whether that function reads from a stored adjacency list, computes neighbors on the fly, or fetches a webpage and parses its outlinks. The same five-line skeleton finds the shortest passable path through a maze that has never been materialized as a graph object.

Take a small maze on a 5×5 grid. The maze is represented by its set of *blocked* cells; the remaining cells are passable, and a cell's neighbors are its passable 4-connected grid neighbors. Chapter 31's `grid_neighbors` already produces the right `NeighborFn`. BFS finds the shortest path from start to goal, in passable-cell-count, by treating the grid as an implicit graph.

```python
from codex.graphs.implicit import grid_neighbors
from codex.graphs.bfs import bfs, reconstruct_path

# 5x5 maze, '#' is a wall, '.' is open. Start at (0,0), goal at (4,4).
blocked = frozenset({
    (1, 0), (1, 1), (1, 3),
    (3, 1), (3, 2), (3, 3),
})
nbrs = grid_neighbors(width=5, height=5, blocked=blocked)

dist, parent = bfs((0, 0), nbrs)
path = reconstruct_path(parent, (4, 4))

print(f"shortest path: {dist[(4, 4)]} steps over {dist[(4, 4)] + 1} cells")
print(f"path: {path}")
print()
# Render the maze with the path overlaid
for y in range(5):
    row = ""
    for x in range(5):
        if (x, y) in blocked:
            row += "# "
        elif (x, y) in (path or []):
            row += "o "
        else:
            row += ". "
    print(f"   {row}")
```

The maze has two `#`-shaped walls that force the path to weave around. BFS finds the shortest path — eight steps, nine cells — without ever materializing the grid as a graph object. The 25-cell grid is trivial here, but the same code works on a $10000 \times 10000$ grid where storing the full adjacency list would be $\Theta(10^8)$ entries. The implicit-graph representation lets BFS solve problems whose state space is too large to enumerate; the only cost is one `grid_neighbors` call per cell visit, and the cost stays $\Theta(\text{visited cells} + \text{visited edges})$ rather than scaling with the full grid size.

Word-ladder puzzles work the same way. The vertices are words of a fixed length; the neighbors of a word are the words you can reach by changing exactly one letter; BFS from `"COLD"` to `"WARM"` finds the shortest letter-by-letter transformation. The graph is exponentially large in principle (every length-4 string is a vertex), but BFS only enumerates the reachable subset, and on a dictionary of English words the reachable component from any common word is a few thousand vertices at most. The implicit framing is what makes the problem tractable; storing the full word graph would be wasteful and unnecessary.

## The three questions, applied

### Is it correct?

The correctness of BFS rests on one invariant: **when a vertex is dequeued, its recorded distance is its true shortest-path distance from the source.** The proof is induction on the dequeue order. The source itself is dequeued first with distance 0, which is correct. For any later vertex $v$ dequeued at recorded distance $d$, $v$ was enqueued at the moment some vertex $u$ at distance $d - 1$ visited it as a neighbor — and $u$'s distance was correct by the induction hypothesis. So $v$'s recorded distance is at most $d$. It's also at least $d$, because any vertex enqueued before $v$ had distance $\le d - 1$, and a shorter path to $v$ would have produced an earlier enqueue. The recorded distance equals the true shortest-path distance.

The "mark on enqueue, not on dequeue" discipline is what keeps this argument tight. If a vertex $v$ were enqueued twice — once at distance $d_1$ and once at distance $d_2$ with $d_1 \le d_2$ — the second visit would either overwrite $v$'s correct shortest distance with a longer one (corrupting the dictionary) or be filtered out by an "already-dequeued" check (adding a layer of bookkeeping). Marking on enqueue prevents the double-enqueue from ever happening, which is what lets the dictionary serve as the seen-set with no additional state.

Path reconstruction is correct by the same induction. Each non-source vertex's parent pointer points at the vertex from which it was first discovered, and the first discovery is via a shortest path (by the dequeue invariant above). Chasing parent pointers backward therefore produces a shortest path, in reverse, which `reconstruct_path` un-reverses.

### How efficient is it?

BFS runs in $\Theta(n + m)$ time and $\Theta(n)$ extra space on a graph with $n$ vertices and $m$ edges, when the graph is represented as an adjacency list. Each vertex is enqueued at most once (the dictionary `dist` enforces this) and dequeued at most once, contributing $\Theta(n)$ total queue work. Each edge is walked at most once per endpoint — twice total for undirected graphs, once for directed — and each walk is $O(1)$ on an adjacency list, contributing $\Theta(m)$ total. The two pieces add to $\Theta(n + m)$. Space is dominated by the `dist` and `parent` dictionaries, which together hold one entry per reachable vertex; in the worst case where every vertex is reachable, that's $\Theta(n)$.

On an adjacency *matrix* the cost shape changes. Finding the neighbors of $u$ now takes $\Theta(n)$ work — a row scan — and BFS calls `neighbors` once per dequeued vertex, so the total cost rises to $\Theta(n \cdot n) = \Theta(n^2)$. For a sparse graph with $m = O(n)$ that's a factor of $n$ slowdown over the adjacency-list version; for a dense graph with $m = \Theta(n^2)$ the two costs match. Chapter 31's table predicted this, and BFS is the cleanest demonstration of the prediction in action.

On an implicit graph the cost depends on the `NeighborFn`. For `grid_neighbors`, each call is $O(1)$ (four directions, four bounds checks), so BFS on an implicit grid is $\Theta(\text{visited cells})$ — strictly better than building the explicit graph and then running BFS on it. For more expensive neighbor functions (a web crawl that fetches a page, a word-ladder generator that scans the dictionary), the per-call cost dominates and the asymptotic shape becomes $\Theta(\text{visited vertices} \cdot \text{cost per call})$.

### Is it optimal?

For unweighted shortest paths from a single source, $\Theta(n + m)$ is the lower bound. Every reachable vertex has to be reached, and every edge incident to a reachable vertex has to be examined to be sure no shorter path exists. BFS achieves the bound exactly. No algorithm can do better in the unit-weight model.

A stronger optimality claim holds when the graph is *implicit*. BFS's per-vertex cost is the cost of one `neighbors` call plus $O(1)$ bookkeeping, which is asymptotically tight: any algorithm that finds shortest paths in an implicit graph has to consult the neighbor function at least once per visited vertex, and bookkeeping below $O(1)$ per visit is impossible. The implicit-graph BFS is therefore optimal *for problems whose state space is too large to materialize* — and that is what makes it the workhorse algorithm of AI search and combinatorial enumeration.

For weighted shortest paths the question changes. BFS solves the unweighted case in $\Theta(n + m)$; Dijkstra in chapter 34 solves the weighted case (with non-negative weights) in $\Theta((n + m) \log n)$ using a heap. The $\log n$ factor is what the heap pays for, and the price is unavoidable when edge weights stop being unit.

## What this chapter teaches

**First, the right discipline at the queue is the right answer at the graph.** BFS visits vertices in *the order they were first seen* — that's the FIFO contract from chapter 11, applied to graph traversal. The contract guarantees that vertices come out in distance order, which guarantees that the first-discovered path is a shortest path. Replace the queue with a stack and you get DFS (chapter 33): different discipline, different cost shape, completely different set of facts about the graph. Replace it with a priority queue and you get Dijkstra (chapter 34): the heap's "smallest-first" discipline solves weighted shortest paths the way the queue's FIFO discipline solves unweighted ones. The choice of container determines the algorithm's character; the rest of the code stays nearly the same.

**Second, the layered frontier is the structural object, not the queue.** The queue is an implementation detail — it's how you maintain the frontier from one layer to the next. The *layered* view of BFS (every vertex at distance $k$ forms layer $k$) is what the algorithm actually computes, and it's the right mental model for any algorithm that builds on BFS. Edmonds-Karp's augmenting paths in chapter 38 are BFS layers in the residual graph. The bipartite check is a parity argument on BFS layers. Parallel BFS expands one layer at a time across many cores. Once you see BFS as "expand the frontier outward, one ring at a time," the variations stop being separate algorithms and start being variations on a single shape.

A third observation. **The implicit-graph framing is what makes graph algorithms applicable beyond the cases where you can store the graph.** A maze on a $10000 \times 10000$ grid has $10^8$ vertices — too many to materialize on most machines, trivial for BFS as long as the start-to-goal path doesn't touch a substantial fraction of them. A word-ladder graph has $26^4 \approx 4 \times 10^5$ length-4 strings — too many to enumerate, fine for BFS because most aren't reachable from any English word. The pattern recurs across the rest of this part and through the AI-search literature: define the state graph implicitly via a successor function, and let BFS or its descendants explore only the part that matters.

## Notes and further reading

BFS in its modern form is usually attributed to Edward Moore's 1957 maze-solving algorithm, presented at the International Symposium on the Theory of Switching at Harvard (proceedings published 1959 as "The shortest path through a maze," *Proceedings of an International Symposium on the Theory of Switching*, pp. 285–292). Konrad Zuse's 1945 dissertation contained an essentially identical algorithm for graph traversal but went unpublished for decades; C. Y. Lee's 1961 paper "An Algorithm for Path Connections and Its Applications" (*IRE Transactions on Electronic Computers* EC-10:346–365) independently rediscovered the same algorithm for VLSI routing. The "breadth-first search" name is post-1960s and tracks the algorithm's role in graph theory rather than its earlier applications.

CLRS chapter 22 covers BFS with the same skeleton and the same proof. Sedgewick and Wayne's *Algorithms* (4th ed.) §4.1 presents BFS alongside DFS and walks through the connected-components computation. For the parallel BFS variant — important on multi-core hardware and the basis of the Graph500 benchmark — the canonical reference is Beamer, Asanović, and Patterson's "Direction-Optimizing Breadth-First Search" (*SC '12*), which alternates between the layer-expansion form shown here and a "bottom-up" pass that checks each unvisited vertex for any frontier neighbor; on graphs with high-degree hub vertices the bottom-up pass is dramatically faster than the standard top-down form.

For implicit-graph BFS in AI search, Russell and Norvig's *Artificial Intelligence: A Modern Approach* chapter 3 covers BFS as one of the *uninformed search* strategies, alongside iterative deepening and uniform-cost search (which generalizes BFS to weighted graphs and is essentially Dijkstra's algorithm in different notation). The book also discusses *bidirectional* search, where BFS runs from both source and target simultaneously and meets in the middle — a $\sqrt{n}$-factor improvement on the explored-vertex count when both endpoints are known up front.

The Edmonds-Karp algorithm — Jack Edmonds and Richard Karp's 1972 paper "Theoretical improvements in algorithmic efficiency for network flow problems" (*Journal of the ACM* 19(2):248–264) — uses BFS to find augmenting paths in flow networks; chapter 38 develops it in full. Worth noting now: every iteration of Edmonds-Karp runs one BFS in the residual graph, so the algorithm's correctness ultimately depends on BFS's "shortest path in edges" guarantee.

In the next chapter I'll keep the graph and swap the queue for a stack. The resulting algorithm — depth-first search — gives up BFS's distance guarantee but gains something else: the ability to expose the *structure* of the graph through discovery and finish times. Cycle detection, topological sort, articulation points, and strong components all fall out of DFS plus a few lines of bookkeeping. The trade is the one chapter 11 already made for you: FIFO answers "what's the layered frontier," LIFO answers "what's the structural decomposition."
