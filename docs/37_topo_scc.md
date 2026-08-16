# Ordering vertices and finding strong components

Two structural questions about directed graphs fall out of DFS with almost no additional machinery. The first: can the vertices of a directed graph be lined up so that every edge points from earlier to later in the line? The answer is yes exactly when the graph is acyclic, and DFS produces the ordering as a side effect — the vertices in decreasing order of their finish times from chapter 33 form a valid topological order. The second: which maximal subsets of vertices can all reach each other? These are the *strongly connected components*, and Tarjan's 1972 algorithm finds all of them in one DFS pass by maintaining a single integer per vertex — the *low-link value* — that tracks the earliest-discovered ancestor still reachable from each vertex's subtree.

By the end of this chapter you will have implemented topological sort two ways (DFS finish-time order and Kahn's in-degree BFS), confirmed that both algorithms detect cycles and produce the same valid ordering on DAGs, implemented Tarjan's strongly connected components algorithm on a directed graph with three distinct components, and understood why the SCC condensation of any directed graph is always a DAG — a result that Part VI will use directly when it runs dynamic programming on directed graphs. Both topological sort algorithms and Tarjan's SCC run in $\Theta(n + m)$ time.
## A directed graph either admits a linear order or contains a cycle

A *topological ordering* of a directed graph is a linear ordering of all its vertices such that for every directed edge $(u, v)$, $u$ appears before $v$ in the ordering. Scheduling problems, build systems, package dependency resolution, and circuit evaluation all reduce to finding a topological order: each vertex is a task, each edge is a dependency, and the topological order is a valid execution sequence.

The key constraint is that topological orderings exist *if and only if* the graph is a DAG — a directed acyclic graph. If there's a directed cycle $v_1 \to v_2 \to \cdots \to v_k \to v_1$, then a topological order would need $v_1$ before $v_2$ before $\cdots$ before $v_k$ before $v_1$, which is impossible. Conversely, a DFS on a directed graph produces a back edge (an edge to a gray ancestor) if and only if the graph has a cycle. So detecting a topological order and detecting the absence of cycles are the same computation. DFS does both: the cycle check produces the topological ordering as a side effect.

## DFS writes the order in its finish times

The DFS-based topological sort is the `has_cycle` algorithm from chapter 33 with one extra line: append each vertex to a list the moment it turns black (finishes). That list, reversed, is a topological order.

The reason: if $(u, v)$ is a directed edge and DFS visits $u$ before $v$, then the recursion visits $v$'s entire subtree before returning to finish $u$, so $v$ finishes before $u$. If DFS visits $v$ before $u$, then since there's no path from $v$ to $u$ (the graph is a DAG — there's no back edge from $v$'s subtree to $u$), $u$ is discovered only after $v$'s entire subtree finishes, so again $v$ finishes before $u$. In both cases, $u$ finishes after $v$. In the reversed list, $u$ therefore appears before $v$. Every edge points from earlier to later in the reversed finish-time order.

```python {export=src/codex/graphs/topo_scc.py}
from collections.abc import Hashable, Iterable
from collections import deque
from codex.graphs.implicit import NeighborFn


def topological_sort_dfs[V: Hashable](
    vertices: Iterable[V], neighbors: NeighborFn[V]
) -> list[V]:
    """Topological sort via DFS finish times. Returns vertices in topological
    order (sources first, sinks last). Raises ValueError if the graph
    contains a directed cycle.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[V, int] = {}
    finish_order: list[V] = []

    def visit(v: V) -> None:
        color[v] = GRAY
        for w in neighbors(v):
            state = color.get(w, WHITE)
            if state == GRAY:
                raise ValueError("graph contains a cycle — not a DAG")
            if state == WHITE:
                visit(w)
        color[v] = BLACK
        finish_order.append(v)

    for v in vertices:
        if color.get(v, WHITE) == WHITE:
            visit(v)

    return list(reversed(finish_order))
```

The structure is `has_cycle` from chapter 33 with `finish_order.append(v)` added at the moment each vertex turns black. One new line. The return value reverses the list because vertices that finish last (sources, with no incoming edges) should appear first in the topological order. The three-color machine and the gray-vertex cycle check are unchanged.

Run it on a small DAG:

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.topo_scc import topological_sort_dfs

dag = AdjacencyList[str](directed=True)
for u, v in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")]:
    dag.add_edge(u, v)

order = topological_sort_dfs(dag.vertices(), dag.neighbors)
print("topological order:", " → ".join(order))

# verify: every edge should point forward
edges = list(dag.edges())
pos = {v: i for i, v in enumerate(order)}
valid = all(pos[u] < pos[v] for u, v, _ in edges)
print(f"all edges point forward? {valid}")
```

`A → B → C → D → E` or `A → C → B → D → E` depending on iteration order, but always with $A$ first and $E$ last. The verification loop checks that every edge satisfies the topological constraint. Kahn's finds the same order from the opposite direction: not finish times, but in-degree counts.

## Peel the sources one level at a time

Kahn's algorithm approaches topological sort from the opposite direction. Instead of running DFS and reading the result in reverse, it processes the graph front-to-back: find all vertices with no incoming edges (sources), add them to the output, remove them and all their outgoing edges, and repeat. The new sources after each removal are the vertices whose last incoming edge was just removed. A FIFO queue tracks the sources waiting to be processed.

The algorithm is cleaner to explain than to implement, because counting incoming edges requires either a precomputed in-degree table or iterating all edges. The implementation materializes both the in-degree dictionary and an adjacency list from the `neighbors` function, then runs the BFS:

```python {export=src/codex/graphs/topo_scc.py}
def topological_sort_kahn[V: Hashable](
    vertices: Iterable[V], neighbors: NeighborFn[V]
) -> list[V]:
    """Topological sort via Kahn's algorithm (BFS from in-degree-0 vertices).
    Returns vertices in topological order (sources first). Raises ValueError
    if the graph contains a directed cycle.
    """
    vlist = list(vertices)
    in_degree: dict[V, int] = {v: 0 for v in vlist}
    adj: dict[V, list[V]] = {v: [] for v in vlist}
    for v in vlist:
        for w in neighbors(v):
            in_degree[w] = in_degree.get(w, 0) + 1
            adj[v].append(w)
    queue: deque[V] = deque(v for v in vlist if in_degree[v] == 0)
    order: list[V] = []
    while queue:
        v = queue.popleft()
        order.append(v)
        for w in adj[v]:
            in_degree[w] -= 1
            if in_degree[w] == 0:
                queue.append(w)
    if len(order) != len(vlist):
        raise ValueError("graph contains a cycle — not a DAG")
    return order
```

The cycle detection is free: if the graph has a cycle, the vertices on the cycle never reach in-degree zero, so they're never added to the queue. At the end, `len(order) < len(vlist)` reveals the problem. Kahn's approach gives a different correctness argument than the DFS approach — instead of proving the finish-time order is topological, you prove that at each step the sources are exactly the vertices with no remaining dependencies — but both algorithms produce a valid topological order on any DAG.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.topo_scc import topological_sort_kahn

dag = AdjacencyList[str](directed=True)
for u, v in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")]:
    dag.add_edge(u, v)

order_kahn = topological_sort_kahn(dag.vertices(), dag.neighbors)
print("Kahn order:", " → ".join(order_kahn))

# cycle detection
cyclic = AdjacencyList[str](directed=True)
for u, v in [("A", "B"), ("B", "C"), ("C", "A")]:
    cyclic.add_edge(u, v)

try:
    topological_sort_kahn(cyclic.vertices(), cyclic.neighbors)
    print("no cycle detected")
except ValueError as e:
    print(f"caught: {e}")
```

Kahn's output for the DAG matches DFS's ordering (same valid topological sequence). For the cyclic graph, all three vertices remain at non-zero in-degree and the output list is shorter than the vertex count. Cycle detected.

Topological sort assumes the graph is acyclic. When vertices form mutual-reachability clusters, the right question shifts: which clusters are they?

## Vertices that can all reach each other

A *strongly connected component* of a directed graph is a maximal set of vertices $S$ such that for any two vertices $u, v \in S$, there is a directed path from $u$ to $v$ and from $v$ to $u$. Every directed graph has a unique partition into SCCs, even if some SCCs contain just one vertex. In the graph below — vertices $A$, $B$, $C$, $D$, $E$, $F$ with edges $A \to B \to C \to A$ (a 3-cycle), $C \to D \leftarrow E \to D$ (a 2-cycle), and $C \to F$ (isolated vertex) — the SCCs are $\{A, B, C\}$, $\{D, E\}$, and $\{F\}$.

SCC decomposition matters for two reasons. First, the *condensation* of a directed graph — the DAG formed by collapsing each SCC to a single node and keeping the edges between SCCs — is always a DAG. (If there were a cycle in the condensation, the corresponding SCCs would themselves form a larger SCC, contradicting the maximality of the partition.) That DAG is the input to the graph-DP algorithms in Part VI. Second, many "find if you can get from here to there" questions reduce to SCC: two vertices are in the same SCC if and only if they can reach each other; vertices in different SCCs can be reached only in topological order of the condensation. Finding those components efficiently is the question — and DFS already has everything it needs.

## Tarjan's low-link DFS finds all SCCs in one pass

Here is the move at the heart of Tarjan's algorithm. Run DFS and maintain, for each vertex $v$, a value `low[v]` defined as the minimum discovery time among all vertices reachable from $v$'s DFS subtree via *at most one back edge*. Formally:

$$\text{low}[v] = \min\!\left(\text{disc}[v],\;\min_{(v, w) \text{ is a back edge}} \text{disc}[w],\;\min_{(v, w) \text{ is a tree edge}} \text{low}[w]\right)$$

Two vertices $u$ and $v$ are in the same SCC if and only if they are on the same DFS path and there is a back edge from $v$'s subtree back to $u$ or an ancestor of $u$. The low-link value is what makes this checkable in $O(1)$: vertex $v$ is the *root* of its SCC — the first vertex of the SCC to be discovered — exactly when $\text{low}[v] = \text{disc}[v]$. No back edge from $v$'s subtree reaches further back than $v$ itself, which means $v$'s subtree (minus vertices already assigned to earlier SCCs) forms a maximal reachable cluster.

The algorithm maintains a separate stack of unassigned vertices. When $v$ is identified as an SCC root, pop the stack until $v$ is popped, and those vertices are $v$'s SCC.

```python {export=src/codex/graphs/topo_scc.py}
def tarjan_scc[V: Hashable](
    vertices: Iterable[V], neighbors: NeighborFn[V]
) -> list[list[V]]:
    """Tarjan's strongly connected components. Returns a list of SCCs, each
    as a list of vertices. The list is in reverse topological order of the
    condensation DAG (sinks first, sources last). O(n + m) time.
    """
    disc: dict[V, int] = {}
    low: dict[V, int] = {}
    on_stack: set[V] = set()
    stack: list[V] = []
    sccs: list[list[V]] = []
    timer = [0]

    def visit(v: V) -> None:
        timer[0] += 1
        disc[v] = low[v] = timer[0]
        stack.append(v)
        on_stack.add(v)
        for w in neighbors(v):
            if w not in disc:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], disc[w])
        if low[v] == disc[v]:
            scc: list[V] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    for v in vertices:
        if v not in disc:
            visit(v)
    return sccs
```

Thirty lines. The `visit` function is the recursive DFS from chapter 33's `has_cycle`, with three additions: the low-link bookkeeping (`disc[v] = low[v] = timer[0]`, the two `min` updates), the stack management (`stack.append`, `on_stack.add`), and the SCC extraction at the end of `visit` when the SCC root is detected. The `on_stack` set gives the $O(1)$ check that makes each edge processing $O(1)$ despite the set operations. The two branches at the edge-processing step are: if the neighbor hasn't been discovered yet, it's a tree edge — recurse and update `low[v]` from the child's low; if the neighbor is on the stack, it's a back edge — update `low[v]` from the neighbor's discovery time.

```python
from codex.graphs.adjacency_list import AdjacencyList
from codex.graphs.topo_scc import tarjan_scc

g = AdjacencyList[str](directed=True)
for u, v in [("A", "B"), ("B", "C"), ("C", "A"),   # 3-cycle
             ("C", "D"), ("D", "E"), ("E", "D"),     # 2-cycle
             ("C", "F")]:                            # isolated vertex
    g.add_edge(u, v)

sccs = tarjan_scc(g.vertices(), g.neighbors)
print(f"number of SCCs: {len(sccs)}")
for i, scc in enumerate(sccs):
    print(f"  SCC {i + 1}: {sorted(scc)}")
```

Three SCCs: `{A, B, C}`, `{D, E}`, `{F}`. The order in which they appear in the output is reverse topological order of the condensation: sinks are found first (the algorithm finishes exploring sinks before finishing the source SCCs), sources last.

## The condensation is always a DAG

Watch what happens when the SCC list is reversed: the SCCs appear in topological order of the condensation. `{A, B, C}` has outgoing edges to both `{D, E}` and `{F}` in the condensation, so it's a source; `{D, E}` and `{F}` are sinks. The condensation's topological order is `{A, B, C}` first, then `{D, E}` and `{F}` in either order. Reverse the SCC list from Tarjan's output and you have it.

This connection is the bridge to Part VI. Many dynamic-programming algorithms on directed graphs work by running DP in topological order on the condensation: compute the answer for each SCC, then propagate answers downstream. For example, the longest path in a DAG is computed by processing vertices in topological order and taking the best incoming path at each step. The same algorithm on a general directed graph reduces to: find SCCs with Tarjan's, collapse each SCC to a single vertex (keeping its best-case answer), then run DAG-DP on the condensation.

For this specific graph, the condensation has three vertices: $A' = \{A, B, C\}$, $D' = \{D, E\}$, $F' = \{F\}$, with edges $A' \to D'$ and $A' \to F'$. Any DP on this graph — "what's the maximum-weight path from source to sink," "which sinks are reachable from a given source," "what's the minimum cost to visit at least one vertex in each SCC" — can now run on the three-vertex DAG rather than on the original six-vertex graph with cycles.

## The three questions, applied

### Is it correct?

For DFS-based topological sort, the argument is the one sketched above: for any edge $(u, v)$, $v$ finishes before $u$ (because $v$'s subtree is either explored inside $u$'s recursive call, or $v$ is explored and finished before $u$ is even discovered). In both cases $u$ appears before $v$ in the reversed finish-time list. The gray-vertex cycle check is the same as `has_cycle` from chapter 33, which is correct for the same reason: a gray vertex is one whose recursive call is on the stack, and a gray-to-gray edge is a back edge, which witnesses a cycle.

For Kahn's algorithm, correctness follows from the invariant that every vertex added to the output has all of its predecessors already in the output. When $v$ is dequeued, its in-degree is zero — all its predecessors have already been dequeued and removed. If the graph has no cycle, every vertex eventually reaches in-degree zero and is added. If there's a cycle, the vertices on the cycle keep each other at non-zero in-degree permanently.

For Tarjan's SCC, the correctness argument has two parts. First, the SCC root identification: vertex $v$ with $\text{low}[v] = \text{disc}[v]$ is the first vertex of its SCC to be discovered, and the back edges from its subtree don't reach further back than $v$. This means no vertex above $v$ on the DFS stack is in $v$'s SCC (they were discovered earlier and any path from $v$ can't complete a cycle back to them). Second, the stack pop is safe: all vertices between $v$ and the top of the stack were discovered after $v$ and can reach $v$ via a path through the DFS tree, so they're in the same SCC.

