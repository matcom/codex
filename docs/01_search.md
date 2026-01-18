# Search

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

```python {export=src/codex/search/linear.py}
def find[T](x:T, items: Sequence[T]) -> bool:
    for y in items:
        if x == y:
            return True

    return False

```
Our first test will be a sanity check for simple cases:

```python {export=tests/search/test_linear.py}
from codex.search.linear import find

def test_simple_list():
    assert find(1, [1,2,3]) is True
    assert find(2, [1,2,3]) is True
    assert find(3, [1,2,3]) is True
    assert find(4, [1,2,3]) is False

```

The `find` method is good to know if an element exists in a sequence, but it doesn't tell us _where_. We can easily extend it to return an _index_. We thus define the `index` method, with the following condition: if `index(x,l) == i` then `l[i] == x`. That is, `index` returns the **first** index where we can find a given element `x`.

```python {export=src/codex/search/linear.py}
def index[T](x: T, items: Sequence[T]) -> int | None:
    for i,y in enumerate(items):
        if x == y:
            return i

    return None

```

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

```python {export=src/codex/search/linear.py}
def count[T](x: T, items: Sequence[T]) -> int:
    c = 0

    for y in items:
        if x == y:
            c += 1

    return c

```

Let's write some simple tests for this method.

```python {export=tests/search/test_linear.py}
from codex.search.linear import count

def test_index():
    assert count(1, [1,2,3]) == 1
    assert count(2, [1,2,2]) == 2
    assert count(4, [1,2,3]) == 0

```

## Min and Max

Let's now move to a slightly different problem. Instead of finding one specific element, we want to find the element that ranks minimum or maximum. Consider a sequence of numbers in an arbitrary order. We define the minimum (maximum) element as the element `x` such as `x <= y` (`x >= y`) for all `y` in the sequence.

Now, instead of numbers, consider some arbitrary total ordering function `f`, such that `f(x,y) <= 0` if and only if `x <= y`. This allows us to extend the notion of minimum and maximum to arbitrary data types.

Let's formalize this notion as a Python type alias. We will define an `Ordering` as a function that has this signature:

```python {export=src/codex/types.py}
from typing import Callable

type Ordering[T] = Callable[[T,T], int]

```

Let's write the `minimum` method using this convention. Since we have no knowledge of the structure of the sequence other than it supports partial ordering, we have to test all possible items, like before. But now, instead of returning as soon as we find the "correcOf course, we t" item, we simply store the minimum item we've seen so far, and return at the end of the `for` loop. This guarantees we have seen all the items, and thus the minimum among them must be the one we have marked.

```python {export=src/codex/search/linear.py}
from codex.types import Ordering

def minimum[T](items: Sequence[T], f: Ordering[T]) -> T:
    m = None

    for x in items:
        if m is None or f(x,m) <= 0:
            m = x

    return m

```

The `minimum` method can fail only if the `items` sequence is empty. In the same manner, we can implement `maximum`. But instead of coding another method with the same functionality, which is not very DRY, we can leverage the fact that we are passing an ordering function that we can manipulate.

Consider an arbitrary ordering function `f` such `f(x,y) <= 0`. This means by definition that `x <= y`. Now we want to define another function `g` such that `g(y,x) <= 0`, that is, it _inverts_ the result of `f`. We can do this very simply by swaping the inputs in `f`.

```python {export=src/codex/search/linear.py}
def maximum[T](items: Sequence[T], f: Ordering[T]) -> T:
    return minimum(items, lambda x,y: f(y,x))

```

We can easily code a couple of test methods for this new functionality.

```python {export=tests/search/test_linear.py}
from codex.search.linear import minimum, maximum

def test_minmax():
    items = [4,2,6,5,7,1,0]

    assert minimum(items, lambda x,y: x-y) == 0
    assert maximum(items, lambda x,y: y-x) == 0
```

## Binary Search

Now that we have started considering ordered sets, we can introduce what is arguably the most beautiful algorithm in the history of Computer Science: binary search. A quintessential algorithm that shows how a well-structured search space is exponentially easier to search than an arbitrary one.

To build some intuition for binary search, let's consider we have an _ordered_ sequence of items; that is, we always have that if `i < j`, then `l[i] <= l[j]`. This simple constraint introduces a very powerful condition in our search problem: if we are looking for `x`, and `x < y`, then we know no item after `y` in the sequence can be `x`.

Convince yourself of this simple truth before moving on.

This fundamentally changes how fast we can search. Why? Because now every test that we perform--every time we ask whether `x < y` for some `y`--we gain _a lot_ of information, not only about `y`, but about _every other item greater or equal than `y`_.

This is the magical leap we always need in order to write a fast algorithm--fast as in, it doesn't need to check _every single thing_. We need a way to gather more information from every operation, so we have to do less operations. Let's see how we can leverage this powerful intuition to make search not only faster, but _exponentially faster_ when items are ordered.

Consider the set of items $x_1, ..., y, ..., x_n$. We are searching for item $x$, and we choose to test whether $x \leq y$. We have two choices, either $x \leq y$, or, on the contrary, $x > y$. We want to gain the maximum amount of information in either case. The question is, how should we pick $y$?

If we pick $y$ too close to either end, we can get lucky and cross off a large number of items. For example if $y$ is in the last 5% of the sequence, and it turns out $x > y$, we have just removed the first 95% of the sequence without looking at it! But of course, we won't get _that_ lucky too often. In fact, if $x$ is a random input, it could potentially be anywhere in the sequence. Under the fairly mild assumption that $x$ should be uniformly distributed among all indices in the sequences, we will get _this_ lucky exactly 5% of the time. The other 95! we have almost as much work to do as in the beginning.

It should be obvious by now that the best way to pick $y$ either case is to choose the middle of the sequence. In that way I always cross off 50% of the items, regardless of luck. This is good, we just removed a huge chunk. But it gets even better.

Now, instead of looking for $x$ linearly in the remaining 50% of the items, we do the exact same thing again! We take the middle point of the current half, and now we can cross off another 25% of the items. If we keep repeating this over and over, how fast will we be left with just one item? Keep that thought in mind.

Before doing the math, here is the most straightforward implemenation of binary search. We will use two indices, `l(eft)` and `r(ight)` to keep track of the current sub-sequence we are analyzing. As long as `l <= r` there is at least one item left to test. Once `l > r`, we must conclude `x` is not in the sequence.

Here goes the code.

```python {export=src/codex/search/binary.py}
from typing import Sequence
from codex.types import Ordering

def binary_search[T](x:T, items:Sequence[T], f: Ordering[T]) -> int | None:
    l, r = 0, len(items)-1

    while l <= r:
        m = (l+r)//2

        if items[m] == x:
            return m
        elif x < items[m]:
            r = m - 1
        else:
            l = m + 1

    return None

```

Here is a minimal test.

```python {export=tests/search/test_binary.py}
from codex.search.binary import binary_search

def test_binary_search():
    items = [0,1,2,3,4,5,6,7,8,9]

    assert binary_search(3, items, lambda x,y: x-y) == 3
    assert binary_search(10, items, lambda x,y: x-y) is None

```