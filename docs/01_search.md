# Basic Search

Searching is arguably the most important problem in Computer Science. In a very simplistic way, searching is at the core of critical applications like databases, and is the cornerstone of how the internet works.

However, beyond this simple, superficial view of searching as an end in itself, you can also view search as means for general-purpose problem solving. When you are, for example, playing chess, what your brain is doing is, in a very fundamental way, _searching_ for the optimal move--the only that most likely leads to winning.

In this sense, you can view almost all of Computer Science problems as search problems. In fact, a large part of this book will be devoted to search, in one way or another.

In this first chapter, we will look at the most explicit form of search: where we are explicitly given a set or collection of items, and asked to find one specific item.

We will start with the simplest, and most expensive kind of search, and progress towards increasingly more refined algorithms that exploit characteristics of the input items to minimize the time required to find the desired item, or determine if it's not there at all.

## Linear Search

Let's start by analyzing the simplest algorithm that does something non-trivial: linear search. Most of these algorithms work on the simplest data structure that we will see, the sequence.

A sequence (`Sequence` class) is an abstract data type that represents a collection of items with no inherent structure, other than each element has an index.

```python {export=src/codex/search/linear.py}
from typing import Sequence

```

Linear search is the most basic form of search. We have a sequence of elements, and we must determine whether one specific element is among them. Since we cannot assume anything at all from the sequence, our only option is to check them all.