### How efficient is it?

All three algorithms run in $\Theta(n + m)$ time on an adjacency-list graph. DFS-based topological sort is DFS with a constant-time append per vertex — same cost as DFS. Kahn's algorithm computes in-degrees in $\Theta(n + m)$ (iterate all edges), initializes the queue in $\Theta(n)$, and processes each vertex and each edge exactly once in the BFS loop — $\Theta(n + m)$ total. Tarjan's SCC is DFS with constant-time stack operations per vertex and per edge — $O(1)$ amortized for the `on_stack` set (hash set), $O(1)$ for the stack push/pop, $O(1)$ for the low-link min. Every vertex and edge is visited exactly once, giving $\Theta(n + m)$.

Space is $\Theta(n)$ for all three: the `color`/`disc`/`low` dictionaries, the stacks and queues, and the output list are all at most $O(n)$ simultaneously. The `adj` dictionary in Kahn's adds $O(m)$ space but that's dominated by the input graph itself.

### Is it optimal?

For topological sorting, $\Theta(n + m)$ is optimal: any algorithm must examine every vertex and every edge to be sure no ordering constraint is missed. Both DFS-based sort and Kahn's algorithm match this lower bound.

For strongly connected components, $\Theta(n + m)$ is similarly optimal — any algorithm must examine every edge at least once to determine whether it's a cross-component or intra-component edge. Tarjan's algorithm is optimal in this sense. The alternative SCC algorithm (Kosaraju's, which runs two DFS passes and requires the reversed graph) has the same asymptotic cost; Tarjan's advantage is that it requires only one DFS pass and no explicit graph reversal.

## What this chapter teaches

**DFS finish times encode a topological order.** The observation that reversing DFS finish times gives a topological sort is the deepest payoff of the finish-time vocabulary from chapter 33. A finish time is a certificate that everything reachable from a vertex has been fully explored. Reversing by finish time guarantees that sources (no incoming edges) finish last and appear first in the output. The same vocabulary supports Tarjan's SCC in this chapter and cycle-detection in both algorithms.

**Kahn's algorithm makes cycle detection visible without DFS.** The in-degree BFS approach produces the same topological order as the DFS approach but expresses the algorithm as a queue drain rather than a recursion. This matters for practical implementation: Kahn's has no recursion-depth concern, is easier to parallelize (vertices at the same in-degree level can be processed concurrently), and makes the cycle-detection output explicit (the unprocessed vertices are exactly those on cycles). For build systems and dependency resolvers, Kahn's is typically the right choice; for algorithms that also need DFS timestamps for other purposes (like Tarjan's SCC), the DFS approach comes for free.

