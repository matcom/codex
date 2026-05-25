# Asymptotic Notation and Analysis

When you read an algorithm and ask "is this fast?", you're really asking *how does its cost scale with the input?* The exact number of operations on your laptop on this Tuesday is a number that depends on the compiler, the CPU, the cache, the temperature of the room. The *rate of growth* — how the cost changes when the input doubles, or grows tenfold, or grows to a million — is an intrinsic property of the algorithm. Asymptotic notation is the language for talking about that intrinsic property without getting distracted by the constants the implementation drags along.

This appendix collects the notation and the standard hierarchy in one place. The chapters use Big-O, Big-$\Omega$, and Big-$\Theta$ from the very first one (chapter 1), and they assume you can read all three. If you can, you can skim this appendix for reference. If you can't, this is the place to slow down.

## What the notation is hiding

Asymptotic notation deliberately throws away two kinds of information: *constant factors* and *lower-order terms*. An algorithm that runs in $3n^2 + 5n + 100$ steps is called $\Theta(n^2)$, even though for $n = 5$ the linear term might actually dominate. The bet is that for large enough $n$, the highest-order term swamps everything else, and the constant in front of it is something you can attack with engineering (better data layout, fewer cache misses, SIMD) while the *order* of growth is something you can only attack with a different algorithm.

This bet is right most of the time and wrong sometimes. It's wrong when the inputs are *always* small (a sort over 8 items, where insertion sort beats quicksort by a wide margin because the constant matters more than the order). It's wrong when the hidden constants are *astronomical* (Strassen's matrix-multiply algorithm is asymptotically faster than naive, but its hidden constant doesn't pay off until matrices are quite large). When you see me writing about practical performance in a chapter, I'm usually talking about constants the asymptotic notation hides; when you see me writing about scaling, I'm talking about what the asymptotic notation reveals.

## The Big-O family

Let $f(n)$ and $g(n)$ be functions from natural numbers to non-negative reals. The five families of notation describe different relationships between them.

### Big-$O$ — upper bound

$$f(n) = O(g(n)) \iff \exists c > 0,\ n_0 \geq 0\ \text{s.t.}\ 0 \leq f(n) \leq c \cdot g(n)\ \text{for all}\ n \geq n_0$$

In words: past some threshold $n_0$, the function $f$ is bounded above by some constant multiple of $g$. This is the most commonly written notation, but it's also the most overloaded — when someone says "binary search is $O(\log n)$", they often *mean* $\Theta(\log n)$ (it's also a lower bound), but using $O$ has become idiomatic. Big-$O$ is a *promise about the worst behavior*; it doesn't say $f$ ever achieves that worst behavior.

### Big-$\Omega$ — lower bound

$$f(n) = \Omega(g(n)) \iff \exists c > 0,\ n_0 \geq 0\ \text{s.t.}\ 0 \leq c \cdot g(n) \leq f(n)\ \text{for all}\ n \geq n_0$$

The mirror of Big-$O$. Past some threshold, the function $f$ is bounded *below* by a constant multiple of $g$. This is what you use when you want to argue that an algorithm *must* take at least so much time — for instance, comparison-based sorting is $\Omega(n \log n)$ regardless of how clever you are about it (chapter 7 of Part I closes on exactly this kind of argument).

### Big-$\Theta$ — tight bound

$$f(n) = \Theta(g(n)) \iff f(n) = O(g(n))\ \text{and}\ f(n) = \Omega(g(n))$$

When both bounds match, the algorithm grows *exactly* like $g$ (up to constants). This is the most informative notation and the one I use when I have a tight bound. "Binary search is $\Theta(\log n)$" tells you both that no instance ever takes more than $c \log n$ steps *and* that for sufficiently many inputs it takes at least $c' \log n$ steps. If you can prove $\Theta$, prefer it to $O$ — you're giving strictly more information.

### Little-$o$ — strict upper bound

$$f(n) = o(g(n)) \iff \lim_{n \to \infty} \frac{f(n)}{g(n)} = 0$$

$f$ grows *strictly slower* than $g$. Not just bounded by — *eventually negligible compared to*. $\log n = o(n)$. $n = o(n^2)$. $n^{100} = o(2^n)$. The little-$o$ notation is what you use to say "this part of the cost is irrelevant in the long run".

### Little-$\omega$ — strict lower bound

$$f(n) = \omega(g(n)) \iff \lim_{n \to \infty} \frac{f(n)}{g(n)} = \infty$$

$f$ grows *strictly faster* than $g$. The mirror of little-$o$. $n = \omega(\log n)$. $2^n = \omega(n^k)$ for any constant $k$.

