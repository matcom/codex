# Python 3.12+ Advanced Functionality & The Type System

This document covers the modern type system and advanced object-oriented programming (OOP) features introduced or refined in Python 3.12. The focus is on PEP 695 (Type Parameter Syntax), improved generics, structural subtyping via Protocols, and modern `dataclasses`.

---

## 1. Modern Generics (PEP 695)

Python 3.12 introduces a more concise and readable syntax for defining generic functions, classes, and type aliases. This eliminates the need for explicit `TypeVar` declarations and `Generic` base classes in most cases.

### Generic Functions
Previously, defining a generic function required importing `TypeVar`. In Python 3.12+, you can define the type parameter directly in the function signature using square brackets.

```python
# Modern Syntax (Python 3.12+)
def get_first[T](items: list[T]) -> T:
    return items[0]

# Legacy Syntax (Pre-3.12)
from typing import TypeVar
T = TypeVar("T")
def get_first_legacy(items: list[T]) -> T:
    return items[0]
```

### Generic Classes
Similarly, classes no longer need to inherit from `Generic[T]`. The type parameter is scoped to the class body.

```python
# Modern Syntax
class Box[T]:
    def __init__(self, content: T):
        self.content = content

    def get_content(self) -> T:
        return self.content

# Usage
int_box = Box(10)      # Inferred as Box[int]
str_box = Box("Hello") # Inferred as Box[str]
```

### Bounds and Constraints
You can still apply bounds (type must be a subclass) and constraints (type must be one of several specific types) using the new syntax.

```python
# T must be a subclass of float (Upper Bound)
def process_numeric[T: float](value: T) -> T:
    return value * 2

# T must be exactly str or bytes (Constraints)
def handle_data[T: (str, bytes)](data: T) -> T:
    return data
```

### Key Advantages
- **No Manual `TypeVar`:** Reduces boilerplate and improves readability.
- **Scoping:** Type parameters are scoped only to the function or class where they are defined.
- **Auto-Variance:** Type checkers (like Mypy or Pyright) can now automatically infer if a type is covariant, contravariant, or invariant based on its usage.
- **Performance:** The new syntax is slightly more efficient as type parameters are evaluated lazily.

---

## 2. Modern Type Alias Syntax

Python 3.12 introduces the `type` keyword for creating type aliases. This replaces the old method of using simple assignments or the `TypeAlias` annotation.

### The `type` Keyword
The new syntax is clearer and supports generics naturally.

```python
# Simple Alias
type Point = tuple[float, float]

# Generic Alias
type Matrix[T] = list[list[T]]

# Usage
my_matrix: Matrix[int] = [[1, 2], [3, 4]]
```

### Lazy Evaluation
Type aliases created with the `type` statement are evaluated lazily. This means you can refer to types defined later in the same file without using string-based forward references.

```python
type Tree[T] = Node[T] | None  # Node is defined below!

class Node[T]:
    value: T
    left: Tree[T]
    right: Tree[T]
```

---

## 3. Protocols & Polymorphism

Python supports two main forms of subtyping: **Nominal** (inheritance-based) and **Structural** (interface-based).

### Structural Subtyping (`typing.Protocol`)
Introduced in PEP 544, `Protocol` allows for "static duck typing." A class is considered a subtype of a Protocol if it implements the required methods and attributes, even without explicit inheritance.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable  # Allows isinstance(obj, Drawable) at runtime
class Drawable(Protocol):
    def draw(self) -> None:
        ...

class Circle:  # No explicit inheritance from Drawable
    def draw(self) -> None:
        print("Drawing a circle")

def render(shape: Drawable):
    shape.draw()

render(Circle())  # This works!
```

### Nominal Subtyping (`abc.ABC`)
Nominal subtyping requires an explicit relationship through inheritance. This is the traditional OOP approach.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        ...

class Square(Shape):  # Must inherit to be considered a Shape
    def __init__(self, side: float):
        self.side = side
    
    def area(self) -> float:
        return self.side ** 2
```

### Comparison

| Feature | `Protocol` (Structural) | `ABC` (Nominal) |
| :--- | :--- | :--- |
| **Relationship** | Implicit (matches structure) | Explicit (inheritance) |
| **Use Case** | Interfaces for third-party code | Strict hierarchies & mixins |
| **Check** | Static (Mypy) / Runtime (with decorator) | Runtime (`isinstance`) |

---

## 4. Modern OOP & Dataclasses

`dataclasses` have become the standard way to write concise, data-oriented classes in Python. Python 3.10 and 3.12 added several powerful features.

### `kw_only=True`
Forces all fields in the dataclass to be passed as keyword arguments. This prevents errors with positional arguments, especially when a class has many fields or when fields are added in subclasses.

```python
from dataclasses import dataclass

@dataclass(kw_only=True)
class User:
    id: int
    username: str
    email: str

# This fails: user = User(1, "alice", "alice@example.com")
user = User(id=1, username="alice", email="alice@example.com")  # Correct
```

### `slots=True`
Using `slots` reduces the memory footprint of objects and speeds up attribute access by preventing the creation of a dynamic `__dict__`.

```python
@dataclass(slots=True)
class Point3D:
    x: float
    y: float
    z: float

p = Point3D(1.0, 2.0, 3.0)
# p.color = "red"  # This would raise AttributeError because of slots
```

### Comprehensive Example: Modern OOP with PEP 695
Combining generics, protocols, and dataclasses for a modern, type-safe architecture.

```python
from dataclasses import dataclass
from typing import Protocol

# 1. Define a Protocol for a storage engine
class Storage[T](Protocol):
    def save(self, item: T) -> None: ...
    def load(self, id: str) -> T: ...

# 2. Implement a concrete storage using a Dataclass
@dataclass(slots=True)
class MemoryStorage[T]:
    _data: dict[str, T]

    def save(self, item: T) -> None:
        # Simplified for example
        self._data[str(hash(item))] = item

    def load(self, id: str) -> T:
        return self._data[id]

# 3. Define a Generic Data Model
@dataclass(kw_only=True)
class Record[T]:
    payload: T
    version: int = 1

# 4. A generic function that works with the Protocol
def sync_record[T](storage: Storage[Record[T]], record: Record[T]):
    storage.save(record)
    print(f"Saved version {record.version}")

# Usage
store = MemoryStorage[Record[str]](_data={})
rec = Record(payload="Initial Data")
sync_record(store, rec)
```

---

## Summary of Python 3.12+ Changes
1.  **Generic Syntax:** `class MyClass[T]` and `def my_func[T]` replace `Generic` and `TypeVar`.
2.  **Type Alias:** `type MyAlias = ...` replaces `TypeAlias` annotation.
3.  **Efficiency:** PEP 695 introduces lazy evaluation for types, improving performance and solving circular/forward reference issues.
4.  **OOP Cleanliness:** `kw_only` and `slots` in dataclasses make code safer and more performant by default.
