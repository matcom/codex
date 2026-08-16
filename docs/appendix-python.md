# A Python Primer

This Codex uses Python 3.13 as its executable notation. That choice carries some baggage — Python is slower than C, less expressive than Haskell, less type-safe than Rust — but it earns its keep on one axis I care about: *you can read it the first time*. The code I write in the chapters is meant to be the algorithm, not an obstacle between you and the algorithm. This appendix is the glossary that makes that promise honest. If you've programmed in any modern language, most of what's here will look familiar; the parts that won't are usually about the *type system*, which Python 3.13 changed substantially in 2024 and which I lean on heavily.

I won't try to teach you Python. There are better books for that. What I'll do is name the features I actually use, show the idiomatic shape, and call out the parts that look surprising if you're coming from another language. If something in a chapter looks unfamiliar, this appendix is where to look first.

## Reading code as algorithms

Throughout the book I follow a small set of conventions to keep code readable as algorithm pseudocode:

- **Type annotations are mandatory** on function signatures, class attributes, and module-level variables. If a name has a type written next to it, you should never have to guess what shape it holds.
- **No `Optional` where a sentinel will do.** When a function returns "the index, or -1 if not found", I write `-> int` and document the convention, not `-> int | None`. The cost is a single comment; the gain is that the type signature stays simple.
- **One thing per name.** A variable named `result` is only ever the final answer; a variable named `i` is only ever a loop index. I don't reuse names across responsibilities.
- **No clever one-liners.** A four-line loop that's obviously a loop beats a list comprehension that's secretly an algorithm.

## Variables and the assignment model

A name in Python is a reference to an object. The object has a type; the name doesn't. That asymmetry is what people mean when they say Python is *dynamically typed*: the same name can be rebound to a different type during execution. The annotations I add are checked by tools like `mypy` and `pyright` but not by the interpreter — they're documentation that the tooling enforces.

```python
n: int = 42
name: str = "Codex"
is_active: bool = True
pi: float = 3.14159
```

Assignment is reference-copy, not value-copy. After `b = a`, the names `a` and `b` point at the same object. For immutable types (int, str, tuple) this distinction never matters because you can't change the object in place. For mutable types (list, dict, set, your own classes) it matters a great deal — modifying `b` modifies what `a` sees too. The chapters that build mutable data structures lean on this constantly.

## Built-in collections

Four built-in collection types do most of the work in the standard library:

