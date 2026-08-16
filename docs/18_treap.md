# Random priorities, balanced trees

Chapter 17 bought a worst-case $O(\log n)$ height bound with a single integer per node and a careful four-case rotation table. The price was real — every insert and delete recomputes heights up the recursion, every imbalance triggers a rotation case-split, and a single delete can fire $O(\log n)$ rotations on its way back to the root. The structure works, but you carried a fair amount of bookkeeping to make it work, and the question I want to open with is whether there's a cheaper way to buy the same guarantee.

**Two invariants at once — BST on key, max-heap on priority — and that's what randomization buys you.** One node, two ordering rules. The BST rule does what BSTs always do. The heap rule, applied to *random* priorities, is the rebalancing mechanism in disguise. The generic `Treap[K, V]` developed below maintains both invariants on every operation, and a sorted insertion of $0, 1, \ldots, 15$ — the same input that drove chapter 16's BST into a chain — produces a tree of height comparable to chapter 17's AVL.

## Determinism's price

Chapter 17's AVL tree is correct, tight, and a bit fussy. Each node carries a `height` field, every operation recomputes it on the way up, and the `_rebalance` step does a four-case split — LL, LR, RR, RL — to decide which rotation pattern restores the invariant. Insertion is one rotation in the worst case; deletion is up to $\log_2 n$ rotations because an imbalance can propagate arbitrarily high. You pay the determinism in two ways: storage (one integer per node) and code complexity (the case table). Both are small in absolute terms, but they're not zero.

The natural question is whether you can drop both costs and still get $O(\log n)$ per operation. The deterministic answer says no — an adversary who controls insertion order can drive any *predictable* BST shape into a chain, just like chapter 16 demonstrated. But the deterministic question is the wrong question. If you let the structure make a *random* choice on every insertion, the adversary stops being able to predict the shape, and the worst case stops being constructible. The expected cost becomes $O(\log n)$ on every input, including the adversarially-crafted ones that broke chapter 16's BST.

A treap (the name fuses *tree* + *heap*) attaches a random priority to each node at insertion time, and maintains a max-heap order on those priorities alongside the BST order on the keys. The heap order is what keeps the tree shallow; the randomness of the priorities is what makes "shallow" hold in expectation, regardless of insertion order. No height field, no balance factor, no four-case table — just a comparison against a random number and a rotation when the heap order is violated.

## Two invariants, one node

A treap is a binary tree where each node carries a key $k$, a value, and a priority $p$. The structure obeys two ordering rules at every node:

- **BST on key.** Every key in the left subtree is strictly less than the node's key; every key in the right subtree is strictly greater. Same rule as chapter 16.
- **Max-heap on priority.** The node's priority is greater than or equal to the priorities of its two children. The same heap rule you'd see at every level of a max-heap (chapter 19 develops it as a structure in its own right).

Those two rules, taken together, determine the tree's shape *uniquely*. Given a set of $(k, p)$ pairs with distinct keys and distinct priorities, there is exactly one binary tree that satisfies both rules. You can prove it by induction on set size: the root has to be the node with the largest priority (forced by the heap rule), the left subtree is recursively the treap of the keys less than the root, and the right subtree is recursively the treap of the keys greater. Both subtrees are uniquely determined by recursion. So the (key, priority) multiset *is* the tree, up to the shape that the rules force.

That uniqueness has a second consequence. **A treap is the unique BST you'd build by inserting keys in priority order, highest priority first.** If you took the same set of nodes and inserted them into a plain BST in *decreasing* priority order, the root would be the highest-priority node, then each subsequent insertion would attach to the appropriate side, and you'd produce exactly the treap. So the treap's shape *is* the shape of a BST built from a particular insertion order — namely, the order priorities induce on the keys.

