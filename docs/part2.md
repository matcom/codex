# Fundamental Data Structures

In the first part of this Codex, we treated data largely as an abstract sequence—a collection of items that we could index, compare, and rearrange at will. We discovered that by imposing logical order, we could achieve remarkable algorithmic efficiency. However, algorithms do not exist in a vacuum; they must inhabit the physical reality of a computer's memory.

In this part, we shift our focus from the logic of the process to the topology of the data. Here, we explore how the way we organize information in memory—whether as a contiguous block or a web of pointers—determines the physical limits of the algorithms we write.

## What We Will Explore

In this part, we move beyond the high-level abstractions provided by Python's built-in types to implement the essential structures that form the foundation of all modern software systems:

* **Memory and Sequences**: We begin by examining the trade-offs between contiguous memory (arrays) and linked structures, understanding why the physical layout of data is the primary driver of performance.
* **Linked Lists**: We implement the most fundamental non-contiguous structure, exploring how pointers allow for dynamic growth and efficient insertions at the cost of random access.
* **Stacks and Queues**: We build the primary abstractions for managing order and flow, implementing LIFO (Last-In, First-Out) and FIFO (First-In, First-Out) behaviors that are critical for everything from expression evaluation to task scheduling.
* **Hashing and Hash Tables**: We investigate the "magic" of constant-time access, learning how to bridge the gap between an arbitrary value and its physical location in memory through hash functions and collision resolution strategies.

## What You Will Learn

By the end of this part, you will have moved from a theoretical understanding of algorithms to a practical mastery of their physical containers. Specifically, you will learn:

1. **The Physicality of Data**: Why the distinction between a pointer and an index is the most important decision in low-level system design.
2. **Trade-off Analysis**: How to weigh the benefits of fast insertion against the necessity of fast retrieval, moving beyond simple Big O notation to consider cache locality and memory overhead.
3. **Abstractions and Protocols**: How to use Python’s modern type system and protocols to implement these structures in a way that is generic, reusable, and mathematically sound.
4. **Building Blocks**: How these simple structures—lists, stacks, and queues—serve as the indispensable components for the more complex trees and graphs we will encounter later in the Codex.

In the same way that a builder must understand the properties of wood, steel, and stone, a computer scientist must understand the properties of data structures. We are moving from the design of the strategy to the selection of the material.
