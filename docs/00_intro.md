# Foundations {.unnumbered}

An algorithm is a recipe a machine can follow without thinking. That sentence is mostly right and a little misleading, and the difference is what this whole book is about.

By the end of this chapter, you'll be able to take any algorithm you read in the rest of the book — or anywhere else — and ask it the three questions that, between them, decide whether it's worth your time. You won't have to take any algorithm on faith again.

Most of what follows is small, deliberate work: defining what counts as an algorithm, building a way to measure how fast or slow one is without depending on the hardware you happen to own, and naming the analytical machinery the rest of the book leans on. None of it is glamorous on its own. All of it pays off in every chapter that comes after.

## What counts as an algorithm

You probably already have a working definition: an algorithm is a sequence of steps a computer can follow to solve a problem. That's good enough for most of life. For this book, I want to be a little stricter.

In the Codex, an algorithm is a **formal mathematical object**: a precise strategy that exploits the structure of its input to produce a specific output, efficiently. Three properties are doing the work:

- **Finiteness.** The description fits on a finite number of pages, and on any valid input the procedure halts in a finite number of steps. Recipes that go on forever don't count, no matter how clever.
- **Correctness.** The procedure produces the right answer for every valid input — not just the ones you remembered to test.
- **Definiteness.** Every step is unambiguous. There's no room for the executor to "do the obvious thing" — that's where bugs and disagreements live.

Historically, textbooks have written algorithms in **pseudo-code** — a flexible, English-like sketch of the steps, with the understanding that you'll translate it into a real programming language to actually use it.

I've never liked pseudo-code. It hides exactly the details that matter when you sit down to implement something. The gap between *"swap the elements at positions $i$ and $j$"* and *"no, you can't, you forgot you were working with an immutable list"* is where most of an algorithm's real character lives.

This book uses runnable **Python 3.13** instead. Every code block you see in a chapter is extracted into the actual `codex` Python package by a small tool called `illiterate`, and every demonstration block is executed by Quarto when the book renders. If an algorithm in the book is wrong, the book won't render. If a diagram is wrong, the diagram won't draw. The book and the code can never disagree.

## The three questions

When I've implemented an algorithm — really implemented it, not just described it — I'm only halfway done. The other half is asking it three questions, in order.

I want you to internalize these three, because they're going to come back at the end of every chapter in this book, in this exact order, as the recurring closing template.

**Is it correct?** Does the algorithm produce the right answer on *every* valid input — not just the ones you tried, but the ones you didn't think of: the empty input, the single-element input, the input where every element is the same, the input some adversary built to mess with you?

I won't usually do formal Hoare-logic proofs of correctness. Something looser will do: an intuitive argument about why the algorithm must be right — invariants the loop preserves, exhaustive case analysis, sometimes a small inductive sketch. Enough to convince a careful skeptic; not enough to satisfy a formal verifier.

**How efficient is it?** Once you trust the answer is right, you ask what it cost to get there. Two resources matter: **time** (the number of operations performed) and **space** (the amount of memory used along the way). For each, I'll give the cost as a function of the input size — the bigger the input, the more interesting the question gets.

**Is it optimal?** The third question is the most interesting, and the one most often skipped. "Optimal" doesn't mean "fast enough." It means: is there a *theoretical* lower bound on this problem that says no algorithm can possibly do better, and does this one meet it?

When you can answer all three — yes it's correct, here's how efficient, yes it hits the lower bound — you've solved the problem completely. The computational task stops being a research question and becomes a settled fact.

You'll see in the very next chapter that even the most boring algorithm in the book — linear search — has a satisfying answer to all three.

## Why I count operations, not seconds

Here's a problem. If I tell you *"my algorithm takes 0.3 seconds on a 1,000-element input,"* you've learned almost nothing useful.

You don't know what computer I ran it on. You don't know what language I wrote it in. You don't know whether 0.3 seconds is good or terrible for this problem. And you have no way to predict what happens when the input gets bigger.