When priorities are uniform-random and independent, that insertion order is a uniformly random permutation of the keys. And chapter 16 already told you what happens then: Knuth's result is that a BST built from a uniformly-random insertion sequence has expected height $\approx 1.39 \log_2 n$. So a treap with random priorities has expected height $\approx 1.39 \log_2 n$, with high probability. The randomness of the priorities is the randomness of the implied insertion order, and the implied insertion order is random regardless of what order keys *actually* arrived in.

That is: the adversary can pick any sequence of keys, but you pick the priorities, and the priorities are what determines the shape. Adversary loses.

## Insert by rotate-up, delete by rotate-down

Two rotation primitives, same shape as chapter 17's but stripped of the height-update bookkeeping (a treap has no height field).

```python {export=src/codex/trees/treap.py}
import random
from typing import Iterator


class TreapNode[K, V]:
    def __init__(
        self,
        key: K,
        value: V,
        priority: float,
        left: "TreapNode[K, V] | None" = None,
        right: "TreapNode[K, V] | None" = None,
    ) -> None:
        self.key = key
        self.value = value
        self.priority = priority
        self.left = left
        self.right = right
```

Each node carries a key, a value, a priority (a float drawn from $[0, 1)$ at insertion time), and the two child pointers. I'll use `random.Random` instances inside the wrapper class so that a caller can pass a seeded RNG and get reproducible trees — important for the demos below and for any debugging session where you'd want a specific tree to keep showing up.

Right rotation is the same primitive as chapter 17, with the height-update lines deleted. Three pointer writes; return the new subtree root.

```python {export=src/codex/trees/treap.py}
def _rotate_right[K, V](node: TreapNode[K, V]) -> TreapNode[K, V]:
    assert node.left is not None
    new_root = node.left
    node.left = new_root.right
    new_root.right = node
    return new_root


def _rotate_left[K, V](node: TreapNode[K, V]) -> TreapNode[K, V]:
    assert node.right is not None
    new_root = node.right
    node.right = new_root.left
    new_root.left = node
    return new_root
```

Same in-order argument as chapter 17 — the keys keep their in-order positions, so the BST invariant survives every rotation. What changes between the two chapters is the *trigger*: AVL rotates when a balance factor goes out of range; a treap rotates when a child's priority exceeds the parent's.

Now the wrapper. I'll keep the same `_root` / `_size` shape as `BST` and `AVL`, plus a private `_rng` field so reproducible demos are cheap to write.

```python {export=src/codex/trees/treap.py}
class Treap[K, V]:
    def __init__(self, rng: random.Random | None = None) -> None:
        self._root: TreapNode[K, V] | None = None
        self._size: int = 0
        self._rng: random.Random = rng if rng is not None else random.Random()

    def __len__(self) -> int:
        return self._size

    def height(self) -> int:
        def _h(node: TreapNode[K, V] | None) -> int:
            if node is None:
                return -1
            return 1 + max(_h(node.left), _h(node.right))

        return _h(self._root)
```

No cached height — I recompute it on demand, the same way chapter 16's `BST.height` did. A treap doesn't need height during operations (no balance factor to evaluate), so paying $\Theta(n)$ for a height query is the right trade. The single-key operations stay cheap.

Insertion is the BST descent plus a rotate-up on the way back. The new node enters as a leaf at the position the BST rule dictates, with a fresh random priority. On the recursive return, each ancestor checks whether the child it just recursed into now has a *higher* priority than itself; if so, the heap rule is violated and a rotation pulls the child up one level. The rotation preserves the BST rule (proved above) and reduces the priority gap by one node, so a chain of rotations bubbles the new node up until it lands at a position where the heap rule holds.

