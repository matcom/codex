# Foundations {.unnumbered}

Before we begin our journey through specific algorithms, we must establish the ground on which we stand. To study algorithms is to study the limits of what can be computed and the cost of doing so.

## What is an Algorithm?

At its simplest, an algorithm is a procedure that takes an input and produces an output. However, in this Codex, we view an algorithm as a **formal mathematical object**—a precise strategy that exploits the structure of data to achieve an outcome efficiently.

To be considered a valid algorithm in our context, a procedure must satisfy several key characteristics:

- **Finiteness**: The description of the algorithm itself must be finite. Furthermore, for any valid input, the algorithm must always finish within a finite amount of time.
- **Correctness**: The algorithm must always produce the correct answer for every valid input within its problem class.
- **Definiteness (Formality)**: An algorithm is a formal procedure. It must be described in a language that admits no ambiguity regarding the operations to be performed. Historically, this has been achieved through mathematical notation; in this book, we use the **Python programming language**.

Most academic texts rely on **pseudo-code**—a high-level, informal description of an algorithm. While pseudo-code is useful for broad strokes, it often hides subtle complexities and can be interpreted in multiple ways.

In **The Algorithm Codex**, we deliberately avoid pseudo-code in favor of actual, runnable **Python 3.13**. By using a real programming language, we ensure that every operation is precisely defined and that the implementations you see are ready to be tested, scrutinized, and executed. This approach removes the "translation layer" between theory and practice, making the logic transparent and absolute.

## Analyzing Algorithms

Following the definition of what an algorithm is, we must establish a framework for evaluating them. Once an implementation is complete, the work of a computer scientist is only beginning. We must subject our solution to a rigorous three-step analysis to ensure it is not just a working program, but a complete solution to a computational problem.

When we finish writing an algorithm, we must ask ourselves three fundamental questions. Only when all three are answered can we consider our work in computer science truly satisfied.

**Is it correct?**

The first and most critical question is whether the algorithm always produces the expected output for any valid input. This is the property of **correctness**. While this book avoids exhaustive formal proofs, we will always strive to provide a deep, intuitive explanation of why the logic holds. We focus on the underlying mechanics of the algorithm and how it handles **corner cases**—those extreme or unusual inputs where many naive solutions fail.

**How efficient is it?**

Once we are certain the algorithm is correct, we must quantify its cost. We ask: **How efficient is this in terms of time and space?**. Using the scaling intuition of Big O notation, we analyze how the algorithm's resource requirements grow as the input size n increases . We look for the "bottlenecks" in the logic and determine whether the primary cost comes from the number of operations performed or the amount of memory consumed.

**Is it optimal?**

The final question is perhaps the most profound: **Is this the most efficient algorithm possible, or can there be a better one?** We are not just looking for a "fast" algorithm; we are looking for the theoretical limits of the problem itself. Throughout this Codex, we will try to provide intuitive proofs of **optimality**—explaining why a certain complexity (like O(nlogn) for comparison-based sorting) cannot be improved upon.

When we can prove—even intuitively—that we have reached the optimal efficiency for a correct algorithm, we have solved the problem completely. At that point, the computational task is no longer a mystery; it is a solved piece of the science of computation.

## Measuring Efficiency

Once we have established that an algorithm is correct, we must ask how much it "costs" to run. In this book, we care about two primary resources: **Time** (the number of operations performed) and **Space** (the amount of memory required).

However, hardware changes so rapidly that it is rarely useful to talk about performance in terms of seconds or megabytes. To remain hardware-agnostic, we use an idealized computational model.

In this book, and in most algorithmic analysis, we utilize the **Random Access Machine (RAM) model**. This model provides a controlled environment where we can precisely describe the number of steps an algorithm takes by assuming a **unitary unit of cost** for basic operations.

In the RAM model, we assume:

- **Unitary Operation Cost**: Basic operations—such as arithmetic, variable assignment, and method calls—all cost exactly one unit of time.
- **Discrete Memory Cells**: Memory is divided into discrete cells, each capable of holding one unit of data (such as a number, a character, or sometimes a small string).
- **Constant Access Time**: We can access any memory cell directly with a unitary cost. This is the "Random Access" from which the model takes its name; we can jump to any random location in memory without paying a penalty for distance.

Of course, this is an abstraction. In a real computer, multiplication is more expensive than addition, floating-point numbers carry additional costs, and memory is structured into complex layers of cache. However, the RAM model works exceptionally well for comparing algorithms in the abstract because it glosses over details that are often unimportant in the grand scheme of complexity. It only begins to break down in specialized areas, such as **numerical algorithms**, where the exact cost of multiplications versus additions or the precise layout of numbers in memory becomes critical to performance.

Furthermore, we rarely care about the absolute number of steps. Knowing that a specific sort takes exactly 1,024 operations is less useful than knowing how that cost grows as the input size $n$ increases.

The core of algorithmic analysis is **scaling**. For example:

- **Constant Cost ($O(1)$):** If you have a list of items and you want to access the 42nd element, that operation has a unitary cost of 1. It does not matter if the list has 1,000 items, 1 million items, or 1 billion items; the effort required to jump to that specific index remains the same.
- **Linear Cost ($O(n)$):** If you want to count every item in that list, you must visit each one. If the size of the input doubles, the cost of the operation doubles. If you have 1,000 items, the cost is 1,000; if you have 1 million, the cost is 1 million.

To formalize these scaling patterns, we use **asymptotic notation**, a terminology borrowed from mathematical analysis. This allows us to categorize algorithms into growth classes:

- **$O(1)$ - Constant Time**: The cost is independent of the input size.
- **$O(n)$ - Linear Time**: The cost grows in direct proportion to the input size.
- **$O(n^2)$ - Quadratic Time**: The cost grows with the square of the input size, often seen in algorithms with nested loops.

By focusing on these growth rates, we can determine the "efficiency ceiling" of our solutions and decide whether we have found the optimal approach for a given problem.

## Final Words

Now that we have settled our expectations, you are ready to start the journey. It will be fast-paced but--I hope--really exciting. We will discover many algorithms, close to a hundred of them! And in each case, we ill ask ourselves these same three questions. And, surprisingly often, we will be able to answer them pretty well!
