# A Python Primer

This appendix provides a concise overview of the Python 3.13 features and syntax used throughout **The Algorithm Codex**. While this book is not an introductory programming text, this primer serves as a reference for the specific idioms and modern type-system features that enable our clean, algorithmic implementations.

Python is a high-level, interpreted language that prioritizes readability and expressiveness. In this Codex, we treat Python as a executable notation for algorithms, leveraging its modern type system to ensure our code is both correct and self-documenting.

## Variables and Basic Types

Variables in Python are names that point to objects in memory. Unlike many lower-level languages, variables do not have fixed types; however, the objects they point to do.

```python
# Integers and Floats
n: int = 42
pi: float = 3.14159

# Strings and Booleans
name: str = "Codex"
is_active: bool = True

```

In the Codex, we always provide type hints for variables in global or class scopes to maintain clarity.

## Expressions and Statements

An **expression** is a piece of code that evaluates to a value (e.g., `2 + 2`), while a **statement** is an instruction that performs an action (e.g., an assignment or a function call).

Python supports standard arithmetic operators (`+`, `-`, `*`, `/`) and a specific operator for integer division (`//`), which we use extensively in binary search and partitioning algorithms to find middle indices.

## Control Flow: Loops and Conditionals

We rely on two primary looping constructs to traverse data structures: `for` loops for iterating over sequences and `while` loops for processes that continue until a specific logical condition is met.

```python
# Iterating over a sequence
for item in [1, 2, 3]:
    print(item)

# Conditional logic
if n > 0:
    # Do something
elif n < 0:
    # Do something else
else:
    # Default case

```

In our implementations of Selection Sort and Bubble Sort, we use `range()` to generate indices for controlled iteration.

## Functions

Functions are the primary unit of work in this book. We prefer "pure" functions that take inputs, perform a transformation, and return a result without side effects.

```python
def square(x: int) -> int:
    return x * x

```

## Classes and Objects

While the Codex favors a functional style, we use classes as simple data containers or to implement specific protocols. Python 3.13 allows for clean class definitions that integrate seamlessly with the type system.

```python
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

```

## Type Annotations and Modern Generics

The most important feature of the Codex's coding style is the use of **PEP 695 generics**, introduced in Python 3.12 and refined in 3.13. This allows us to write algorithms that work for any data type `T` while maintaining full type safety.

Instead of older `TypeVar` syntax, we use the elegant bracket notation:

```python
# A generic function that works for any type T
def identity[T](value: T) -> T:
    return value

# Using the 'type' alias for complex definitions
type Ordering[T] = Callable[[T, T], int]

```

This syntax is used throughout our searching and sorting implementations to ensure that an algorithm designed for integers works just as correctly for strings or custom objects, provided they satisfy the required protocols.

## The `Sequence` Protocol

In almost every chapter, we use `Sequence` or `MutableSequence` from the `typing` module. These are **Protocols**--they define what a type can *do* (like being indexed or having a length) rather than what it *is*. By using `Sequence[T]` instead of `list[T]`, our algorithms remain generic enough to work with lists, tuples, or custom array-like structures.