```python {export=src/codex/trees/treap.py}
    def insert(self, key: K, value: V) -> None:
        priority = self._rng.random()
        self._root = self._insert(self._root, key, value, priority)

    def _insert(
        self,
        node: TreapNode[K, V] | None,
        key: K,
        value: V,
        priority: float,
    ) -> TreapNode[K, V]:
        if node is None:
            self._size += 1
            return TreapNode(key, value, priority)
        if key < node.key:
            node.left = self._insert(node.left, key, value, priority)
            if node.left.priority > node.priority:
                return _rotate_right(node)
        elif key > node.key:
            node.right = self._insert(node.right, key, value, priority)
            if node.right.priority > node.priority:
                return _rotate_left(node)
        else:
            node.value = value  # overwrite, no priority change, no rotation
        return node
```

Three branches per node, just like AVL. The two recursive branches descend BST-style, then on the way back up check whether the child's priority now exceeds the parent's — if so, rotate to bring it up. A right rotation pulls the *left* child up; a left rotation pulls the *right* child up. The duplicate-key case overwrites the value and returns without touching priorities; the heap rule is unaffected.

Reading the function from the bottom up: every recursive return passes through at most one rotation, and rotations only happen on the path the recursion just traversed. That path is the BST insertion path, length $O(\log n)$ in expectation, so insertion fires $O(\log n)$ rotations in the worst-case for *that single insert* — though the expected number of rotations per insert is $O(1)$ once you account for where in the tree the new node lands.

Search and `__contains__` are unchanged from chapter 16. The heap rule plays no role in lookup — only the BST rule matters when you're descending to find a key.

```python {export=src/codex/trees/treap.py}
    def search(self, key: K) -> V | None:
        node = self._root
        while node is not None:
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return node.value
        return None

    def __contains__(self, key: K) -> bool:
        return self.search(key) is not None

    def in_order(self) -> Iterator[tuple[K, V]]:
        def _walk(node: TreapNode[K, V] | None) -> Iterator[tuple[K, V]]:
            if node is None:
                return
            yield from _walk(node.left)
            yield (node.key, node.value)
            yield from _walk(node.right)

        yield from _walk(self._root)
```

Iterative search, generator in-order — same idioms as chapters 16 and 17. The treap's distinguishing structure is invisible to a read-only client.

Deletion inverts insertion. Instead of bubbling a new node *up* into a heap-legal position, I'll bubble the target node *down* into a leaf position and snip it off. The trick at each step: rotate the target past whichever of its children has the higher priority. That preserves the heap rule for the children — they each remain greater than or equal to their *own* children — and pushes the target one level deeper. Repeat until the target has no children left, then unlink it.

```python {export=src/codex/trees/treap.py}
    def delete(self, key: K) -> None:
        self._root = self._delete(self._root, key)

    def _delete(
        self,
        node: TreapNode[K, V] | None,
        key: K,
    ) -> TreapNode[K, V] | None:
        if node is None:
            return None  # key not present — silent no-op
        if key < node.key:
            node.left = self._delete(node.left, key)
            return node
        if key > node.key:
            node.right = self._delete(node.right, key)
            return node
        return self._rotate_down_and_remove(node)
```

BST descent until I find the match site, same as chapter 16. The match site is where the rotate-down work happens, and I've factored it into its own helper so the dispatch reads cleanly.