- `list[T]` — a dynamic array (chapter 8 builds one from scratch to show why it's $O(1)$ amortized for append).
- `dict[K, V]` — a hash table (chapter 12 builds one from scratch).
- `set[T]` — a hash table with no values, used for fast membership.
- `tuple[T, ...]` — an immutable, fixed-arity sequence.

The chapters I write almost always *use* the built-in `list` for input or output, because it's the natural shape in Python. But when a chapter is *about* a sequence structure, I build the structure from scratch on top of a fixed-size array (a Python list pre-allocated with `[None] * cap`) so the cost model stays visible.

## Slicing

A slice expression `seq[a:b]` creates a new sequence containing items at indices `a, a+1, ..., b-1`. The right endpoint is exclusive. Slices of `list` and `str` allocate fresh memory; they are not views. That's an important cost: writing `arr[mid:]` inside a recursive call allocates a new list of half the size every level, turning what looks like in-place recursion into $\Theta(n \log n)$ extra space. When a chapter needs in-place behavior, it passes indices `(lo, hi)` rather than slicing.

```python
xs = [10, 20, 30, 40, 50]
xs[1:4]      # [20, 30, 40] — new list
xs[::2]      # [10, 30, 50] — step of 2
xs[::-1]     # [50, 40, 30, 20, 10] — reversed
```

Negative indices count from the end: `xs[-1]` is the last element.

## Control flow

Two looping constructs cover essentially everything algorithmic:

```python
for item in iterable:
    ...

while condition:
    ...
```

`for` iterates anything that implements the iteration protocol (`__iter__` returning an iterator with `__next__`). `while` runs until a boolean expression goes false. Inside either loop, `break` exits, `continue` skips to the next iteration, and `else` (yes, loops have an `else` clause) runs only if the loop completed without a `break`.

Conditional logic uses `if` / `elif` / `else`. Python's truthiness rules treat empty containers, `0`, `0.0`, `""`, and `None` as false; everything else as true. I rely on this for idiomatic checks like `if not stack:` to mean "the stack is empty".

## Functions

Functions are defined with `def`. Arguments can be positional, keyword, or both. Default values are evaluated *once at definition time*, which is a notorious source of bugs if the default is mutable:

```python
def bad(items: list[int] = []) -> list[int]:  # don't do this
    items.append(1)
    return items

def good(items: list[int] | None = None) -> list[int]:
    if items is None:
        items = []
    items.append(1)
    return items
```

The Codex never writes `def f(x=[])`. The pattern above (default `None`, materialize inside) is the safe shape.

Functions are first-class objects. You can pass them as arguments, return them from other functions, and store them in data structures. This is how chapter 5 implements custom ordering — by accepting a comparison function as an argument.

## Lambdas

A `lambda` is an anonymous function restricted to a single expression. I use them only when the function body is genuinely one short expression, typically as a key for sorting or as a custom comparator:

```python
points.sort(key=lambda p: (p.y, p.x))
```

If the body grows beyond an expression, I write a `def` with a real name. Multi-line lambdas don't exist in Python by design, and that's a feature.

## Classes

A class bundles state (attributes) with behavior (methods). Python's class syntax is lightweight:

```python
class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def distance_to(self, other: "Point") -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx * dx + dy * dy) ** 0.5
```

The first argument to every method is `self` — the instance being operated on. The `__init__` method runs at construction time. The string `"Point"` in the type hint is a *forward reference* needed because the class isn't fully defined yet inside its own body; from Python 3.13 onward you can also write `from __future__ import annotations` at the top of the file to make all annotations lazy.

## Dunder methods

Dunder methods (double-underscore methods like `__init__`, `__len__`, `__getitem__`) hook into Python's syntax. Implementing them is how a custom class gets to behave like a built-in. The ones I use most often:

| Method | Triggers |
|---|---|
| `__init__(self, ...)` | construction (`Point(1, 2)`) |
| `__repr__(self)` | the interactive repr / `repr(obj)` |
| `__eq__(self, other)` | `obj == other` |
| `__hash__(self)` | use as dict key or in a set |
| `__len__(self)` | `len(obj)` |
| `__getitem__(self, k)` | `obj[k]` |
| `__setitem__(self, k, v)` | `obj[k] = v` |
| `__iter__(self)` | use in a `for` loop |
| `__contains__(self, x)` | `x in obj` |
| `__lt__`, `__le__`, ... | `<`, `<=`, ... (with `@functools.total_ordering` to fill in the rest) |

Chapter 8's `DynamicArray[T]` implements `__len__`, `__getitem__`, `__setitem__`. Chapter 9's `LinkedList[T]` implements `__iter__`. Chapter 12's `HashMap[K, V]` implements `__getitem__`, `__setitem__`, `__contains__`, and `__len__`. Each one is a deliberate choice about *which language affordances the structure participates in*.

## Generators and `yield`

A function containing `yield` is a *generator*. Calling it doesn't run the body; it returns a generator object that lazily produces values as they're requested. Generators are how you write iteration over your own structures cheaply, without materializing an intermediate list:

```python
def naturals(stop: int) -> Iterator[int]:
    i = 0
    while i < stop:
        yield i
        i += 1
```

The `for` loop calls `next(gen)` repeatedly until it raises `StopIteration`. In chapter 9 I use a generator inside `__iter__` to walk a linked list without copying its contents into a Python list.

## Type annotations and modern generics

This is the place where Python 3.13 differs most from older codebases. Two features matter:

**PEP 695 generic syntax.** Pre-3.12, generics required `TypeVar` declarations:

```python
# old style
from typing import TypeVar
T = TypeVar("T")
def first(xs: list[T]) -> T:
    return xs[0]
```

3.13 lets you write the type parameter inline in brackets after the name:

```python
# new style — used throughout this book
def first[T](xs: list[T]) -> T:
    return xs[0]

class Stack[T]:
    ...
```

The new syntax is cleaner, scoped properly (the `T` only exists inside `first`), and removes the boilerplate. Every generic function and class in the Codex uses it.

**PEP 695 type aliases.** A type alias gives a name to a complex type expression. Old style required `TypeAlias` from `typing`; new style uses the `type` keyword:

```python
type Comparator[T] = Callable[[T, T], int]
type Graph[V] = dict[V, list[V]]
```

The alias is lazily evaluated, so it can reference itself recursively (useful for trees in Part III).

## Protocols and structural typing

The `typing.Protocol` mechanism is Python's answer to *structural typing* — describing a type by what it can *do* rather than what it *is*. The standard library defines several protocols I lean on:

- `Sequence[T]` — has `__getitem__` and `__len__`; can be iterated.
- `MutableSequence[T]` — additionally has `__setitem__`, `append`, `pop`, etc.
- `Iterable[T]` — has `__iter__`.
- `Iterator[T]` — has `__iter__` and `__next__`.
- `Hashable` — has `__hash__` (and a consistent `__eq__`).
- `Comparable[T]` (custom, but common) — supports `<` against `T`.

Writing a function that takes `Sequence[T]` instead of `list[T]` means it works on lists, tuples, strings (for `str`), and any custom array-like class. The chapters lean on this for the same reason they lean on PEP 695 generics: the algorithm is about the *shape* of the data, not the *Python class* of the data.

You can define your own protocol with `@runtime_checkable` if you want `isinstance` checks; I rarely need that.

## Dataclasses

A `@dataclass` decorator auto-generates `__init__`, `__repr__`, and (optionally) `__eq__` from class attributes:

```python
from dataclasses import dataclass

@dataclass
class Edge:
    src: int
    dst: int
    weight: float
```

This is the same as writing the three dunder methods by hand. The Codex uses dataclasses for plain "record" types — the `_Entry[K, V]` in chapter 12's hash table is one, and Part III's tree nodes will be others. When the class needs custom behavior beyond data, I write the dunder methods explicitly.

## Optional, union, and `None`

Python 3.10+ supports the pipe syntax for union types:

```python
def find(xs: list[int], target: int) -> int | None:
    for i, x in enumerate(xs):
        if x == target:
            return i
    return None
```

`int | None` is the same as `Optional[int]`. The Codex prefers the pipe syntax. When `None` is a legitimate return value, the caller must check for it before using the result (`mypy --strict` enforces this).

## Exceptions

`raise` throws an exception. `try` / `except` catches it. `finally` runs regardless. The Codex raises exceptions for *programming errors* (e.g., popping from an empty stack) and returns sentinel values for *expected absence* (e.g., a search miss). The split is a judgment call; the rule is to be consistent within a structure.

```python
class StackEmpty(Exception):
    pass

class Stack[T]:
    def pop(self) -> T:
        if not self._items:
            raise StackEmpty("pop from empty stack")
        return self._items.pop()
```

I almost never catch broad exceptions (`except Exception`). When I do catch, I catch the specific class.

## Context managers (`with`)

A `with` block manages setup and teardown around a body. The standard use is for files (`with open(...) as f:`), but the protocol works for anything that needs paired enter/exit. I rarely need to *implement* a context manager in the Codex, but I use them whenever a chapter touches a file.

## `match` statements

Python 3.10's `match` is a structural pattern-matching construct. I use it sparingly — usually only when dispatching on the shape of an algebraic data type:

```python
match node:
    case Leaf(value):
        return value
    case Branch(left, right):
        return walk(left) + walk(right)
```

For simple value dispatch, an `if / elif` chain is almost always clearer. `match` earns its place when the cases are *structural* — when they're naming and binding parts of the matched object.

## Iteration helpers

A handful of built-ins and `itertools` helpers come up often:

- `enumerate(xs)` yields `(index, value)` pairs.
- `zip(a, b)` yields `(a[i], b[i])` pairs, stopping at the shorter one.
- `range(start, stop, step)` is a memory-cheap arithmetic progression.
- `reversed(xs)` iterates in reverse without copying.
- `sorted(xs, key=..., reverse=...)` returns a new sorted list.
- `min(xs)`, `max(xs)`, `sum(xs)`, `any(xs)`, `all(xs)` are the standard reductions.

From `itertools`: `chain`, `accumulate`, `combinations`, `permutations`, `product` show up occasionally. From `collections`: `deque`, `Counter`, `defaultdict` are tools I sometimes reach for in benchmarks but build from scratch when a chapter is about them.

## Running the code

Every code block in the chapters that begins with ```` ```{python} ```` is executed by Quarto when the book renders. The chunks share state within a chapter (later chunks see names defined by earlier ones). Plain ```` ```python ```` blocks are inert — they're shown but not run. When you see an *output line* under a chunk, that output is the actual result of executing the chunk during the most recent build, not a hand-written example.

The illiterate tool extracts every executable chunk into `src/codex/` so the code is also importable as a regular Python package. If you've cloned the repo, `uv run python -c "from codex.structures.array import DynamicArray; ..."` will give you a REPL-friendly version of any structure from the book.
