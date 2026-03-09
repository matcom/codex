# Python 3.12+ Intermediate Data Structures & Modern Control Flow

This document explores intermediate concepts in Python 3.12+, focusing on data structures, the evolution of f-strings, and advanced control flow mechanisms like structural pattern matching and modern error handling.

---

## 1. Tuples and Sets: Immutability vs. Uniqueness

### Tuples: The Immutable Record
Tuples are ordered, immutable sequences. In modern Python, they are idiomatic for representing "records" where position implies meaning.

- **Immutability:** Once created, elements cannot be added, removed, or changed. This makes them hashable (if their contents are hashable), allowing them to be used as dictionary keys.
- **Packing/Unpacking:** Tuples excel at returning multiple values and swapping variables.
- **Performance:** Tuples are more memory-efficient and faster to create than lists.

```python
# Idiomatic record
point = (10, 20)
x, y = point  # Unpacking

# Tuples as dictionary keys
locations = {
    (40.7128, -74.0060): "New York",
    (34.0522, -118.2437): "Los Angeles"
}
```

### Sets: The Unique Collection
Sets are unordered collections of unique, hashable elements. They are essentially hash tables without values.

- **Uniqueness:** Adding a duplicate element has no effect.
- **Performance:** Membership testing (`in`) is $O(1)$, making sets far superior to lists/tuples for large-scale existence checks.
- **Set Operations:**
    - **Union (`|` or `.union()`):** Elements in either set.
    - **Intersection (`&` or `.intersection()`):** Elements in both sets.
    - **Difference (`-` or `.difference()`):** Elements in the first but not the second.
    - **Symmetric Difference (`^` or `.symmetric_difference()`):** Elements in one or the other, but not both.

```python
administrators = {"alice", "bob"}
developers = {"bob", "charlie", "david"}

# Union: Everyone
all_staff = administrators | developers  # {"alice", "bob", "charlie", "david"}

# Intersection: Admin developers
leads = administrators & developers  # {"bob"}

# Difference: Admins who don't develop
pure_admins = administrators - developers  # {"alice"}
```

---

## 2. Structural Pattern Matching (PEP 634/636)

Introduced in 3.10 and refined since, `match/case` is not just a `switch` statement; it is a powerful **destructuring** tool.

### Literals and Wildcards
The underscore `_` acts as a wildcard that matches anything but does not bind the value.

```python
match status_code:
    case 200:
        print("Success")
    case 404:
        print("Not Found")
    case 500 | 501 | 502:  # Combined patterns
        print("Server Error")
    case _:
        print("Unknown Status")
```

### Sequence and Mapping Patterns
You can match the internal structure of lists, tuples, and dictionaries.

```python
def process_command(cmd):
    match cmd.split():
        case ["quit"]:
            exit()
        case ["load", filename]:
            print(f"Loading {filename}")
        case ["move", x, y] if int(x) > 0:  # With Guard
            print(f"Moving to {x}, {y}")
        case ["move", *rest]:
            print(f"Invalid move arguments: {rest}")

# Dictionary matching (matches if keys are present)
match user_data:
    case {"name": name, "role": "admin"}:
        print(f"Welcome Admin {name}")
    case {"name": name}:
        print(f"Welcome User {name}")
```

### Class Patterns and `__match_args__`
You can match against class instances. By defining `__match_args__`, you enable positional matching.

```python
class Point:
    __match_args__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y

def locate(point):
    match point:
        case Point(0, 0):
            print("Origin")
        case Point(x, 0):
            print(f"X-axis at {x}")
        case Point(0, y):
            print(f"Y-axis at {y}")
        case Point(x, y) as p:
            print(f"Point at {x}, {y}")
```

---

## 3. Modern Strings: Python 3.12 F-strings (PEP 701)

Python 3.12 completely overhauled f-strings by integrating them into the formal grammar, removing several legacy restrictions.

### Quote Reuse
You can now use the same quotes for the expression as the f-string itself.

```python
# Valid in 3.12+
songs = ["Hallowed Be Thy Name", "The Trooper"]
print(f"Songs: {", ".join(songs)}") 
```

### Backslashes and Escape Sequences
Backslashes are now permitted within expressions inside `{}`.

```python
# Valid in 3.12+
words = ["apple", "banana"]
print(f"List:\n{"\n".join(words)}")
```

### Multiline Expressions and Comments
Expressions within f-strings can now span multiple lines and include comments.

```python
# Valid in 3.12+
print(f"Result: {
    10 + 20 # Add the base
    + 30    # Add the bonus
}")
```

---

## 4. Modern Error Handling

### Exception Groups (3.11+)
`ExceptionGroup` allows raising multiple unrelated exceptions simultaneously. This is particularly useful in concurrent programming.

```python
def fetch_data():
    raise ExceptionGroup("Batch failed", [
        ValueError("Invalid format"),
        ConnectionError("Network timeout")
    ])
```

### The `except*` Syntax
To handle specific exceptions within a group, use `except*`. Note that `except*` cannot be mixed with traditional `except` in the same `try` block.

```python
try:
    fetch_data()
except* ValueError as eg:
    for e in eg.exceptions:
        print(f"Handled Value Error: {e}")
except* ConnectionError as eg:
    print(f"Handled Connection Error")
```

### Contextualizing Errors with `add_note()`
Python 3.11 introduced `add_note()`, allowing you to enrich exceptions with context without modifying the error message or wrapping the exception.

```python
try:
    process_transaction(tx_id)
except Exception as e:
    e.add_note(f"Failure occurred during transaction: {tx_id}")
    raise
```

### Best Practices
1. **Specific Exceptions:** Always catch the most specific exception possible.
2. **Clean Cleanup:** Use `finally` for resource cleanup (closing files, releasing locks).
3. **Custom Exceptions:** Inherit from `Exception` for domain-specific errors to improve API clarity.

```python
class InsufficientFundsError(Exception):
    """Raised when an account balance is too low."""
    pass

def withdraw(amount):
    if amount > balance:
        raise InsufficientFundsError(f"Attempted to withdraw {amount} with balance {balance}")
```