## Worst, average, and best case

A single algorithm has *three* asymptotic stories — one per cost regime:

- **Worst case** is the maximum cost over all inputs of size $n$. This is what most analysis defaults to, because it's the conservative guarantee an algorithm provides.
- **Average case** is the expected cost over some distribution of inputs (usually uniform random). Quicksort is the canonical example: $\Theta(n^2)$ worst case, $\Theta(n \log n)$ average case.
- **Best case** is the minimum cost. It's the *least* useful of the three for engineering, but it's useful for showing that an algorithm is *fundamentally limited* (every comparison sort is $\Omega(n)$ best-case because it has to look at every element to be sure).

When a chapter says "binary search is $\Theta(\log n)$", it's giving the worst case. When it says "insertion sort is $\Theta(n)$ on nearly-sorted input", it's giving the best case under a structural assumption. I try to label the regime when there's any ambiguity.

## Amortized analysis

Some operations are *cheap most of the time and expensive occasionally*, where the expensive operations only happen because the cheap ones piled up the necessary state. Dynamic array append (chapter 8), hash table insert (chapter 12), and union-find union (chapter 14) all have this shape: most calls are constant-time, a few are linear, and a careful accounting shows the *total* cost over a sequence of $n$ calls is $O(n)$ — so the *average per call*, amortized over the sequence, is $O(1)$.

There are three standard methods for amortized analysis: the **aggregate method** (compute the total cost of a sequence of $n$ operations, then divide by $n$), the **accounting method** (assign each operation a "credit" larger than its actual cost, with the surplus paying for future expensive ops), and the **potential method** (define a potential function that captures the structure's stored work, then bound each operation's cost by its actual cost plus the change in potential). I introduce the aggregate method in chapter 8, the accounting method in chapter 12, and use the potential method implicitly in chapter 14. The mathematical machinery for all three lives in the math appendix; the conceptual entry point is in chapter 8.

The headline: *amortized $O(f(n))$ per operation* is a guarantee over a sequence, not per individual call. The worst single call may be more expensive than $f(n)$ — what's guaranteed is that the *total* over $k$ calls is $O(k \cdot f(n))$.

## Space complexity

The same notation describes memory cost. An algorithm is $O(n)$ in space if it allocates a number of words proportional to the input size. There are a few important subtleties:

- **Input space doesn't count.** The convention is to measure *additional* memory beyond what's needed to hold the input itself.
- **In-place** means $O(1)$ extra space, or sometimes $O(\log n)$ to allow for recursion stack.
- **Recursion costs space.** A recursive algorithm with depth $d$ uses $\Theta(d)$ stack space, even if the function body itself looks constant. Mergesort is $O(n \log n)$ in time and $O(n)$ in extra space — the extra space is the temporary array, not the recursion stack ($O(\log n)$).
- **Output space sometimes counts and sometimes doesn't.** If the output is required to be a new array of size $n$, that $O(n)$ is unavoidable and not usually called "extra".

I try to state both time and space complexity for every structure and algorithm in the book; the math appendix has the bookkeeping rules.

## The hierarchy of growth

Most algorithms in the book live in one of a small set of complexity classes. From fastest to slowest growth:

| Class | Name | Where it appears |
|---|---|---|
| $\Theta(1)$ | constant | array access, hash lookup (avg), stack push |
| $\Theta(\alpha(n))$ | inverse Ackermann | union-find with path compression (ch 14) |
| $\Theta(\log \log n)$ | doubly logarithmic | van Emde Boas trees, interpolation search |
| $\Theta(\log n)$ | logarithmic | binary search, balanced tree ops |
| $\Theta(\sqrt{n})$ | square root | sqrt decomposition, some range queries |
| $\Theta(n)$ | linear | sequential scan, linked list traversal |
| $\Theta(n \log n)$ | linearithmic | comparison-based sorting, FFT |
| $\Theta(n^2)$ | quadratic | naive sorting, all-pairs over $n$ items |
| $\Theta(n^3)$ | cubic | naive matrix multiply, Floyd-Warshall |
| $\Theta(n^k)$ | polynomial | the class $P$ |
| $\Theta(2^n)$ | exponential | subset enumeration, naive TSP |
| $\Theta(n!)$ | factorial | permutation enumeration |

The classes are deeply unequal. For $n = 10^6$, an $O(n)$ algorithm runs in a millisecond on modern hardware; an $O(n \log n)$ runs in 20 milliseconds; an $O(n^2)$ runs in roughly 17 minutes; an $O(n^3)$ would take 30 years. Going from $O(n^2)$ to $O(n \log n)$ is not a minor optimization — it's the difference between a usable tool and an unusable one.

