# Python 3.12+ Foundational Syntax & Control Flow

This document provides a comprehensive overview of the foundational syntax and basic control flow in Python 3.12+. It focuses on modern best practices, including improvements introduced in recent versions such as PEP 701 (f-strings) and PEP 695 (type parameter syntax).

---

## 1. Basic Syntax

### Variable Naming
Python uses **snake_case** for variable and function names (consistent with [PEP 8](https://peps.python.org/pep-0008/)).
- **Case-sensitive:** `my_var` and `My_Var` are different variables.
- **Allowed characters:** Letters (a-z, A-Z), underscores (`_`), and numbers (0-9), but cannot start with a number.
- **Reserved words:** Avoid using Python keywords like `if`, `def`, `class`, `import`, etc.

### Comments
- **Single-line:** Use the hash symbol (`#`).
- **Docstrings:** Use triple quotes (`"""`) for multi-line documentation at the start of modules, classes, or functions.

```python
# This is a single-line comment
x = 42  # Inline comment

"""
This is a docstring.
It is used to document the purpose of a block of code.
"""
```

### Primitive Types
Python 3.12 handles four main primitive types:

1.  **`int` (Integer):** Whole numbers. Python integers have arbitrary precision (limited only by memory).
2.  **`float` (Floating Point):** Decimal numbers. These follow the IEEE 754 double-precision standard.
3.  **`str` (String):** Sequence of Unicode characters.
    - **F-Strings (3.12 Update):** PEP 701 lifted previous restrictions. You can now:
        - Reuse quotes: `f"User: {data["name"]}"` is now valid.
        - Include backslashes: `f"Newline: {"\n"}"`.
        - Use multi-line expressions and comments inside `{}`.
4.  **`bool` (Boolean):** Represents `True` or `False`.

```python
age: int = 25
price: float = 19.99
name: str = "Alice"
is_active: bool = True

# Python 3.12 F-string power
message = f"Hello {name.upper()}, " \
          f"your age is {age} " \
          f"and your status is {"Active" if is_active else "Inactive"}"
```

---

## 2. Control Flow

### Conditional Statements
Python uses `if`, `elif`, and `else` for branching. 
- **Truthiness:** Empty collections (`[]`, `{}`), `0`, `0.0`, `None`, and `False` evaluate to `False`. Everything else is typically `True`.

```python
score = 85

if score >= 90:
    print("Grade: A")
elif score >= 80:
    print("Grade: B")
else:
    print("Grade: C")
```

#### Structural Pattern Matching (Python 3.10+)
For more complex branching based on the structure of data, Python provides the `match` statement.

```python
status = 404
match status:
    case 200:
        print("Success")
    case 404:
        print("Not Found")
    case _:
        print("Unknown Status")
```

### Loops
#### `for` loops
Used to iterate over any iterable (lists, strings, ranges).
- **`range(stop)`**: Generates a sequence from `0` to `stop-1`.
- **`enumerate(iterable)`**: Returns both the index and the value.

```python
# Basic for loop
for i in range(3):
    print(f"Iteration {i}")

# enumerate for index-value pairs
fruits = ["apple", "banana", "cherry"]
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
```

#### `while` loops
Repeats as long as a condition is `True`.
- **`break`**: Exits the loop immediately.
- **`continue`**: Skips the rest of the current iteration.

```python
count = 0
while count < 5:
    if count == 3:
        break  # Stops the loop when count is 3
    print(count)
    count += 1
```

---

## 3. Collections

### Lists
Ordered, mutable sequences.
- **Slicing:** `my_list[start:stop:step]`
    - `start`: inclusive index.
    - `stop`: exclusive index.
    - `step`: interval (can be negative to reverse).

```python
nums = [0, 1, 2, 3, 4, 5]
print(nums[1:4])    # [1, 2, 3]
print(nums[::-1])   # [5, 4, 3, 2, 1, 0] (Reversed)

# Key Methods
nums.append(6)      # Adds to end
nums.extend([7, 8]) # Merges another list
nums.pop()          # Removes and returns last item
nums.sort()         # Sorts in-place
```

### Dictionaries
Unordered (insertion order preserved since 3.7) mappings of unique keys to values.
- **Key Methods:**
    - `.get(key, default)`: Safely access values without raising `KeyError`.
    - `.keys()`, `.values()`, `.items()`: Views of the dictionary data.
    - `|` and `|=` (3.9+): Union operators for merging dictionaries.

```python
user = {"name": "Bob", "role": "Admin"}

# Safe access
role = user.get("role", "Guest")

# Merging (Modern)
defaults = {"theme": "light", "role": "Guest"}
settings = defaults | user  # user values override defaults
```

---

## 4. Basic Functions

Functions are defined using the `def` keyword. Python 3.12 encourages the use of type hints for clarity and tooling support.

### Parameters and Arguments
1.  **Positional Arguments:** Matched by order.
2.  **Keyword Arguments:** Matched by name.
3.  **Default Values:** Parameters can have pre-assigned values.

```python
def greet(name: str, greeting: str = "Hello") -> str:
    """Returns a greeting message."""
    return f"{greeting}, {name}!"

# Call using positional and keyword arguments
print(greet("Alice"))               # Hello, Alice!
print(greet("Bob", greeting="Hi"))  # Hi, Bob!
```

### Python 3.12 Generics (PEP 695)
Python 3.12 introduced a simpler syntax for generic functions using square brackets `[]`.

```python
# A generic function that works with a list of any type 'T'
def get_first[T](items: list[T]) -> T:
    return items[0]

first_int = get_first([1, 2, 3])      # Infers T as int
first_str = get_first(["a", "b"])     # Infers T as str
```

### Return Values
If no `return` statement is reached, the function returns `None`. You can return multiple values as a tuple.

```python
def get_stats(numbers: list[int]) -> tuple[int, int]:
    return min(numbers), max(numbers)

minimum, maximum = get_stats([10, 20, 30])
```