The rotate-down helper handles the three children-count cases. If the target has no children, just return `None` (the parent will splice the gap closed). If it has only one child, return that child (same single-child splice as chapter 16's BST deletion). If both children exist, rotate the target one level deeper — past whichever child has the higher priority, to preserve the heap rule at that subtree's root — and recurse on the rotated tree to keep pushing down.

```python {export=src/codex/trees/treap.py}
    def _rotate_down_and_remove(
        self,
        node: TreapNode[K, V],
    ) -> TreapNode[K, V] | None:
        if node.left is None and node.right is None:
            self._size -= 1
            return None
        if node.left is None:
            self._size -= 1
            return node.right
        if node.right is None:
            self._size -= 1
            return node.left
        # both children — rotate target past the higher-priority child
        if node.left.priority > node.right.priority:
            new_root = _rotate_right(node)
            new_root.right = self._rotate_down_and_remove(node)
            return new_root
        new_root = _rotate_left(node)
        new_root.left = self._rotate_down_and_remove(node)
        return new_root
```

Each rotation pushes the target node one level deeper. The recursion on `node` (now a child of `new_root`) keeps pushing until one of the leaf or one-child cases fires and the node is removed. The heap rule at the rotated-up child is preserved because that child *was* the higher-priority one, so it satisfies the heap rule with respect to the sibling that didn't rotate, and the recursion fixes the heap rule beneath the rotation.

Inserting `[5, 3, 8, 1, 9, 4, 7]` with a seeded RNG produces a deterministic tree — same priorities every time.

```python
import random
from codex.trees.treap import Treap

rng = random.Random(42)
tree: Treap[int, str] = Treap(rng=rng)
for k in [5, 3, 8, 1, 9, 4, 7]:
    tree.insert(k, f"v{k}")

# In-order traversal — the BST rule says this must be sorted
print(f"in-order:   {[k for k, _ in tree.in_order()]}")
# [1, 3, 4, 5, 7, 8, 9] — sorted, as the BST invariant promises

# Walk the tree showing parent + L/R children — priorities decrease
# as you descend (heap rule), keys partition BST-style (BST rule)
def _walk(node, indent=0):
    if node is None:
        return
    l = node.left.key if node.left is not None else "·"
    r = node.right.key if node.right is not None else "·"
    print(f"{'  ' * indent}key={node.key}, prio={node.priority:.3f}, "
          f"L={l}, R={r}")
    _walk(node.left, indent + 1)
    _walk(node.right, indent + 1)

_walk(tree._root)
# Root key=7, prio=0.892 — the highest priority in the tree, as the heap
# rule demands. The keys split BST-style: 4 and friends on the left, 9
# and friends on the right.
print(f"height:     {tree.height()}")
```

The in-order is sorted (BST rule) and the priorities decrease as you walk down from the root (heap rule). Both invariants visible at once on the same seven nodes.

The sorted-insertion experiment, redone with the treap. Same sixteen keys, $0$ through $15$, inserted in their natural order. The plain BST gave you height 15; the AVL gave you height 4. I expect the treap to land somewhere close to the AVL — random priorities should keep the height around $2 \log_2 16 = 8$ in expectation, often lower.

```python
sorted_treap: Treap[int, int] = Treap(rng=random.Random(42))
for k in range(16):
    sorted_treap.insert(k, k)

print(f"sorted insertion of 0..15: height = {sorted_treap.height()}")
# 5 — close to AVL's 4 and dramatically better than the BST's 15
print(f"in-order: {[k for k, _ in sorted_treap.in_order()]}")
# [0, 1, ..., 15] — sorted, same as both the BST and the AVL produced
```

Height 5 on the same sorted input that drives a plain BST to height 15 and an AVL to height 4. The treap landed one above the AVL — not as tight as AVL's deterministic bound, but within a small constant of it, with no balance-factor bookkeeping at all. That gap is the cost of buying balance with randomness rather than with rotations: a slightly larger constant in front of the $\log n$, in exchange for a much simpler implementation.

Scaling up: five different RNG seeds, each inserting `range(1000)` into a fresh treap, height read off at the end. Expected $\approx 2 \log_2 1000 \approx 20$, with some variance per seed.

```python
heights: list[int] = []
for seed in [1, 2, 3, 4, 5]:
    t: Treap[int, int] = Treap(rng=random.Random(seed))
    for k in range(1000):
        t.insert(k, k)
    heights.append(t.height())

print(f"heights across 5 seeds: {heights}")
# [20, 21, 20, 22, 25] — cluster around 2·log_2(1000) ≈ 20.
# A plain BST on the same sorted input would have given you height 999.
print(f"mean: {sum(heights) / len(heights):.1f}, "
      f"max: {max(heights)}, min: {min(heights)}")
# mean: 21.6, max: 25, min: 20
```

Every treap landed at a height between 20 and 25 — roughly a factor of two off the perfectly-balanced ideal of $\log_2 1000 \approx 10$, on the same sorted input that drives a plain BST into a chain. The plain BST of chapter 16 would have given you height 999 on the exact same insertion sequence. That's the adversary defeated by randomness.

## Expected height is O(log n)

The height bound holds in expectation. The full proof from Seidel and Aragon's 1996 paper is several pages of careful probability; the intuition that drives it sketches as follows, and the paper carries the details.

The argument reduces to a question about *depths*. Pick any node $v$ in the treap — what's the expected depth of $v$? If I can show that any single node has expected depth $O(\log n)$, the expected height (which is the maximum depth over all nodes) is also $O(\log n)$ by a union-bound argument I'll wave at rather than execute.

Fix two nodes $u$ and $v$ in the treap, with $v$ the one you're trying to bound. Sort all nodes by key, and let $|u - v|$ denote the *rank gap* between them — the number of keys (inclusive of $u$ and $v$) you'd pass through walking from $u$ to $v$ in the sorted order. Seidel and Aragon's key observation: $u$ is an ancestor of $v$ in the treap if and only if $u$ has the *highest priority* among all the nodes in the rank interval between $u$ and $v$. The reason is the uniqueness theorem from earlier — the treap is the BST induced by inserting in priority order, so the first node from that interval to be "inserted" is the one whose key splits the interval at the treap, and that's the ancestor.

Now if priorities are uniform-random and independent, the probability that $u$ has the highest priority among $|u - v|$ candidates is exactly $1 / |u - v|$. So the expected number of ancestors $v$ has is the sum over all other nodes $u$ of $1 / |u - v|$. Summing over a tree of $n$ nodes (where rank gaps from $v$ go from 1 to about $n$), you get a harmonic-series sum:

$$\mathbb{E}[\text{depth of } v] = \sum_{u \ne v} \frac{1}{|u - v|} \le 2 H_n = O(\log n)$$

where $H_n = 1 + 1/2 + \ldots + 1/n \approx \ln n$. That's the per-node depth bound. The factor of 2 comes from summing the harmonic series on both sides of $v$ (nodes with smaller keys and nodes with larger keys, each contributing one tail of the harmonic).

The expected height of the whole tree is a tighter argument that needs to bound the *maximum* depth across all nodes, not just one node's depth. Seidel and Aragon show that the expected height is at most $4.31 \log_2 n$ — slightly worse than AVL's $1.44 \log_2 n$ deterministic bound, but in the same asymptotic class. And more importantly, the bound holds with high probability: the chance of seeing a treap of height much larger than $c \log n$ falls polynomially in $n$, so the tail is genuinely thin.

On a million keys, an AVL is at most about 28 nodes tall, a treap is *expected* to be at most about 90 nodes tall, and a plain BST on adversarial input can be 999,999 nodes tall. Randomization lifts you from the catastrophic case into the same asymptotic class as the deterministic structure, at the cost of a slightly larger constant.

## The bridge to Part IX

Randomization-as-balance is the first instance of a pattern that recurs across sorting, hashing, graph search, and data structures, and Part IX picks it up systematically. The same trick — *make a random choice the adversary can't predict, and the worst case becomes statistically unreachable* — drives at least four structures or algorithms you'll meet again:

- **Treaps** (this chapter). Random priorities turn the BST's input-order pathology into an expected-case bound.
- **Skip lists** (Pugh, 1990). A randomized layered linked list that competes with self-balancing BSTs at $O(\log n)$ expected per operation, with even less rotation bookkeeping than a treap.
- **Randomized quicksort.** A random pivot makes the worst-case sorted-input quadratic blow-up of chapter 4's plain quicksort statistically unreachable. Expected $O(n \log n)$ on every input, including adversarial ones.
- **Rabin-Karp fingerprinting.** A randomly-chosen hash modulus makes the adversary unable to construct strings that collide on the rolling hash, which turns a $\Theta(nm)$ worst-case substring search into $O(n + m)$ in expectation.

What unifies these is the same observation. A deterministic algorithm has a worst case the adversary can construct *if* they can predict the algorithm's behavior on each input. Randomization breaks the prediction: the adversary picks the input, but you pick the random coins, and the adversary doesn't see your coins before committing to the input. Worst-case constructibility requires both the input and the coins to align, and the probability that they do is exponentially small in the algorithm's parameters.

The treap is the first textbook example because its randomization is so *local* — one float per node, decided at insertion time — and the payoff is so direct: a structure that's nearly as good as the deterministic AVL with about half the bookkeeping.

## The three questions, applied

### Is it correct?

A treap is correct as a BST if, after any sequence of `insert` and `delete` operations, the in-order traversal of its keys is sorted. It is correct as a *treap* if, in addition, every node's priority is greater than or equal to the priorities of its children. The two invariants stack: the BST rule guarantees the right *answers* to search and the right *order* across mutations; the heap rule on random priorities guarantees the right *cost shape* in expectation.

The BST rule survives every operation by the same argument as chapter 16. Insert descends BST-style into the slot the rule dictates. Delete either splices a child up (which moves a sorted contiguous chunk into the deleted slot — same as chapter 16's one-child case) or rotates the target down to a leaf and unlinks it. Rotations preserve the BST in-order ordering (chapter 17's picture proves it), so a chain of rotations preserves it too. The heap rule is the part the algorithms have to *actively* maintain: insert bubbles up by rotation until a parent has higher priority than the new node; delete bubbles down by rotation past the higher-priority child until the target is a leaf. Both maintenance steps terminate because each rotation moves the offending node strictly one level (up for insert, down for delete) and the tree has finite height.

### How efficient is it?

Cost table for a treap of $n$ nodes, expectations taken over the random priorities:

| Operation | Expected time | Worst case | Extra space |
|-----------|---------------|------------|-------------|
| `insert`  | $O(\log n)$ | $O(n)$ | $O(\log n)$ — recursion stack |
| `search` / `__contains__` | $O(\log n)$ | $O(n)$ | $O(1)$ — iterative |
| `delete`  | $O(\log n)$ | $O(n)$ | $O(\log n)$ — recursion stack |
| `in_order` | $\Theta(n)$ | $\Theta(n)$ | $O(\log n)$ — generator |
| `height`  | $\Theta(n)$ | $\Theta(n)$ | $O(\log n)$ |
| `__len__` | $\Theta(1)$ | $\Theta(1)$ | $\Theta(1)$ |

That is: every single-key operation on a treap is bounded by roughly $4.3 \log_2 n$ comparisons in expectation, regardless of insertion order. For a million keys that's about 86 comparisons; for a billion, about 129. The worst case is $\Theta(n)$ — the unlucky priorities case — but the probability of seeing it falls polynomially in $n$, so it never shows up in practice. Storage per node is one float for the priority and two child pointers; no balance factor, no color bit, no parent pointer.

The expected number of rotations per insert is $O(1)$ — not $O(\log n)$. That's a stronger statement than the height bound: even though the new node may sit at depth $O(\log n)$, the number of rotations on its way up is expected constant. The argument is again Seidel and Aragon's: a new node lands at a random depth, and the number of rotations equals the number of ancestors with priority lower than it, which is geometrically distributed. Expected constant rotations per insert is part of what makes the treap competitive with AVL in practice despite the looser height bound.

### Is it optimal?

Among randomized self-balancing BSTs on the comparison-based model, **a treap is asymptotically optimal in expectation**. The information-theoretic lower bound from chapter 16 still holds: ordered insert, search, and delete each need $\Omega(\log n)$ comparisons per operation, and a treap achieves $O(\log n)$ in expectation. The constant $4.31$ in the expected height bound is worse than AVL's $1.44$ deterministic constant, but the asymptotic class is the same, and randomized algorithms pay a slightly worse constant in exchange for a simpler structure.

Skip lists (Pugh, 1990) — the other major randomized ordered-dictionary structure — achieve the same $O(\log n)$ expected bound with a different storage layout: $O(\log n)$ pointers per node on average, instead of two. In practice, skip lists are easier to implement lock-free in a concurrent setting (because they use only pointer writes, no rotations), and treaps are easier to implement sequentially (because they're a tree, not a layered list). Both are textbook randomized structures and both live in the same asymptotic class as AVL and red-black; the engineering choice between them is about implementation context, not asymptotic cost.

What a treap gives you that the deterministic structures don't is the *simplicity*. No balance factor, no color bit, no four-case rotation table — just a random float per node and a one-line rotation-up rule. That simplicity is what makes treaps a popular teaching structure and what makes them attractive for prototype implementations where bookkeeping cost matters more than peak constant-factor performance.

## Randomization is the rebalancing mechanism in disguise

The BST rule does the ordered-lookup work the BST was designed for; the heap rule applied to *random* priorities does the rebalancing work, without you ever having to compute a balance factor or dispatch a four-case rotation table. The randomness of the priorities makes the implied insertion order uniform, and a uniformly-random insertion order is the regime where chapter 16's plain BST is already expected-balanced.

Randomization is a worst-case-tamer. When an adversary can construct an input that breaks a deterministic algorithm, hiding the algorithm's choices behind random coins reduces the worst case to expected-case behavior. Treaps, skip lists, randomized quicksort, and Rabin-Karp all share this signature, and Part IX picks the pattern up systematically.

Simplicity is a real engineering currency. A treap trades a constant factor in height (4.3 vs. 1.4) for a dramatic reduction in implementation complexity — one float per node, one rotation-up rule, no balance-factor case-split. In contexts where the code has to be small, readable, or easy to modify, the simplicity wins even when a slightly worse asymptotic constant comes with it.

And the right invariant for a problem is often two invariants. A treap's shape is determined by *both* the BST rule and the heap rule taken together — neither rule alone is enough. The same dual-invariant move shows up in segment trees (chapter 21) and in many tree structures from competitive programming. Composing two simple ordering rules into something whose behavior neither rule predicts on its own is an algorithm-design move worth remembering.

Chapter 19 takes the heap rule on its own and lets it carry an entire structure. A treap uses the heap order on priorities as a balancing trick; a *heap* uses the heap order on the data itself, and the priority *is* the whole story. The same ordering rule, used for a different job.

## Notes and further reading

The treap was introduced by Cecilia Aragon and Raimund Seidel in their 1989 paper "Randomized Search Trees" at the IEEE Symposium on Foundations of Computer Science (FOCS '89), and the journal version appeared as "Randomized Search Trees" in *Algorithmica* 16(4–5):464–497, 1996 — the full expected-height analysis and the $O(1)$-expected-rotations-per-insert bound both come from that paper. Knuth's *The Art of Computer Programming*, vol. 3, §6.2.2 has the original analysis of the expected height of a random BST (the $1.39 \log_2 n$ result that the treap argument leans on), and Sedgewick and Flajolet's *An Introduction to the Analysis of Algorithms* §6 develops the same harmonic-series argument I sketched in section 4. William Pugh's 1990 paper "Skip Lists: A Probabilistic Alternative to Balanced Trees" in *Communications of the ACM* 33(6):668–676 is the canonical reference for the other major randomized ordered-dictionary structure; it's the structure I'd reach for in a lock-free concurrent setting, where treaps' rotation-based updates make synchronization harder. For the broader pattern of randomization-as-balance, Motwani and Raghavan's *Randomized Algorithms* (Cambridge, 1995) §8 is the textbook reference, and Part IX of this book picks up the same thread when randomized quicksort and Rabin-Karp fingerprinting come around.
