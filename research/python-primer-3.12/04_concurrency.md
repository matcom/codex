# Python 3.12+ Iteration, Generators & Concurrency

This document explores the evolution of data processing and execution models in modern Python, focusing on how language-level features impact algorithmic efficiency and system performance.

## 1. Iterators & Generators: The Efficiency Foundation

Python's iteration model is built on two core protocols that allow for "lazy" data processing, ensuring that memory consumption remains independent of the dataset size ($O(1)$ space complexity for the stream itself).

### The Iteration Protocol
An object is iterable if it implements `__iter__`, which must return an **iterator**. An iterator must implement:
- `__iter__`: Returns itself.
- `__next__`: Returns the next value or raises `StopIteration`.

### Memory Efficiency with `yield`
Generators provide a high-level syntax for creating iterators. Instead of building a full collection in memory (e.g., a list), a generator function "pauses" execution, yielding values one by one.

**Back-of-the-envelope impact:**
- **List-based processing:** $O(N)$ memory. A list of 1 million integers (~28 bytes each) consumes ~28 MB.
- **Generator-based processing:** $O(1)$ memory. A generator for 1 million integers consumes ~128 bytes (the size of the generator object itself).

### Delegation with `yield from`
Introduced to simplify sub-generator delegation, `yield from` is more than a loop shortcut. It establishes a transparent bidirectional channel between the caller and the sub-generator, handling `StopIteration` and value passing efficiently.

```python
def recursive_walk(node):
    yield node.value
    for child in node.children:
        yield from recursive_walk(child)
```

### Python 3.12 Improvements
- **Generic Protocols (PEP 695):** Python 3.12 introduces a cleaner syntax for defining generic iterables.
  ```python
  from typing import Protocol, Iterator

  class Stream[T](Protocol):
      def __iter__(self) -> Iterator[T]: ...
  ```
- **Specialization:** The 3.12 interpreter specializes the bytecode for common iteration patterns, reducing the overhead of `__next__` calls in tight loops.

---

## 2. Async/Await: Structured Concurrency

Python 3.11 and 3.12 have significantly matured the asynchronous programming model, moving away from "unstructured" task management toward a safer, more predictable pattern.

### Task Groups (Python 3.11+)
The `asyncio.TaskGroup` is now the recommended way to run multiple concurrent tasks. It provides **Structured Concurrency**:
- If one task in the group fails, all other tasks are automatically cancelled.
- It guarantees that all tasks are finished (or cancelled) before the `async with` block exits.

### Exception Groups (`except*`)
Since multiple tasks can fail simultaneously, Python 3.11+ uses `ExceptionGroup` and the `except*` syntax to handle multiple exceptions in a single block.

```python
async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fetch_api_1())
            tg.create_task(fetch_api_2())
    except* ConnectionError as eg:
        for e in eg.exceptions:
            logger.error(f"Network error: {e}")
```

### Impact on Algorithm Design
- **Non-blocking I/O:** Algorithms that involve network or disk latency can achieve massive speedups by yielding control during wait times.
- **CPU-bound caveat:** `asyncio` is single-threaded. For CPU-intensive algorithms, `asyncio` primarily helps in managing the "orchestration" rather than the "computation" itself.

---

## 3. Performance & Evolution: Specialist Interpreter & Beyond

The "Faster CPython" project has introduced transformative changes to how Python code is executed.

### The Specialist Interpreter (PEP 659)
Introduced in 3.11 and refined in 3.12, the interpreter now "specializes" code during runtime.

1.  **Cold Stage:** Code starts as generic, slow bytecode.
2.  **Warming Stage:** The interpreter counts executions. Once "hot," it identifies patterns (e.g., "this loop always adds two integers").
3.  **Hot Stage:** The interpreter replaces generic opcodes with specialized ones (e.g., `BINARY_OP` becomes `BINARY_OP_ADD_INT`).
4.  **De-optimization:** If the types change (e.g., a float is passed), the interpreter "misses" and reverts to generic code.

**Impact:** Real-world performance gains of **10-50%** without changing a line of code.

### Python 3.13 Preview: The Next Frontier

#### Free-threading (PEP 703)
The removal of the Global Interpreter Lock (GIL) is currently experimental.
- **Multi-core Scaling:** CPU-bound algorithms can see a **3x to 5x speedup** on multi-core systems.
- **The "GIL Tax":** Removing the GIL requires more fine-grained locking. Single-threaded code might be **10-40% slower** in the free-threaded build due to this overhead.
- **Memory Impact:** Memory usage can **double** due to the need for thread-safe reference counting (immortal objects and biased reference counting).

#### Copy-and-Patch JIT (PEP 744)
Python 3.13 includes an experimental JIT compiler.
- **Mechanism:** It compiles "micro-ops" (intermediate representation) into machine code template "patches."
- **Current Impact:** Modest (**2-9%**) on math-heavy loops, near zero for general application logic. It represents the infrastructure for future, more aggressive optimizations.

## Summary: Back-of-the-Envelope Trade-offs

| Feature | Primary Benefit | Algorithmic Impact | Performance Tax |
| :--- | :--- | :--- | :--- |
| **Generators** | Memory Efficiency | $O(N) \to O(1)$ Space | Negligible (function call overhead) |
| **Task Groups** | Robust Concurrency | Parallel I/O Wait | Minimal orchestration overhead |
| **PEP 659 (3.12)** | Execution Speed | Reduced Constant Factors | Memory for inline caches |
| **Free-threading (3.13)**| Parallelism | True $1/N$ Time (CPU-bound) | 10-40% single-thread slowdown |
| **JIT (3.13)** | Execution Speed | Reduced constant factors (Math) | 10-20% memory increase |