**Tarjan's SCC is DFS with one bookkeeping integer per vertex.** The low-link value adds five lines to the DFS from chapter 33 and computes the entire SCC decomposition in a single pass. Every structural graph question reduces to DFS plus one or two integers per vertex, recorded at discovery and finish. Cycle detection used a color (three-valued integer). Topological sort added a finish list. SCC adds a low-link value and a stack. None of these are separate algorithms in the sense of requiring different traversal strategies; they are all DFS, varying only in what they measure as they go.

## Notes and further reading

Topological sort via DFS finish times is essentially Tarjan's 1972 result, extracted from the SCC paper. The observation that reversed finish times form a topological order is stated explicitly in CLRS chapter 22.4. Kahn's algorithm appeared in Kahn's 1962 paper "Topological Sorting of Large Networks" (*CACM* 5(11):558–562) and predates the DFS-based approach; Kahn was solving a build-system-like problem for a large software project.

Robert Tarjan published the SCC algorithm in "Depth-First Search and Linear Graph Algorithms" (*SIAM Journal on Computing* 1(2):146–160, 1972). The paper introduced both the timestamping infrastructure (discovery times, finish times, the parenthesis theorem) and the SCC algorithm as its main application — Tarjan's primary goal was to show that DFS could answer structural questions in linear time. The low-link value as defined in this chapter is a slight simplification of Tarjan's original formulation; the behavior is equivalent for the SCC problem.

