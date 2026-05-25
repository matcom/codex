# A Mathematical Toolkit

Algorithm analysis lives downstream of a handful of mathematical tools: summations, logarithms, recurrences, probability, and a few specialty objects like the inverse Ackermann function. Most undergraduate algorithms courses assume you've seen this material in discrete math and don't re-derive it; this book takes the same approach in the chapters, but I want to give you one place to look up the identities and the methods when an analysis in the chapter asks you to solve a sum or unroll a recurrence.

This isn't a math textbook either. It's a *toolkit* — the smallest set of facts and methods you need to follow every analysis in this book. If you've seen all of this before, you can skim it. If parts of it look unfamiliar, the chapter analyses will refer back here when they lean on a specific identity.

## Summations

Almost every cost analysis ends in a sum. The five sums below cover the vast majority of what comes up.

### Arithmetic series

$$\sum_{i=1}^{n} i = \frac{n(n+1)}{2} = \Theta(n^2)$$

The classic. Appears in any algorithm with a nested loop of the shape "for each $i$, do $i$ units of work" — selection sort, the comparison count for bubble sort, the work done by insertion sort on a reversed array.

More generally, for a sum of the first $n$ natural numbers raised to a power $k$:

$$\sum_{i=1}^{n} i^k = \Theta(n^{k+1})$$

This is the *power rule for sums* — it's the discrete analog of the integral $\int_0^n x^k\, dx = \frac{n^{k+1}}{k+1}$, and the asymptotic agrees with the integral up to constants.

### Geometric series

$$\sum_{i=0}^{n-1} r^i = \frac{r^n - 1}{r - 1}$$

for $r \neq 1$. When $r > 1$, this is $\Theta(r^n)$: the last term dominates the entire sum, up to a constant factor that depends on $r$. When $0 < r < 1$, the sum converges to $\frac{1}{1-r}$ as $n \to \infty$, so the partial sum is $\Theta(1)$ — bounded regardless of how many terms you take. This is the math behind chapter 8's amortized argument for dynamic array doubling: the cost of all resizes through size $n$ is $1 + 2 + 4 + \cdots + n = 2n - 1 = \Theta(n)$, because a geometric series with ratio $2$ and last term $n$ sums to $\Theta(n)$.

### Harmonic series

$$H_n = \sum_{i=1}^{n} \frac{1}{i} = \ln n + \gamma + O(1/n)$$

