# What you see when you go deep before you go wide

Swap the queue for a stack and the algorithm from chapter 32 becomes a completely different thing. The skeleton is the same — five lines of "mark, expand neighbors, repeat" — but where BFS visited the graph one ring at a time outward from the source, depth-first search rams as far down a single branch as it can, backtracks when it has to, and on its way home leaves behind a structural fingerprint the graph didn't appear to have. That fingerprint is what makes DFS the substrate every structural graph algorithm builds on. Cycle detection, topological ordering, articulation points, strongly connected components, bridge detection — none of these are separate algorithms. They are DFS with a few lines of bookkeeping each, and they all rest on a single property that recursive DFS exposes for free: every vertex is visited inside a time interval, and the intervals from any DFS run form a properly nested parenthesis structure over the vertex set.

By the end of this chapter you will have implemented DFS in two forms (recursive, which is the natural way to think about it, and iterative with an explicit stack, which is the only way to walk a graph deep enough that Python's recursion limit kicks in), recorded discovery and finish timestamps for every vertex, used those timestamps to detect cycles in a directed graph, and read the same timestamps as a *parenthesization* of the DFS tree that makes the algorithm's structural output visible. The vocabulary developed here — discovery times, finish times, tree edges, back edges — is what chapter 37's topological sort and strongly connected components stand on directly. Both of those algorithms are this chapter's DFS plus one extra pass.

## DFS in its natural form

The form I'd write at the keyboard before writing anything cleaner is a recursion. Visit a vertex, mark it, recurse on each of its unvisited neighbors. The recursion stops at vertices whose neighbors are all already visited, the call stack unwinds, and the algorithm finishes when every reachable vertex has been touched exactly once. The whole thing is about ten lines including the wrapper.

```python {export=src/codex/graphs/dfs.py}
from collections.abc import Hashable, Iterable
from sys import setrecursionlimit
from codex.graphs.implicit import NeighborFn
from codex.structures.stack import ArrayStack


def dfs_recursive[V: Hashable](source: V, neighbors: NeighborFn[V]) -> set[V]:
    """Return the set of vertices reachable from source via depth-first
    recursion. Visits each reachable vertex exactly once.
    """
    seen: set[V] = set()
    def visit(u: V) -> None:
        seen.add(u)
        for v in neighbors(u):
            if v not in seen:
                visit(v)
    visit(source)
    return seen
```

Nine lines of substance. The inner `visit` is the recursion; the outer wrapper exists so the `seen` set is shared across the recursive calls without being a global. The order in which a vertex's neighbors are visited determines which path DFS goes down first — the canonical demo from chapter 31 traverses `A → B → C → D → E → F` because that's the insertion order of the adjacency dictionaries, but a different insertion order would give a different traversal. DFS produces *one* depth-first ordering per starting vertex and per neighbor iteration order; the ordering depends on the data structure underneath.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.dfs import dfs_recursive

g = AdjacencyList[str](directed=False)
for u, v, _ in [("A", "B", 5), ("A", "C", 3), ("B", "C", 2), ("B", "D", 6),
                ("C", "D", 1), ("C", "E", 4), ("D", "E", 2), ("D", "F", 3),
                ("E", "F", 5)]:
    g.add_edge(u, v)

reached = dfs_recursive("A", g.neighbors)
print(f"vertices reached from A: {sorted(reached)}")
print(f"all six? {len(reached) == 6}")
```

All six vertices, same set BFS produced in chapter 32. Reachability is a structural property of the graph; both algorithms agree on it. What they disagree on is the *order* of discovery. That order is what later algorithms care about.

## When recursion overflows the stack

Python's default recursion limit is around 1000 frames. A DFS over a graph with a chain of 10000 vertices — perfectly reasonable in practice; think of a linked-list-shaped graph, a path through a long maze, a chain of dependencies in a build system — will hit `RecursionError` before it finishes. The fix is either to raise the limit (`sys.setrecursionlimit`, which trades a stack overflow for a process crash if you go too far) or to convert the recursion into an explicit loop with an explicit stack. The explicit-stack form is the one you ship.

The translation is mechanical. Push the source onto a stack; while the stack is non-empty, pop a vertex; if it hasn't been seen yet, mark it seen and push each of its unvisited neighbors onto the stack. The "mark on push" discipline (the LIFO analogue of BFS's "mark on enqueue") prevents the same vertex from being pushed twice via two different paths, which would otherwise cause $O(n^2)$ work in the worst case.

```python {export=src/codex/graphs/dfs.py}
def dfs_iterative[V: Hashable](source: V, neighbors: NeighborFn[V]) -> set[V]:
    """Iterative DFS using an explicit stack. Same reachability set as
    dfs_recursive, no recursion limit, $O(n)$ stack space.
    """
    seen: set[V] = {source}
    stack: ArrayStack[V] = ArrayStack()
    stack.push(source)
    while stack:
        u = stack.pop()
        for v in neighbors(u):
            if v not in seen:
                seen.add(v)
                stack.push(v)
    return seen
```

Eleven lines. Same skeleton as BFS, swapped queue for stack, same `seen`-as-dictionary trick. The visit order is *not* identical to the recursive form — the iterative version expands the last-pushed neighbor first, which reverses the order in which neighbors of each vertex are explored — but the reachable set is the same. For algorithms that only care about reachability (the connected-components sweep at the end of the chapter, the cycle check in the next section), the iterative form is the right call: it shares the same correctness guarantees with the recursive form and never crashes the interpreter.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.dfs import dfs_iterative

g = AdjacencyList[str](directed=False)
for u, v, _ in [("A", "B", 5), ("A", "C", 3), ("B", "C", 2), ("B", "D", 6),
                ("C", "D", 1), ("C", "E", 4), ("D", "E", 2), ("D", "F", 3),
                ("E", "F", 5)]:
    g.add_edge(u, v)

reached = dfs_iterative("A", g.neighbors)
print(f"vertices reached from A: {sorted(reached)} (iterative)")
```

Same six vertices. The iterative form has one subtlety the recursive form doesn't: if you need a specific DFS *order* — say, to match a textbook proof that walks neighbors left-to-right — you have to push neighbors in *reverse* iteration order so the last-pushed (first-popped) is the leftmost neighbor. The recursive form does this implicitly via the order of the `for v in neighbors(u)` loop. The iterative form needs `for v in reversed(list(neighbors(u)))` if order matters. For the timestamp algorithm below I'll use the recursive form precisely because the order matters.

## Discovery, finish, and the parenthesis structure

Here's the move I want you to remember from this chapter. DFS can attach two timestamps to every vertex with almost no extra code, and the timestamps are the structural fingerprint the rest of the book reads. The *discovery time* `d[v]` is the value of a global counter at the moment DFS first reaches `v`; the *finish time* `f[v]` is the counter's value at the moment DFS returns from the recursive call on `v`. The counter ticks up by one on each event, so over a DFS that visits $n$ vertices, the counter goes from 1 to $2n$, with each vertex contributing two ticks: one on discovery, one on finish.

Recording the timestamps is a one-line addition to the recursive DFS at each of the two events.

```python {export=src/codex/graphs/dfs.py}
def dfs_timestamps[V: Hashable](
    source: V, neighbors: NeighborFn[V]
) -> tuple[dict[V, int], dict[V, int]]:
    """Recursive DFS recording discovery and finish times for every vertex
    reachable from source. Times are integers in [1, 2*reached], with
    each vertex contributing one discovery tick and one finish tick.
    Returns (discovery, finish).
    """
    discovery: dict[V, int] = {}
    finish: dict[V, int] = {}
    time = [0]  # boxed so the closure can increment it
    def visit(u: V) -> None:
        time[0] += 1
        discovery[u] = time[0]
        for v in neighbors(u):
            if v not in discovery:
                visit(v)
        time[0] += 1
        finish[u] = time[0]
    visit(source)
    return discovery, finish
```

The boxed `time` is the only piece of Python ergonomics worth flagging — closures over integers in Python need a wrapper because plain integer assignment inside a nested function creates a new local. A one-element list lets the inner function mutate the counter without `nonlocal`. The rest is just the recursive DFS from earlier with two extra lines per visit.

Run it on the canonical graph.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.dfs import dfs_timestamps

g = AdjacencyList[str](directed=False)
for u, v, _ in [("A", "B", 5), ("A", "C", 3), ("B", "C", 2), ("B", "D", 6),
                ("C", "D", 1), ("C", "E", 4), ("D", "E", 2), ("D", "F", 3),
                ("E", "F", 5)]:
    g.add_edge(u, v)

discovery, finish = dfs_timestamps("A", g.neighbors)
print("vertex |  d  |  f  | interval")
print("-------+-----+-----+------------")
for v in sorted(discovery, key=lambda x: discovery[x]):
    print(f"   {v}   |  {discovery[v]:>2} |  {finish[v]:>2} | [{discovery[v]}, {finish[v]}]")
```

Six vertices, twelve ticks. Read the table from top to bottom — that's the order DFS discovered the vertices. `A`'s interval is `[1, 12]`, the outermost; it brackets every other vertex's interval. `B`'s is `[2, 11]`, nested inside `A`'s; it brackets `C`, `D`, `E`, `F`. `F`'s is `[6, 7]`, the innermost — it's the deepest leaf of this DFS tree, reached last and finished first.

The bracketing is not coincidence. Write each vertex's interval as a pair of parentheses — `(` at the discovery time, `)` at the finish time — and the resulting string is a *valid parenthesization*: every opening parenthesis has a matching closing one, and the pairs nest cleanly. This is the **parenthesis theorem**: for any two vertices $u$ and $v$ in a DFS, their intervals `[d[u], f[u]]` and `[d[v], f[v]]` are either *disjoint* (one finishes before the other starts) or *one contains the other* (one's interval is entirely inside the other's). They never partially overlap.

That's the theorem in three lines, and the consequence is the algorithmic payoff. *When one interval contains another, the corresponding vertices stand in an ancestor-descendant relationship in the DFS tree.* If `[d[u], f[u]]` contains `[d[v], f[v]]`, then `u` is an ancestor of `v` in the DFS tree, and the path from `u` down to `v` is part of the DFS recursion stack at the moment `v` was discovered. Ancestor-descendant relationships, subtree membership, path depth — the timestamps encode them all, with no separate tree object needed.

Rendered explicitly, the parenthesization makes the DFS tree visible:

```python
events: list[tuple[int, str, str]] = []
for v, d in discovery.items():
    events.append((d, "open", v))
for v, f in finish.items():
    events.append((f, "close", v))
events.sort()

parens = ""
for _, kind, v in events:
    if kind == "open":
        parens += f"({v}"
    else:
        parens += f" {v})"
print(f"DFS parenthesization: {parens}")
```

`(A (B (C (D (E (F F) E) D) C) B) A)` — six pairs of parentheses, properly nested six levels deep. The graph is a mesh, but DFS from `A` saw it as a chain. That's because the canonical graph happens to be densely connected enough that DFS from `A` goes all the way to `F` without ever needing to backtrack until the deepest leaf is reached. On a sparser or differently-shaped graph the parenthesization would be wider and shallower.

The nesting structure isn't just a visualization. It's the mechanism the next algorithm runs on.

## A gray vertex is proof of a cycle

Here's the payoff. The parenthesis structure makes the next algorithm almost trivial. A directed graph has a cycle if and only if, at some point during DFS, the algorithm encounters an edge from the vertex it's currently expanding to a vertex whose interval is *still open* — i.e., a vertex that's an ancestor of the current vertex in the DFS recursion stack. That kind of edge is called a **back edge**, and back edges are precisely the witnesses of cycles in directed graphs.

The implementation uses three colors to track each vertex's state. *White* means undiscovered, *gray* means currently being explored (between discovery and finish), *black* means finished. A gray vertex is one whose interval is open; an edge from any vertex to a gray vertex is a back edge, hence a cycle. The check is a single state-machine transition at each edge.

```python {export=src/codex/graphs/dfs.py}
def has_cycle[V: Hashable](
    vertices: Iterable[V], neighbors: NeighborFn[V]
) -> bool:
    """Detect whether the directed graph defined by (vertices, neighbors)
    contains a cycle. Uses a three-color DFS: white = undiscovered,
    gray = on the recursion stack, black = finished. A gray-to-gray
    edge is a back edge, which is the witness of a cycle.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[V, int] = {v: WHITE for v in vertices}
    def visit(u: V) -> bool:
        color[u] = GRAY
        for v in neighbors(u):
            if color.get(v, WHITE) == GRAY:
                return True
            if color.get(v, WHITE) == WHITE and visit(v):
                return True
        color[u] = BLACK
        return False
    for v in list(color.keys()):
        if color[v] == WHITE:
            if visit(v):
                return True
    return False
```

Sixteen lines. The structure is recursive DFS plus a color update at each vertex's entry and exit, plus an early-return at the moment a back edge is detected. The outer `for v in list(color.keys())` is what makes the algorithm work on disconnected graphs and on graphs where the source isn't given — every vertex gets a chance to start a DFS, and any DFS that finds a cycle short-circuits the whole computation.

For an *undirected* graph the algorithm is subtly different: the edge from any non-source vertex back to its DFS-tree parent looks like a back edge but isn't a real cycle, just the edge you came in on. Detecting undirected cycles by DFS requires passing the parent vertex into the recursion and treating only non-parent gray-edges as back edges. I'll skip the undirected variant here — chapter 14's union-find solves the undirected cycle problem directly, and chapter 36's MST algorithms lean on union-find for the same reason.

Here's the directed-cycle check on two graphs: a DAG (which should report no cycle) and a graph with one obvious cycle.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.dfs import has_cycle

# A small DAG: 1 -> 2, 1 -> 3, 2 -> 4, 3 -> 4
dag = AdjacencyList[int](directed=True)
for u, v in [(1, 2), (1, 3), (2, 4), (3, 4)]:
    dag.add_edge(u, v)
print(f"DAG has cycle? {has_cycle(dag.vertices(), dag.neighbors)}")

# A graph with a 3-cycle: 1 -> 2 -> 3 -> 1, plus 4 -> 1 (no cycle through 4)
cyclic = AdjacencyList[int](directed=True)
for u, v in [(1, 2), (2, 3), (3, 1), (4, 1)]:
    cyclic.add_edge(u, v)
print(f"graph with 3-cycle has cycle? {has_cycle(cyclic.vertices(), cyclic.neighbors)}")
```

DAG: no cycle. Cyclic graph: cycle detected. The algorithm's worst case is the same $\Theta(n + m)$ as plain DFS — at most one DFS traversal of the whole graph, with one constant-time check per edge — and the early return on the first back edge means cyclic graphs are typically detected much faster than the worst case.

The cycle/DAG distinction is what chapter 37's topological sort runs on. A directed graph admits a linear ordering of its vertices respecting all edges (every edge $u \to v$ has $u$ earlier than $v$ in the ordering) *if and only if* the graph has no cycle — i.e., is a DAG. Once DFS confirms the graph is a DAG, the *reverse* of the finish-time ordering is a valid topological sort. The whole topological-sort algorithm is `has_cycle`'s framework plus "append `u` to the result list at the moment it turns black."

## Edge classification, briefly

A complete DFS on a directed graph classifies every edge into one of four types according to the colors of its endpoints at the moment the edge is examined:

- **Tree edge**: $u$ is gray, $v$ is white. The edge is the one DFS follows to discover $v$; it's part of the DFS tree.
- **Back edge**: $u$ is gray, $v$ is gray. The edge points to an ancestor in the DFS tree. Back edges are cycle witnesses.
- **Forward edge**: $u$ is gray, $v$ is black, *and* $d[u] < d[v]$. The edge points to a proper descendant via a non-tree edge.
- **Cross edge**: $u$ is gray, $v$ is black, *and* $d[u] > d[v]$. The edge points to a vertex in an unrelated, already-finished subtree.

For undirected graphs the classification collapses: every non-tree edge is a back edge, because forward and cross edges can't exist in a graph with no edge directions. That's also why undirected cycle detection has a different shape — for an undirected graph, a back edge to the immediate parent is *not* a real cycle, just the edge you came in on.

The classification is rarely needed as an end product, but it's the vocabulary other algorithms use. Strongly connected components (chapter 37) read tree-edge and back-edge structure via a per-vertex integer called the *low-link* — the earliest discovery time reachable from a vertex's subtree. Articulation points (the cut vertices whose removal disconnects the graph) are characterized by their relationship to back edges in the DFS tree. Bridges (the cut edges whose removal disconnects the graph) similarly. All of these are DFS plus one extra pass to compute one extra integer per vertex; the classification names the integers they care about.

## One DFS per island

The connected-components sweep is the same algorithm as chapter 32's BFS variant, with DFS as the inner traversal. Pick an unvisited vertex, DFS from it to find its whole component, mark the component as visited, repeat. Total work is $\Theta(n + m)$ for the same reason BFS's sweep is $\Theta(n + m)$: every vertex and edge gets touched exactly once across the whole sweep.

```python {export=src/codex/graphs/dfs.py}
def connected_components[V: Hashable](
    vertices: Iterable[V], neighbors: NeighborFn[V]
) -> list[set[V]]:
    """Sweep DFS over the vertex set. Return a list of components, each
    as the set of vertices reachable from one starting vertex via the
    undirected closure of neighbors. Same contract as the BFS sweep in
    chapter 32; this version uses iterative DFS to avoid recursion-limit
    issues on long chains.
    """
    seen: set[V] = set()
    components: list[set[V]] = []
    for start in vertices:
        if start in seen:
            continue
        component: set[V] = {start}
        stack: ArrayStack[V] = ArrayStack()
        stack.push(start)
        while stack:
            u = stack.pop()
            for v in neighbors(u):
                if v not in component:
                    component.add(v)
                    stack.push(v)
        seen |= component
        components.append(component)
    return components
```

Identical structure to the BFS sweep in chapter 32, with `ArrayStack` in place of `LinkedQueue` and `stack.push`/`stack.pop` in place of `queue.enqueue`/`queue.dequeue`. The output is the same list of component sets; only the within-component visit order changes. For component enumeration the distinction is invisible: both algorithms produce the same component sets.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.dfs import connected_components

g = AdjacencyList[int](directed=False)
for u, v in [(1, 2), (2, 3), (3, 4), (5, 6)]:
    g.add_edge(u, v)
g.add_vertex(7)

components = connected_components(g.vertices(), g.neighbors)
print(f"number of components: {len(components)}")
for i, comp in enumerate(sorted(components, key=lambda c: min(c))):
    print(f"   component {i + 1}: {sorted(comp)}")
```

Three components, same as the BFS sweep produced. Pick whichever sweep you prefer; for component enumeration alone they're interchangeable.

## The three questions, applied

### Is it correct?

The correctness of recursive DFS is one invariant: **at the moment `visit(u)` is called, `u` has been added to the `seen` set and every previously-seen vertex either has had `visit` called on it already or is on the call stack.** The invariant holds at the first call (only `source` is seen, nothing is on the stack yet) and is preserved by each recursive call (when `visit(v)` is called from inside `visit(u)`, `v` was just added to `seen` and `u` is on the stack as an ancestor). The recursion terminates because each call adds at least one vertex to `seen`, the graph is finite, and the invariant prevents the same vertex from being visited twice.

For `dfs_timestamps`, the parenthesis theorem is the correctness claim. Two vertices' intervals are properly nested or disjoint because at any moment, only the vertices currently on the recursion stack have open intervals. When `visit(v)` is called from inside `visit(u)`, `u`'s interval opens before `v`'s and closes after `v`'s does — `v`'s recursive call must return before `u`'s does, by the structure of nested function calls. So `[d[v], f[v]] \subseteq [d[u], f[u]]`. For two vertices that aren't on the same root-to-leaf path of the DFS tree, one's interval closes before the other's opens — they were discovered in different subtrees and the recursion left one before entering the other.

For `has_cycle`, correctness follows from "a gray vertex is one whose interval is open." If DFS encounters an edge from $u$ to a gray $v$, then $v$ is an ancestor of $u$ in the DFS recursion — the path from $v$ down to $u$ via tree edges, plus the back edge from $u$ to $v$, forms a cycle. Conversely, if the graph has a cycle, then on the first vertex of the cycle that DFS reaches, the recursion will eventually find an edge into another vertex of the cycle while that vertex is still gray. The three-color machine is the smallest representation of the gray/black distinction that lets the algorithm short-circuit on detection.

### How efficient is it?

DFS runs in $\Theta(n + m)$ time and $\Theta(n)$ extra space on an adjacency-list graph. Each vertex is added to `seen` (or `discovery`, or the gray set) at most once and the addition is $O(1)$ amortized. Each edge is examined at most once per endpoint — twice total for undirected graphs, once for directed — and the examination is $O(1)$. The two pieces add to $\Theta(n + m)$. Space is dominated by either the `seen` set ($\Theta(n)$) or the recursion stack ($\Theta(n)$ in the worst case where the DFS tree is a chain); both are $\Theta(n)$.

The iterative form has the same time and space bounds, with the recursion-stack space moved to an explicit `ArrayStack` whose memory is on the heap rather than on the C call stack. For deep DFS trees this matters in practice — the iterative form can handle graphs that crash the recursive form — but the asymptotics are identical.

The recursive form's per-vertex constant factor is smaller (no stack object, no explicit push/pop) but is dominated by the call-frame overhead Python imposes on every function call. For dense graphs traversed entirely in cache, the iterative form is often a constant factor *faster* than the recursive form because the explicit stack avoids the Python interpreter's call-frame machinery. The two forms are asymptotically equivalent and which one is fastest in practice depends on the workload.

### Is it optimal?

For visiting every vertex reachable from a source, $\Theta(n + m)$ is the lower bound — every reachable vertex has to be visited, every edge incident to a reachable vertex has to be examined to be sure the algorithm hasn't missed anything. DFS hits the bound, BFS hits the bound, both are worst-case optimal for the reachability problem.

For *cycle detection* in directed graphs, $\Theta(n + m)$ is the lower bound too: any algorithm must examine every edge at least once to be sure no cycle exists. The three-color DFS hits this bound. There is no faster way to detect cycles in the comparison model; the only improvement available is the constant factor that comes from short-circuiting on the first back edge.

For the *timestamping* output, recording $2n$ events takes $\Theta(n)$ time, plus the $\Theta(n + m)$ DFS traversal. Total $\Theta(n + m)$. Optimal in the same sense.

The deeper "optimality" question for DFS is about *which* DFS — the recursive form, the iterative form, a hybrid? — and the answer depends on the workload. For a fixed graph the algorithms agree on the reachable set and on the timestamps (given the same neighbor iteration order), but they differ in cache behavior, stack overhead, and recursion-limit safety. Production graph libraries usually pick the iterative form for robustness and pay the small constant-factor cost.

## What this chapter teaches

**First, the choice of container determines what the algorithm computes.** The five-line skeleton from chapter 32 — visit, mark, expand, repeat — is the same in BFS and DFS. The container in the middle is the entire difference. A queue gives FIFO, which gives distance order, which gives shortest paths. A stack gives LIFO, which gives the DFS tree, which gives discovery and finish times, which give cycle detection and topological order and articulation points. Their only difference is the data structure at the center: queue or stack. Everything else follows from that choice.

**Second, DFS exposes structure the graph didn't appear to have.** Walk the canonical graph from `A` and you visit six vertices. Walk it with timestamps and you get a parenthesization — a *tree* structure imposed on a graph that's a mesh. The DFS tree is not a property of the graph; it's a property of the DFS traversal, which depends on the neighbor iteration order. But the tree's structural facts — ancestor-descendant relationships, the existence of back edges that close cycles, the existence of cross edges that link unrelated subtrees — are graph-theoretic facts. DFS is how you compute them, and the parenthesization is how you express them.

A third observation, which the rest of the part will keep paying out. **Every "structural" question about a graph reduces to DFS plus one extra integer per vertex.** Cycle detection: one color per vertex. Topological sort: one finish-time per vertex (chapter 37). Strongly connected components: one *low-link* value per vertex, computed during DFS (chapter 37). Articulation points and bridges: one *discovery low* value per vertex. Each of these algorithms runs DFS, accumulates one or two integers per vertex at discovery and finish, and reads the answer off those integers — the same three moves, different integers. Chapter 37 will be one full application of the recipe; the rest of Part V will use the vocabulary developed here without re-deriving it.

## Notes and further reading

The recursive form of DFS is essentially as old as recursion itself; the timestamp formulation and the parenthesis theorem are usually attributed to Robert Tarjan's 1972 paper "Depth-First Search and Linear Graph Algorithms" (*SIAM Journal on Computing* 1(2):146–160), which introduced both as ways to make DFS a tool for structural problems rather than just a traversal. Tarjan's algorithm for strongly connected components — the subject of chapter 37 — is the headline result of that paper, but the timestamping infrastructure he developed for the SCC algorithm is what underlies the cycle-detection, articulation-point, and bridge-finding algorithms that came after.

CLRS chapter 22 covers DFS with the same three-color machine and the same parenthesis theorem; the textbook treatment is essentially Tarjan's, expanded with explicit proofs and exercises. Sedgewick and Wayne's *Algorithms* (4th ed.) §4.1 covers DFS alongside BFS and walks through cycle detection and topological sort in the same chapter. For the iterative-DFS implementation issue — Python's recursion limit and the moral equivalent in other languages — the standard reference is the discussion in the Python documentation for `sys.setrecursionlimit`, which is more honest than most about why the limit exists (C stack overflow is unrecoverable) and why iterative-DFS is the production answer.

For the algorithmic uses of DFS beyond what this chapter covers: Hopcroft and Tarjan's 1973 paper "Algorithm 447: Efficient Algorithms for Graph Manipulation" (*CACM* 16(6):372–378) collects the DFS-based linear-time algorithms for articulation points, bridges, and biconnected components. The 2-SAT solver — determining whether a 2-CNF Boolean formula is satisfiable in polynomial time — reduces to SCC on the implication graph, another DFS application. Planarity testing in linear time is Hopcroft and Tarjan's 1974 result, again DFS-based. Every question this part keeps asking — does this graph have a cycle? what order should these tasks run in? which vertices, if removed, disconnect the network? — reduces to DFS plus one or two integers per vertex.

In the next chapter I'll change the container one more time. Where BFS used a queue and DFS used a stack, *Dijkstra's algorithm* uses a priority queue — the heap from chapter 19 finally earns its keep. The skeleton stays the same: visit, mark, expand neighbors, repeat. The new discipline at the container makes the algorithm extract vertices in order of *weighted distance from the source* instead of order of discovery or order of hop count, and the result is single-source shortest paths in graphs whose edges carry non-negative real weights.
