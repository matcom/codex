# Linear Time Sorting

This chapter concludes our exploration of sorting by demonstrating that the  limit we established is not a universal law, but a specific constraint of **comparison-based algorithms**. If we possess even deeper knowledge about the structure of our data—specifically that it consists of discrete values within a known range—we can bypass comparisons entirely and achieve true linear time performance.

In the previous chapters, we operated under the assumption that the only way to gain information about our items was to compare them. However, when our data has a predictable, bounded structure, we can use the values themselves as **indices**. This shifts the problem from "which is bigger?" to "how many of each value do we have?".

## Counting Sort

**Counting Sort** is the purest expression of this idea. If we know that every element in a sequence is an integer in the range , we can simply count the occurrences of each integer. By calculating the cumulative sum of these counts, we determine the exact position each element should occupy in the final sorted array.

```python {export=src/codex/sort/linear.py}
from typing import MutableSequence, Callable, List
from codex.types import Ordering, default_order

def counting_sort(
    items: MutableSequence[int], k: int
) -> List[int]:
    """
    Sorts a sequence of integers in the range [0, k].
    This implementation is stable.
    """
    counts = [0] * (k + 1)
    for x in items:
        counts[x] += 1

    # Transform counts into starting indices
    for i in range(1, k + 1):
        counts[i] += counts[i - 1]

    output = [0] * len(items)
    # Iterate backwards to maintain stability
    for x in reversed(items):
        counts[x] -= 1
        output[counts[x]] = x

    return output

```

Counting Sort performs exactly two passes over the input and one pass over the range $O(k)$. This results in a time complexity of $O(n \times k)$. When $k = O(n)$, the algorithm is strictly linear. The cost, however, is **space complexity**: we require an auxiliary array of size $k$. If $k$ is significantly larger than $n$, this becomes impractical.

## Radix Sort: Sorting by Digits

To handle larger ranges without massive memory overhead, we use **Radix Sort**. The intuition here is to view each number (or string) as a sequence of "digits." We sort the collection multiple times, once for each digit position, starting from the **least significant digit** (LSD).

Crucially, each pass must be a **stable sort**. By using Counting Sort as the stable subroutine for each digit, we can sort numbers in any range  by breaking them into  digits.

```python {export=src/codex/sort/linear.py}
def radix_sort(items: MutableSequence[int], base: int = 10) -> List[int]:
    if not items:
        return items

    max_val = max(items)
    exp = 1
    output = list(items)

    while max_val // exp > 0:
        output = _counting_sort_by_digit(output, exp, base)
        exp *= base

    return output

def _counting_sort_by_digit(items: List[int], exp: int, base: int) -> List[int]:
    counts = [0] * base
    for x in items:
        digit = (x // exp) % base
        counts[digit] += 1

    for i in range(1, base):
        counts[i] += counts[i - 1]

    res = [0] * len(items)
    for x in reversed(items):
        digit = (x // exp) % base
        counts[digit] -= 1
        res[counts[digit]] = x
    return res

```

Radix Sort runs in $O(d(n+k)) time, where $d$ is the number of digits and $k$ is the base. Because $d$ is constant for a fixed word size (e.g., 32-bit or 64-bit integers), the algorithm remains linear relative to $n$. This is the preferred method for sorting large sets of integers or fixed-length strings where memory is constrained compared to the range of values.

## Verification

We verify these linear approaches by testing them against various integer ranges and sequences.

```python {export=tests/sort/test_linear_sort.py}
import pytest
from codex.sort.linear import counting_sort, radix_sort

def test_counting_sort():
    items = [4, 1, 3, 4, 3]
    # Range is [0, 4]
    assert counting_sort(items, 4) == [1, 3, 3, 4, 4]

def test_radix_sort():
    items = [170, 45, 75, 90, 802, 24, 2, 66]
    expected = [2, 24, 45, 66, 75, 90, 170, 802]
    assert radix_sort(items) == expected

```