To talk about efficiency in a way that survives hardware changes, language choices, and the passage of time, I'll work inside an idealized model of computation called the **Random Access Machine** — the RAM model. The name is unhelpful (it has nothing to do with the memory chip you call RAM); what matters are the three assumptions.

- **Basic operations cost one unit of time.** Arithmetic, comparisons, assignments, function calls — all unitary. Real hardware doesn't actually work this way (multiplication is slower than addition, for instance), but at the scale of comparing one algorithm against another, the difference washes out.
- **Memory is a sequence of cells.** Each cell holds one item — a number, a character, a reference.
- **Any memory cell is reachable in one unit of time.** That's the "random access" — no penalty for distance. Real hardware has caches and locality effects; I'm ignoring them on purpose, so the algorithm's structure isn't drowned out by the hardware's idiosyncrasies.

The RAM model is a deliberate caricature. It works because, for most algorithms most of the time, the caricature doesn't change the conclusion. It starts to break down in specialized areas — numerical algorithms where the cost of a single multiplication actually matters, or cache-aware algorithms where memory layout dominates the runtime. I'll flag those exceptions when they come up.

## Scaling, not stopwatching

Even inside the RAM model, the absolute number of operations is rarely what I care about. What I care about is how the cost **grows** as the input gets bigger.

The reason matters. Imagine I have an algorithm that scales **linearly**: doubling the input doubles the running time. Yours scales **quadratically**: doubling the input quadruples the running time. Today, on a small input, your algorithm might beat mine — maybe you wrote it in C++ and I wrote mine in Python, so your constants are smaller. But there's some input size beyond which my "slower" linear algorithm wins, no matter what hardware it runs on, no matter what language it was written in. And as the years pass and the inputs people care about get larger, that crossing-point matters more, not less.

Scaling behavior is hardware-independent, language-independent, future-proof in a way that "0.3 seconds" never is. It tells you the shape of the algorithm's cost, which is what you actually need to know.

To talk precisely about scaling, I'll use **asymptotic notation**. The one you'll see most is the big-O. When I write that an algorithm runs in $O(n)$ time, I mean: for inputs large enough, the running time is at most some constant multiple of $n$. Doubling the input at most doubles the running time. Formally, there's a constant $c$ and a threshold $n_0$ such that the running time $f(n)$ stays below $c \cdot g(n)$ for every $n > n_0$, where $g(n) = n$.

The nice thing about asymptotic notation is that it throws away exactly the details I want thrown away: constant factors, low-order terms, anything that depends on the hardware or the implementation language. An algorithm that takes $3n + 2$ steps is $O(n)$. An algorithm that takes $0.001 n$ steps is also $O(n)$. From the asymptotic point of view, they're the same algorithm.

I'm not going to be religious about big-O proofs. Most of the time, intuitions like *"one for-loop is $O(n)$, two nested for-loops are $O(n^2)$"* are exactly what you need. When an algorithm has a subtler cost — $O(n \log n)$, for instance, neither linear nor quadratic — I'll spend a paragraph on why, and that paragraph will earn its keep.

## Where this leaves you

You now have the tools the rest of the book leans on: the definition of an algorithm, the three questions, the RAM model, and asymptotic notation. None of these is glamorous on its own. Together, they're enough to think clearly about any of the roughly hundred algorithms this book is going to throw at you.

The next chapter starts with the simplest one: linear search. It'll be almost embarrassing how little it does — and then, by the time you've asked it the three questions, it'll be more interesting than you expected.

## Notes and further reading

The three-question template — correctness, efficiency, optimality — is the implicit structure of any classical algorithms text, but it's rarely named that explicitly. For the formal treatment of correctness via loop invariants, see Cormen, Leiserson, Rivest and Stein's *Introduction to Algorithms* (CLRS), 4th ed., chapter 2. For asymptotic notation made rigorous, CLRS chapter 3 is the standard reference. The RAM model is treated thoroughly in Sedgewick and Wayne's *Algorithms*, 4th ed., section 1.4. The literate-programming idea this book uses goes back to Knuth's *Literate Programming* (1992); the specific tooling — `illiterate` for extraction, Quarto for rendering — is described in the project's `AGENT.md`.