::: {#lst-linear-search}
```python {export=src/codex/search/linear.py}
def find[T](x:T, items: Sequence[T]) -> bool:
    for y in items:
        if x == y:
            return True

    return False

```

**Linear Search:** Check every item in a sequence until a match is found or the collection is exhausted.

:::

Our first test will be a sanity check for simple cases:

```python {export=tests/search/test_linear.py}
from codex.search.linear import find

def test_simple_list():
    assert find(1, [1,2,3]) is True
    assert find(2, [1,2,3]) is True
    assert find(3, [1,2,3]) is True
    assert find(4, [1,2,3]) is False

```

### Analyzing Linear Search

Once we have an implementation, we must subject it to the three-step analysis established in our foundations.

#### Is it correct?

The property of **correctness** ensures that for any valid input, the algorithm produces the expected output. For linear search, we can verify this through three increasingly formal lenses:

- **The Exhaustive Argument**: Suppose an element $x$ exists in the sequence. By definition, there is some index $i$ such that `items[i] == x`. Since the algorithm performs an equality test over every single index in the sequence without exception, it is logically impossible to miss the item if it is there.

- **The Inductive Argument**: We can reason about the algorithm's correctness across different input sizes. For a sequence of length $0$, the loop never executes, and the algorithm correctly returns `False`. Assume the algorithm works for a sequence of length $n$. For a sequence of length $n+1$, the target $x$ is either in the first $n$ elements—where the inductive hypothesis ensures we find it—or it is the $n+1$-th element, which we check in the final iteration. If it is in neither, the algorithm correctly concludes it is not present.

- **The Loop Invariant**: We can define a formal invariant for the `for` loop: _At the start of iteration $i$, the element $x$ has not been found in the first $i-1$ elements of the sequence._ By the time the loop completes at iteration $n$, if the function hasn't returned `True`, we know with certainty that $x$ is not in the first $n$ elements, which constitutes the entire sequence.

#### How efficient is it?

We analyze linear search using the **RAM model**, assuming each comparison and iteration step has a unitary cost.

- **Time Complexity**: In the worst-case scenario (the item is at the very end or not present at all), we must perform $n$ comparisons for a sequence of size $n$. This gives us a growth rate of $O(n)$, or **linear time**.

- **Space Complexity**: The algorithm only requires a constant amount of extra memory to store the loop variable and the target, regardless of the input size, resulting in $O(1)$ **space complexity**.

#### Is it optimal?

Intuitively, linear search must be **optimal for unstructured data**. If we know _nothing_ about the order or distribution of the elements, we are mathematically forced to look at every single item at least once to be certain $x$ is not there. Any algorithm that skipped an element could be "fooled" if that specific element happened to be the one we were looking for. Thus, for a generic sequence, $O(n)$ is the best possible lower bound.

To prove this more formally, we employ an **adversarial argument**, a powerful technique in complexity theory where we imagine a game between our algorithm and a malicious adversary.

- **The Adversary’s Strategy**: Suppose an algorithm claims to find an element $x$ (or prove its absence) by examining fewer than $n$ elements—say, $n-1$ elements. The adversary waits for the algorithm to finish its $n-1$ checks.

- **The "Trap"**: Because there is one element the algorithm did not inspect, the adversary is free to define that specific element as $x$ if the algorithm concludes "False," or as something other than $x$ if the algorithm concludes "True" without having seen it.

- **The Conclusion**: Since the adversary can always change the unexamined element to make the algorithm’s answer wrong, any correct algorithm _must_ inspect every element in the worst case.

This proves that the lower bound for searching an unstructured sequence is $\Omega(n)$. Linear search, which operates in $O(n)$, meets this lower bound exactly, making it a **tightly optimal** solution for the problem as defined. Unless we possess more information about the data's structure—the central theme of the next chapter—we simply cannot do better.

## Indexing and Counting

The `find` method is good to know if an element exists in a sequence, but it doesn't tell us _where_. We can easily extend it to return an _index_. We thus define the `index` method, with the following condition: if `index(x,l) == i` then `l[i] == x`. That is, `index` returns the **first** index where we can find a given element `x`.

::: {#lst-linear-index}

```python {export=src/codex/search/linear.py}
def index[T](x: T, items: Sequence[T]) -> int | None:
    for i,y in enumerate(items):
        if x == y:
            return i

    return None

```
**Linear Index:** Check every item until found, and return the corresponding index, or `None`.

:::

When the item is not present in the sequence, we return `None`. We could raise an exception instead, but that would force a lot of defensive programming.

Let's write some tests!

```python {export=tests/search/test_linear.py}
from codex.search.linear import index

def test_index():
    assert index(1, [1,2,3]) == 0
    assert index(2, [1,2,3]) == 1
    assert index(3, [1,2,3]) == 2
    assert index(4, [1,2,3]) is None

```
As a final step in the linear search paradigm, let's consider the problem of finding not the first, but _all_ occurrences of a given item. We'll call this function `count`. It will return the number of occurrences of some item `x` in a sequence.

::: {#lst-linear-count}

```python {export=src/codex/search/linear.py}
def count[T](x: T, items: Sequence[T]) -> int:
    c = 0

    for y in items:
        if x == y:
            c += 1

    return c

```

**Linear Count:** Check all items equal to the input and count them.

:::

Let's write some simple tests for this method.

```python {export=tests/search/test_linear.py}
from codex.search.linear import count

def test_index():
    assert count(1, [1,2,3]) == 1
    assert count(2, [1,2,2]) == 2
    assert count(4, [1,2,3]) == 0

```

### Analysis

We won't dwell too much in this section since the analysis is very similar to linear search--these are just specialized versions of it. Once more, we have $O(n)$ algorithms (with $O(1)$ memory cost) for a problem that is provable $\Omega(n)$. Thus, given our assumptions (that there is no intrinsic structure to the elements order), we have optimal algorithms.

## Min and Max

Let's now move to a slightly different problem. Instead of finding one specific element, we want to find the element that ranks minimum or maximum. Consider a sequence of numbers in an arbitrary order. We define the minimum (maximum) element as the element `x` such as `x <= y` (`x >= y`) for all `y` in the sequence.

Now, instead of numbers, consider some arbitrary total ordering function `f`, such that `f(x,y) <= 0` if and only if `x <= y`. This allows us to extend the notion of minimum and maximum to arbitrary data types.

Let's formalize this notion as a Python type alias. We will define an `Ordering` as a function that has this signature:

```python {export=src/codex/types.py}
from typing import Callable

type Ordering[T] = Callable[[T,T], int]

```

Now, to make things simple for the simplest cases, let's define a default ordering function that just delegates to the items own `<=` implementation. This way we don't have to reinvent the wheel with numbers, strings, and all other natively comparable items.

```python {export=src/codex/types.py}
def default_order(x, y):
    if x < y:
        return -1
    elif x == y:
        return 0
    else:
        return 1

```

Let's write the `minimum` method using this convention. Since we have no knowledge of the structure of the sequence other than it supports partial ordering, we have to test all possible items, like before. But now, instead of returning as soon as we find the correct item, we simply store the minimum item we've seen so far, and return at the end of the `for` loop. This guarantees we have seen all the items, and thus the minimum among them must be the one we have marked.

```python {export=src/codex/search/linear.py}
from codex.types import Ordering, default_order

def minimum[T](items: Sequence[T], f: Ordering[T] = default_order) -> T:
    m = items[0]

    for x in items:
        if f(x,m) <= 0:
            m = x

    return m

```

The `minimum` method can fail only if the `items` sequence is empty. In the same manner, we can implement `maximum`. But instead of coding another method with the same functionality, which is not very DRY, we can leverage the fact that we are passing an ordering function that we can manipulate.

Consider an arbitrary ordering function `f` such `f(x,y) <= 0`. This means by definition that `x <= y`. Now we want to define another function `g` such that `g(y,x) <= 0`, that is, it _inverts_ the result of `f`. We can do this very simply by swaping the inputs in `f`.

```python {export=src/codex/search/linear.py}
def maximum[T](items: Sequence[T], f: Ordering[T] = default_order) -> T:
    return minimum(items, lambda x,y: f(y,x))

```

We can easily code a couple of test methods for this new functionality.

```python {export=tests/search/test_linear.py}
from codex.search.linear import minimum, maximum

def test_minmax():
    items = [4,2,6,5,7,1,0]

    assert minimum(items) == 0
    assert maximum(items) == 7
```

The correctness, cost, and optimality analysis is very similar in these cases as well.

## Conclusion

Linear search is a powerful paradigm precisely because it is universal. Whether we are checking for the existence of an item, finding its index, or identifying the minimum or maximum element in a collection, the exhaustive approach provides absolute certainty. No matter the nature of the data, if we test every single element and skim through every possibility, the problem will be solved.

The primary drawback of this certainty is the cost: some search spaces are simply too vast to be traversed one item at a time. To achieve better performance, we must move beyond the assumption of an unstructured sequence. We need to know more about the search space and impose some level of structure.

In the next chapter, we will explore the most straightforward structure we can impose: order. We will see how knowing the relative position of items allows us to implement what is arguably the most efficient and beautiful algorithm ever designed.
