# Asymptotic Notation and Analysis

This appendix provides a formal grounding for the "scaling intuition" introduced in the foundations of the Codex. In the study of algorithms, we are less concerned with exact cycle counts and more with **asymptotic behavior**: how the resource requirements of an algorithm grow as the input size $n$ approaches infinity.

To analyze algorithms rigorously, we use a set of mathematical notations that allow us to ignore constant factors and lower-order terms, focusing instead on the **rate of growth**.

## The Big-O Family

Let $f(n)$ and $g(n)$ be functions mapping natural numbers to non-negative real numbers.

### Big-$O$ (Upper Bound)

We say that $f(n) = O(g(n))$ if there exist positive constants $c$ and $n_0$ such that:

$$0 \leq f(n) \leq c \cdot g(n) \text{ for all } n \geq n_0$$

This notation provides an asymptotic upper bound. If an algorithm is $O(n^2)$, it will perform no worse than quadratic time for large $n$.

### Big-$\Omega$ (Lower Bound)

We say that $f(n) = \Omega(g(n))$ if there exist positive constants $c$ and $n_0$ such that:

$$0 \leq c \cdot g(n) \leq f(n) \text{ for all } n \geq n_0$$

$\Omega$ provides a lower bound, representing the minimum amount of work an algorithm must perform.

### Big-$\Theta$ (Tight Bound)

We say that $f(n) = \Theta(g(n))$ if $f(n) = O(g(n))$ and $f(n) = \Omega(g(n))$. This means there exist positive constants $c_1, c_2,$ and $n_0$ such that:

$$c_1 \cdot g(n) \leq f(n) \leq c_2 \cdot g(n) \text{ for all } n \geq n_0$$

$\Theta$ is the most descriptive notation, as it tells us the algorithm grows exactly like $g(n)$.

### Little-$o$ and Little-$\omega$ (Strict Bounds)

- **$f(n) = o(g(n))$**: The growth of $f(n)$ is strictly less than $g(n)$. Formally, $\lim_{n \to \infty} \frac{f(n)}{g(n)} = 0$.

- **$f(n) = \omega(g(n))$**: The growth of $f(n)$ is strictly greater than $g(n)$. Formally, $\lim_{n \to \infty} \frac{f(n)}{g(n)} = \infty$.


## The Master Theorem

Many of the most efficient algorithms in this book (like Merge Sort) use a divide-and-conquer strategy. Their complexity is often expressed as a recurrence of the form:

$$T(n) = aT(n/b) + f(n)$$

where $a \geq 1$ is the number of subproblems, $b > 1$ is the factor by which the subproblem size is reduced, and $f(n)$ is the cost of work done outside the recursive calls. The Master Theorem provides a "cookbook" solution for such recurrences:

1. **If $f(n) = O(n^{\log_b a - \epsilon})$** for some $\epsilon > 0$, then $T(n) = \Theta(n^{\log_b a})$. (Work is dominated by the leaves).
2. **If $f(n) = \Theta(n^{\log_b a})$**, then $T(n) = \Theta(n^{\log_b a} \log n)$. (Work is balanced across levels).
3. **If $f(n) = \Omega(n^{\log_b a + \epsilon})$** and satisfies the regularity condition ($af(n/b) \leq cf(n)$), then $T(n) = \Theta(f(n))$. (Work is dominated by the root).


## The Hierarchy of Growth

Understanding the relative order of complexity functions is essential for selecting the right algorithm for a given problem size. Below is the standard hierarchy from slowest to fastest growth:

1. **$O(1)$ — Constant**: Accessing an array element, simple arithmetic.
2. **$O(\log n)$ — Logarithmic**: Binary search. The "gold standard."
3. **$O(n)$ — Linear**: Sequential scan.
4. **$O(n \log n)$ — Linearithmic**: Optimal comparison-based sorting (Merge Sort).
5. **$O(n^2)$ — Quadratic**: Nested loops (Bubble Sort).
6. **$O(n^k)$ — Polynomial**: General algorithmic complexity.
7. **$O(2^n)$ — Exponential**: Exhaustive search (Traveling Salesperson).
8. **$O(n!)$ — Factorial**: Permutations of a set.


As $n$ grows, the gaps between these classes become astronomical. While a $O(n^2)$ algorithm might be acceptable for $n=1,000$, it becomes entirely impractical for $n=1,000,000$, where an $O(n \log n)$ or $O(n)$ solution remains trivial for modern hardware.