Kosaraju's SCC algorithm, which runs two DFS passes — one on the original graph to record finish times, one on the reversed graph in decreasing finish-time order to collect SCCs — was independently discovered by Kosaraju in 1978 and Sharir in 1981. CLRS chapter 22.5 presents Kosaraju's algorithm alongside Tarjan's. Both are $\Theta(n + m)$; Tarjan's requires one pass and no graph reversal, while Kosaraju's is easier to prove correct.

For the applications of SCC: 2-SAT (determining whether a 2-CNF Boolean formula is satisfiable) reduces to SCC on the implication graph in $O(n + m)$ time. Program optimization (identifying strongly connected regions of a control-flow graph, which correspond to loops) uses SCC as a first step. Social network analysis uses SCC to identify "echo chambers" — maximal subsets of users that can all influence each other through the network. Sedgewick and Wayne's *Algorithms* (4th ed.) §4.2 presents the SCC algorithms with detailed application examples.

For Tarjan's broader influence: the same 1972 paper that introduced DFS timestamping and SCC also described linear-time algorithms for biconnected components (vertex-cut sets) and bridges (edge-cut sets). Hopcroft and Tarjan's follow-up work on planarity testing (1974) and dominator trees (1979) established DFS as the canonical tool for structural graph analysis. Chapter 33's observation that "every structural question reduces to DFS plus one extra integer per vertex" is a reasonable summary of the body of work Tarjan's 1972 paper inaugurated.

In the next chapter I'll add a concept to graphs that neither shortest paths nor spanning trees needed: *capacity*. Flow networks assign to each directed edge both a direction and an upper bound on how much "flow" can travel through it. The maximum-flow problem asks for the most flow that can get from a source vertex to a sink vertex without violating any capacity. The answer turns out to equal the weight of the minimum-weight cut separating the source from the sink — max-flow equals min-cut — and the proof is constructive: the augmenting-path algorithm simultaneously computes both sides of the duality.
