# Foundations {.unnumbered}

Before we begin our journey through specific algorithms, we must establish the ground on which we stand. To study algorithms is to study the limits of what can be computed and the cost of doing so.

## What is an Algorithm?

At its simplest, an algorithm is a finite sequence of well-defined, computer-implementable instructions to solve a class of specific problems. However, in this Codex, we view an algorithm as a **mathematical object**--a strategy that exploits the structure of data to achieve an outcome efficiently.

Every algorithm we implement must satisfy three fundamental properties:
1.  **Finiteness**: It must terminate after a finite number of steps.
2.  **Definiteness**: Each step must be precisely defined.
3.  **Effectiveness**: Each operation must be basic enough to be performed exactly.
4.  **Correctness**: The algorithm must always produce the correct output for every valid input.

## Measuring Efficiency

In Computer Science, we rarely care about how many seconds an algorithm takes on a specific machine. Instead, we care about how the effort scales as the input size $n$ grows. This is the essence of **Big O Notation**.

* **$O(1)$ - Constant Time**: The "speed of light." No matter how big the universe gets, the time remains the same.
* **$O(\log n)$ - Logarithmic Time**: The "magical" scaling. Even if you double the input, you only add one extra step. This is the gold standard for search.
* **$O(n)$ - Linear Time**: The "honest day's work." To know everything about $n$ items, you must look at $n$ items.
* **$O(n^2)$ - Quadratic Time**: The "barrier." As we will see in the sorting chapter, this often arises when we compare every item with every other item.