where $\gamma \approx 0.5772$ is the Euler–Mascheroni constant. The asymptotic is $\Theta(\log n)$. This sum shows up in randomized analyses (e.g., quicksort's expected comparison count), in the analysis of skip lists, and in any algorithm that does $1 + 1/2 + 1/3 + \cdots$ work — for instance, sifting up through a heap when you only pay $1/h$ at each level.

### Telescoping sums

When consecutive terms cancel, a sum collapses:

$$\sum_{i=1}^{n} (a_i - a_{i-1}) = a_n - a_0$$

This is the engine behind the potential method of amortized analysis, where you express the cost of each operation as "actual cost + (potential after) - (potential before)" and the potential changes telescope across a sequence of operations.

### Logarithm sums

$$\sum_{i=1}^{n} \log i = \log(n!) = \Theta(n \log n)$$

Useful when you have to add up the log-time work done across $n$ inserts into a balanced tree, or the heap-build cost across $n$ insertions. The $\Theta(n \log n)$ growth here is exactly the comparison lower bound for sorting (Stirling's approximation, below, makes the constant explicit).

## Logarithms

A few logarithm identities come up often enough that I'll state them once and reuse them throughout the book.

**Change of base.** $\log_b n = \frac{\log_a n}{\log_a b}$. The ratio is a constant, so $\log_a n = \Theta(\log_b n)$ — all logs are the same complexity class up to constants. That's why the chapters write $\Theta(\log n)$ without specifying the base.

**Logarithm of a product/quotient.** $\log(xy) = \log x + \log y$. $\log(x/y) = \log x - \log y$. $\log(x^k) = k \log x$.

**Inversion.** $b^{\log_b x} = x$. $\log_b(b^x) = x$. Useful when an algorithm's cost is expressed as $2^{\log_2 n}$ — that's just $n$.

**Stirling's approximation.** $\log(n!) = n \log n - n \log e + \Theta(\log n) = n \log n - \Theta(n)$. The first-order term is what makes comparison sorting $\Omega(n \log n)$ in the decision-tree model: a sorting algorithm must distinguish $n!$ permutations, requiring at least $\log_2(n!) = \Theta(n \log n)$ comparisons.

**Iterated logarithm.** $\log^*(n)$ is the number of times you have to take $\log$ before the result drops below 1. It grows *unbelievably slowly*: $\log^*(2^{65536})$ is just 5. The iterated logarithm shows up in some pointer-machine algorithms and in the analysis of the union-by-rank-only version of union-find.

## Recurrences

A recurrence is an equation that defines a function in terms of its values at smaller inputs. Every recursive algorithm has a cost recurrence. Three methods solve them.

### The substitution method

Guess the form of the solution and prove it by induction.

To solve $T(n) = 2 T(n/2) + n$, guess $T(n) = O(n \log n)$ — formally, that $T(n) \leq c \cdot n \log n$ for some $c$ and all $n \geq n_0$. Substitute the guess into the recurrence:

$$T(n) \leq 2 \cdot c \cdot (n/2) \log(n/2) + n = c n \log n - c n + n = c n \log n - (c - 1) n$$

For this to be at most $c n \log n$, the condition is $(c - 1) n \geq 0$, i.e., $c \geq 1$. The base case fixes $c$ for small $n$. The guess holds.

Substitution is the most general method but also the hardest — you have to guess right. It's a good fallback when the others don't apply.

### The recursion-tree method

Draw the recursion tree, sum the work at each level, then sum the levels.

For $T(n) = 2T(n/2) + n$: the root does $n$ work. Its two children do $n/2$ each, totaling $n$. The four grandchildren do $n/4$ each, totaling $n$. Each level does $\Theta(n)$ work, and there are $\Theta(\log n)$ levels before subproblems shrink to size 1. Total: $\Theta(n \log n)$.

For $T(n) = T(n/2) + 1$ (binary search): the root does $1$ work. Its child does $1$. Each level does $1$ work, and there are $\Theta(\log n)$ levels. Total: $\Theta(\log n)$.

For $T(n) = 2 T(n/2) + n^2$: the root does $n^2$ work. Its two children do $(n/2)^2 = n^2/4$ each, totaling $n^2/2$. The work at each level is geometrically decreasing, so the root dominates. Total: $\Theta(n^2)$.

Recursion trees are visual and concrete. They're my preferred method when I'm not sure what shape the answer will take.

### The Master Theorem

The notation appendix has the statement and three worked examples. The Master Theorem is a pre-packaged answer to recurrences of the form $T(n) = a T(n/b) + f(n)$. Use it when it applies; fall back to substitution or trees when it doesn't.

The shapes it *doesn't* handle:

- $T(n) = T(n-1) + 1$ (linear recursion, not divide-and-conquer): unroll directly to get $T(n) = \Theta(n)$.
- $T(n) = T(\sqrt{n}) + 1$: change variable $m = \log n$, get $T(2^m) = T(2^{m/2}) + 1$, which is $\Theta(\log m) = \Theta(\log \log n)$.
- $T(n) = 2 T(n/2) + n \log n$: doesn't match any case cleanly because $f(n) = n \log n$ is $\Theta(n^{\log_b a})$ times a logarithm. The extended master theorem (or substitution) gives $T(n) = \Theta(n \log^2 n)$.

## Amortized analysis methods

When a data structure does expensive work occasionally and cheap work the rest of the time, three methods quantify the average cost over a sequence.

### The aggregate method

Compute the total cost of any sequence of $n$ operations, then divide by $n$.

For chapter 8's dynamic array: a sequence of $n$ appends triggers resizes at sizes $1, 2, 4, 8, \ldots, n$. The cost of all resizes is $1 + 2 + 4 + \cdots + n < 2n$. Plus the $n$ append-after-resize operations, each costing $1$. Total: $O(n)$. Per-operation: $O(1)$ amortized.

The aggregate method is the most intuitive of the three. Use it when the sequence has a recognizable pattern of expensive operations.

### The accounting method

Assign each operation a *credit* — an upper bound on its cost that may exceed its actual cost. The surplus credit is "saved up" and used to pay for future expensive operations. The amortized cost per operation is the credit, *provided you can prove the accumulated savings never go negative*.

For chapter 12's chained hash table: charge $3$ per insert. $1$ pays for the actual insert. The other $2$ are credit: $1$ deposit on the new item, $1$ deposit on an old item. When the table doubles and rehashes, every item has accumulated enough credit to pay for its move (each move costs $1$, and the doubling guarantees at least as many credits as old items). Amortized cost: $O(1)$.

The accounting method is good when the work has a clear "I'll pay you back later" structure.

### The potential method

Define a *potential function* $\Phi: \text{state} \to \mathbb{R}_{\geq 0}$ that captures the structure's stored work. The amortized cost of an operation is its actual cost plus the change in potential:

$$\hat{c}_i = c_i + \Phi(D_i) - \Phi(D_{i-1})$$

If you choose $\Phi$ so that $\Phi(D_n) \geq \Phi(D_0)$, then summing telescopes: $\sum \hat{c}_i \geq \sum c_i$, so the amortized total bounds the actual total.

For chapter 14's union-find with path compression and union by rank: the potential function counts something like "the sum of the levels of the rank hierarchy each node lives below". Operations that compress paths decrease the potential by a lot, paying for their own work; operations that just walk paths increase it by a little. The careful analysis (which I sketch in the chapter and which Tarjan worked out fully in 1975) yields the inverse-Ackermann bound.

The potential method is the most powerful and the most abstract. It's what you reach for when the cost structure is too tangled for credits to cover cleanly.

## The inverse Ackermann function

The Ackermann function $A(m, n)$ is a fast-growing function defined by a double recursion. Its values grow faster than any primitive recursive function — $A(4, 4)$ is a number too large to write down with conventional notation.

The *inverse* Ackermann function $\alpha(n)$ is defined (informally) as the smallest $k$ such that $A(k, k) \geq n$. It grows so slowly that for any $n$ you'll ever see in practice — atoms in the universe, microseconds since the Big Bang, you name it — $\alpha(n) \leq 4$. It is *not* a constant function (it does grow), but for engineering purposes you can treat it as one.

The inverse Ackermann appears in exactly one place in this book: the amortized cost of union-find with both path compression and union by rank (chapter 14). The bound $O(\alpha(n))$ per operation is the tightest known, and it's also a *lower bound* in the pointer-machine model — you cannot do better with the operations on offer.

## Probability essentials

A handful of probability facts come up in the book, especially in the chapters on randomized algorithms (quicksort's expected analysis, Bloom filters' false-positive rate, hashing's expected chain length).

**Linearity of expectation.** $E[X + Y] = E[X] + E[Y]$, regardless of whether $X$ and $Y$ are independent. This is the most useful single fact in randomized algorithm analysis. To bound the expected total work of an algorithm, decompose the work into indicator variables for each "event" (e.g., a comparison happens), bound the expectation of each indicator (the probability the event happens), and add them up.

**Indicator variables.** $X_A = 1$ if event $A$ happens, $0$ otherwise. Then $E[X_A] = \Pr[A]$. This is how chapter 4's expected analysis of randomized quicksort works: define $X_{ij} = 1$ if elements at ranks $i$ and $j$ are compared, $0$ otherwise. The total comparisons is $\sum X_{ij}$. By linearity, the expected total is $\sum \Pr[\text{comparison happens}]$, which works out to $\Theta(n \log n)$.

**Independence.** Events $A$ and $B$ are independent if $\Pr[A \cap B] = \Pr[A] \cdot \Pr[B]$. The Bloom filter analysis assumes the $k$ hash functions are independent — under that assumption, the probability all $k$ bits for a never-inserted key are set is $(1 - e^{-kn/m})^k$, which the chapter optimizes over $k$.

**Markov's inequality.** For a non-negative random variable $X$ with finite mean: $\Pr[X \geq t] \leq E[X]/t$. The weakest of the standard concentration bounds, but it requires no assumptions beyond non-negativity. Often the first tool you reach for.

**Chernoff bounds.** For a sum of independent indicator variables $X = \sum X_i$ with mean $\mu$: $\Pr[X \geq (1+\delta)\mu] \leq e^{-\delta^2 \mu / 3}$ for $\delta \in (0, 1]$. This is *exponentially* tighter than Markov and is what makes randomized algorithms reliable in practice — the probability of being far from the expected behavior decays exponentially fast.

The book uses Markov implicitly in some upper-bound arguments and gestures at Chernoff in the analysis of skip lists and randomized hashing. Detailed Chernoff derivations are out of scope here; the takeaway is that *sums of independent random variables concentrate around their mean fast*, which is why randomized algorithms work as well as they do.

## Working with floors and ceilings

Recurrences and analyses often involve $\lfloor n/2 \rfloor$ and $\lceil n/2 \rceil$. Two useful facts:

- $\lfloor n/2 \rfloor + \lceil n/2 \rceil = n$.
- $\lfloor \log_2 n \rfloor + 1 = \lceil \log_2(n+1) \rceil$ — the number of bits to represent $n$.
- When solving recurrences, you can usually drop floors and ceilings asymptotically: $T(n) = T(\lfloor n/2 \rfloor) + 1$ has the same $\Theta$ behavior as $T(n) = T(n/2) + 1$. The formal justification involves bounding the recurrence above and below by integer-valued recurrences, but the practical shortcut is fine for almost all the analyses in this book.

## When the math gets in the way

Most of the analyses in this book are not deep mathematics. They're a sequence of moves: write down what the algorithm does at each step, count the steps as a sum or a recurrence, simplify using the identities above, report the answer in $\Theta$ form. When an analysis feels intractable, the most common culprits are:

1. **Not separating cases.** Worst, average, and best can have very different shapes. Pick one and stick to it.
2. **Trying to be precise about constants when $\Theta$ would do.** Inside a $\Theta$, constants and lower-order terms are noise. Drop them early.
3. **Reaching for the Master Theorem when the recurrence isn't divide-and-conquer.** Linear-recursion recurrences ($T(n) = T(n-1) + f(n)$) unroll directly to a sum; trying to force them through the Master Theorem just wastes time.
4. **Forgetting that amortized analysis is over a sequence.** A single operation may exceed the amortized bound. What's guaranteed is the *total* over a long enough sequence.

When in doubt: write the sum or the recurrence on paper, solve it with the toolkit above, sanity-check the answer against a small numerical experiment, and report the asymptotic. The notation appendix has the language for the report; this appendix has the tools for the work.
