# Foundations {.unnumbered}

Before we begin our journey through specific algorithms, we must establish the ground on which we stand. To study algorithms is to study the limits of what can be computed and the cost of doing so.

## What is an Algorithm?

At its simplest, an algorithm is a mechanical procedure that takes an input and produces an output. However, in this Codex, we view an algorithm as a **formal mathematical object**--a precise strategy that exploits the structure of data to achieve an outcome efficiently.

To be considered a valid algorithm in our context, a procedure must satisfy several key characteristics:

- **Finiteness**: The description of the algorithm itself must be finite. Furthermore, for any valid input, the algorithm must always finish within a finite amount of time, for any given input.
- **Correctness**: The algorithm must always produce the correct answer for every valid input within its problem class.
- **Definiteness**: An algorithm is a formal procedure. It must be described in a language that admits no ambiguity regarding the operations to be performed. Historically, this has been achieved through mathematical notation; in this book, we use the **Python programming language**.

Most academic texts rely on _pseudo-code_--a high-level, informal description of an algorithm. While pseudo-code is useful for broad strokes, it often hides subtle complexities and can be interpreted in multiple ways.

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

The core of algorithmic analysis is to look at how an algorithm time or memory cost _scales_ with data. For example, an algorithm that checks all items in a list exactly once scales _linearly_, which means if you double the size of the input, you expect the running time to double. However, an algorithm that scales _quadratically_ with the input size--for example, if you compare each item in a list with all others--has a very different behavior: if you double the input size, that algorithm _quadruples_ its runnign time.

The reason we care about scaling behavior rather than actual runtime cost is thus three-fold. First, it lets us reason about the efficiency of two different algorithms regardless of the hardware. If my algorithm scales better than yours, they will both be faster on fast hardware, and slower on slow hardware, but mine will beat yours in every ocasion. No need to discuss which hardware to buy to decide here.

But more importantly, if my algorithm is written with poor optimizations or in a slower language--like Python--but yours is written in C++, you might get an edge on small instances because you can run a tight loop in one milisecond while I need ten miliseconds to do the same. However, as the input data becomes larger and larger, there is a point after which your super optimized quadratic algorithm will always be worse than my lazy linear algorithm. This shouldn't be a justification to write lazy algorithms, but it does tells us we should focus on improving the high-level asymptotic complexity before low-level optimization tricks.

And finally, as time goes by, we expect hardware to improve, and thus we hope to tackle bigger and bigger problems with the same algorithms. If my algorithm scales linearly, next year when I get access to a twice-as-fast computer, I expect to solve a twice-as-big problem with the same resources (time and memory). However, if my algorithm scales quadratically, I have to wait until I get a computer four-times-as-fast to tackle a twice-as-big problem.

## Formalizing scaling behavior

Thus, scaling is what we care about. To formalize this notion we use something called **asymptotic notation**, which looks like this. If we want to say an algorithm scales _roughly linearly_ with input size, we say its running time (or memory) cost is $O(n)$.

Formally, this means the running time (or memory) can be expressed as some function $f(n)$ that grows as slow or slower than the linear function $g(n) = n$. In mathematical terms, we say there exists a constant $c$ and an input size $n_0$ such that for all $n > n_0$ we have $f(n) <= c \cdot g(n)$.

The nice thing about this formulation is that it lets us gloss over all the tiny details of an algorithm and talk just about the rough growth rate. It is easy to prove--although we won't do it--that in asymptotic analysis we can throw away constants and lower order terms, and just keep the higher order function. For example, if some algorithm has a time cost of $f(n) = 3n + 2$, that is still $O(n)$.

In this book, however, we won't concern ourselves too much with being strict at complexity analysis. For the most part, we will rely on intuitions like a single for loop is $O(n)$ and a double-nested loop is $O(n^2)$. However, for some algorithms we will need to perform a slightly more nuanced analysis to arrive at asymptotic cost functions like $O(n \log n)$ which are neither linear nor quadratic, and have their own and very interesting scaling behavior.

## Final Words

Now that we have settled our expectations, you are ready to start the journey. It will be fast-paced but--I hope--really exciting. We will discover many algorithms, close to a hundred of them! And in each case, we will ask ourselves these same three questions. And, surprisingly often, we will be able to answer them pretty well!