The gap between $O(n^k)$ for any constant $k$ and $O(2^n)$ is the conventional boundary between *tractable* and *intractable*. The book's last part returns to this boundary; for now, treat polynomial = OK and exponential = trouble.

## The Master Theorem

Divide-and-conquer algorithms produce recurrences of the form

$$T(n) = a \cdot T(n/b) + f(n)$$

where $a \geq 1$ is the number of subproblems, $b > 1$ is the factor by which each subproblem shrinks, and $f(n)$ is the work done at the current level (the cost of splitting and combining). The Master Theorem gives a recipe for solving these without setting up an explicit recursion tree.

Let $\log_b a$ be the *critical exponent* — the order of growth at which the leaves of the recursion tree dominate.

1. **Leaf-dominated.** If $f(n) = O(n^{\log_b a - \epsilon})$ for some $\epsilon > 0$, then $T(n) = \Theta(n^{\log_b a})$. The total work is dominated by the work at the bottom of the recursion tree, where there are most subproblems.

2. **Balanced.** If $f(n) = \Theta(n^{\log_b a})$, then $T(n) = \Theta(n^{\log_b a} \log n)$. Each level of the tree does the same total work, and there are $\log_b n$ levels.

3. **Root-dominated.** If $f(n) = \Omega(n^{\log_b a + \epsilon})$ for some $\epsilon > 0$ *and* $f$ satisfies the regularity condition $a f(n/b) \leq c f(n)$ for some $c < 1$ and large $n$, then $T(n) = \Theta(f(n))$. The work at the root dominates everything below.

Worked examples in the book:

- **Mergesort** (chapter 4): $T(n) = 2T(n/2) + \Theta(n)$. Here $a = 2, b = 2$, so $\log_b a = 1$, and $f(n) = \Theta(n) = \Theta(n^1)$. Case 2 applies. $T(n) = \Theta(n \log n)$.
- **Binary search** (chapter 2): $T(n) = T(n/2) + \Theta(1)$. Here $a = 1, b = 2$, so $\log_b a = 0$, and $f(n) = \Theta(1) = \Theta(n^0)$. Case 2. $T(n) = \Theta(\log n)$.
- **Strassen's matrix multiply**: $T(n) = 7T(n/2) + \Theta(n^2)$. Here $\log_2 7 \approx 2.807$, and $f(n) = \Theta(n^2)$, which is $O(n^{2.807 - \epsilon})$. Case 1. $T(n) = \Theta(n^{\log_2 7})$.

The Master Theorem covers most divide-and-conquer recurrences you'll meet in this book. When it doesn't apply (e.g., $T(n) = T(\sqrt{n}) + 1$, or recurrences with non-polynomial $f$), the math appendix discusses the substitution and recursion-tree methods that handle them.

## Lower bounds: the model is part of the answer

When a chapter proves a lower bound — "comparison-based sorting requires $\Omega(n \log n)$ comparisons" — the lower bound is *not a fact about the problem*. It's a fact about a *computational model*. The same problem (sorting) is $\Theta(n)$ in the *counting sort* model where elements are integers in a bounded range; the lower bound only applies if your algorithm's only access to the elements is through *comparisons*.

This is one of the most important moves in algorithm analysis, and Part I's closing chapter ends on it. When you see a lower bound, ask: *in what model?* Often the path to a faster algorithm is to escape the model in which the lower bound was proved.

## Notation hygiene

A few conventions I follow that make my chapters readable:

- **Use $\Theta$ when you can.** $O$ is a weaker statement; reserve it for cases where you only have an upper bound (e.g., describing a sub-routine whose exact cost depends on its argument).
- **Don't write $O(2n)$.** Constants disappear; $2n$ and $n$ are both $O(n)$. The notation already absorbed the constant.
- **Don't write $\log_2 n$ inside $\Theta$.** All logs differ by a constant factor; $\Theta(\log n)$ and $\Theta(\log_2 n)$ and $\Theta(\ln n)$ are the same class. Constants inside a $\Theta$ are noise.
- **Don't conflate worst with typical.** "$O(n^2)$ worst case, $O(n \log n)$ expected" is a real and useful sentence; collapsing it to "$O(n^2)$" hides the structure that matters for picking an algorithm.
- **Name the variable.** $O(n)$ when there are two parameters (say $n$ items and $m$ edges) is ambiguous. Write $O(n + m)$ or $O(nm)$, not $O(n)$.

When in doubt, write the recurrence or the sum, solve it, and report the answer. The math appendix has the toolkit.
