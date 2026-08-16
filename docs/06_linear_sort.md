# Looking inside the elements

Every sorting algorithm in Part I has been working in the **comparison model** — the algorithm's only access to the data is to ask, of any two elements, *which one is smaller?* Bubble sort doesn't look at the bits of an integer; merge sort doesn't peek at the characters of a string; quickselect doesn't care whether you're sorting numbers or names. The elements have been opaque boxes that the algorithm can hold up next to each other and nothing more.

That assumption — opacity — is what locks comparison-based sorting at $\Omega(n \log n)$. The decision-tree lower bound from chapter 4 was a statement about the comparison model: with only $\log_2(n!)$ leaves reachable per level of the tree, you can't get to the right answer in fewer comparisons. But it wasn't a statement about *sorting itself*. It was a statement about *sorting under the constraint that all you can do is compare*.

Drop that constraint and the bound goes away.

Two algorithms sort in **linear time** — $O(n)$, beating the comparison lower bound by a factor of $\log n$ — and the price they pay is explicit. Both only work when you can look *inside* the elements, treating each one not as an opaque value to be compared but as a structured thing with intrinsic properties. A magnitude that maps directly to a position in memory. A sequence of digits, each in a bounded range. A fixed-width representation. The lower-bound argument doesn't apply because these algorithms aren't comparison-based; they're *structure-based*. Different model, different bound.

**The value is the address.** Counting sort takes an integer $x$ and uses it as the index into a counting array — no comparison, just a direct memory lookup. Radix sort decomposes an integer into digits and sorts by each digit position in turn. In both cases the algorithm reads the element's intrinsic structure rather than its comparative position relative to other elements. That single reframing — *from comparing to looking inside* — is the move that breaks the $n \log n$ ceiling.

## Counting sort: the value is the address

The simplest exploit. Suppose every element of `items` is a non-negative integer in the range $[0, k]$. Then you can sort the array by *counting how many of each value there are* and reading them back out in order.

There are three phases. **Histogram**: walk the input once and count occurrences of each value. **Prefix sum**: turn the histogram into a cumulative count, so `counts[i]` tells you how many elements are $\leq i$ — which is exactly the position-just-past-the-last-$i$ in the sorted output. **Placement**: walk the input *in reverse*, and for each element, the decremented prefix sum gives its destination index.

```python {export=src/codex/sort/counting.py}
from typing import Sequence


def counting_sort(items: Sequence[int], k: int) -> list[int]:
    """Sort a sequence of integers in [0, k] in O(n + k) time. Stable."""
    counts = [0] * (k + 1)
    for x in items:
        counts[x] += 1

    # Prefix sums: counts[i] becomes the number of elements <= i.
    for i in range(1, k + 1):
        counts[i] += counts[i - 1]

    # Place each element, walking the input in reverse to preserve stability.
    output = [0] * len(items)
    for x in reversed(items):
        counts[x] -= 1
        output[counts[x]] = x

    return output
```

The whole algorithm is three passes, and not one of them involves a single comparison between two input elements. The histogram pass increments `counts[x]` for each `x`; the prefix-sum pass turns counts into cumulative counts; the placement pass reads the cumulative counts as destination indices. Each pass is $O(n)$ (the histogram and placement) or $O(k)$ (the prefix sum). Total: $O(n + k)$.

```python
from codex.sort.counting import counting_sort

print(counting_sort([3, 1, 4, 1, 5, 9, 2, 6], k=9))  # [1, 1, 2, 3, 4, 5, 6, 9]
print(counting_sort([0, 0, 0], k=0))                  # [0, 0, 0] — duplicates fine
print(counting_sort([], k=10))                        # [] — empty input fine
```

**The reverse walk.** The third loop walks `items` in reverse, not forward, and that's not a stylistic choice — it's what makes counting sort **stable**. Stability means equal elements preserve their relative order from input to output. With the reverse walk, the last copy of value $v$ in the input gets placed at the rightmost slot reserved for $v$ in the output, and earlier copies fill the slots to the left of that. Walking forward instead would *reverse* the relative order of equal elements. Stability is going to be essential to radix sort, so the reverse-walk detail isn't cosmetic.

**The $k$ in $O(n + k)$.** If $k$ is roughly the size of $n$ — say, sorting integers in $[0, n]$ — then the algorithm is genuinely linear. If $k$ is enormous — say, sorting 32-bit integers where $k = 2^{32}$ — then counting sort allocates a four-billion-entry array and pays $O(k)$ for the prefix-sum pass, which destroys any practical benefit. Counting sort wins decisively when the value range is small and collapses to uselessness when it isn't. The next algorithm fixes that.

## Radix sort: one digit at a time

What if your integers are large but their *digits* are bounded? A 32-bit integer can take any of $2^{32}$ values, but each of its ten decimal digits is in $[0, 9]$. Each of its 32 binary digits is in $[0, 1]$. Each of its four bytes is in $[0, 255]$. Counting sort is useless on the integers themselves, but it's perfectly suited to sorting by a single digit.

Radix sort is the natural construction: sort by the lowest-order digit, then by the next-lowest, and so on up to the highest. The variant I'll show is **LSD** (least significant digit first), which is the one that's easiest to analyze. After all digit positions are processed, the array is sorted by the full value.

```python {export=src/codex/sort/radix.py}
from typing import Sequence


def radix_sort(items: Sequence[int], base: int = 10) -> list[int]:
    """Sort non-negative integers in O(d * (n + base)) time.

    d = number of digits in the largest element when written in the given base.
    LSD (least significant digit first).
    """
    if not items:
        return []

    items = list(items)
    max_val = max(items)

    digit_place = 1  # ones, then base, then base^2, ...
    while max_val // digit_place > 0:
        items = _counting_sort_by_digit(items, digit_place, base)
        digit_place *= base

    return items
```

The driver loop figures out how many digits the largest element has and runs one stable counting sort per digit position. The per-digit pass is just counting sort applied to a digit-extracting key instead of the value itself:

```python {export=src/codex/sort/radix.py}
def _counting_sort_by_digit(
    items: list[int], digit_place: int, base: int
) -> list[int]:
    """One stable pass: sort by (x // digit_place) % base."""
    counts = [0] * base
    for x in items:
        counts[(x // digit_place) % base] += 1

    for i in range(1, base):
        counts[i] += counts[i - 1]

    output = [0] * len(items)
    for x in reversed(items):
        d = (x // digit_place) % base
        counts[d] -= 1
        output[counts[d]] = x

    return output
```

The shape is identical to plain counting sort. The only change is the "key" the algorithm uses: instead of `x`, it uses `(x // digit_place) % base`, which extracts one specific digit out of `x`.

```python
from codex.sort.radix import radix_sort

print(radix_sort([170, 45, 75, 90, 802, 24, 2, 66]))   # [2, 24, 45, 66, 75, 90, 170, 802]
print(radix_sort([1234, 56, 7, 89, 3210]))             # [7, 56, 89, 1234, 3210]
print(radix_sort([12, 11, 22, 21]))                    # [11, 12, 21, 22]

# Different base, same result — base only affects the constant factor
print(radix_sort([170, 45, 75, 90, 802, 24, 2, 66], base=2))
```

Why does LSD radix sort work? It's not obvious that sorting by the *least* significant digit first should lead anywhere useful — the lowest digit is the least important position, intuitively. The answer is in the stability.

After the first pass, the array is sorted by ones digit. Elements with ones-digit 4 are clustered together, in some order. After the second pass, the array is sorted by tens digit *while preserving the relative order from the previous pass* — because counting sort is stable. So within the cluster of tens-digit-7 elements, the ones-digit order from the first pass is preserved. By induction, after $j$ passes the array is sorted by the bottom $j$ digits of each value. After all $d$ passes, it's sorted by the full value.

Stability is what makes radix sort work at all. Without it, each pass would scramble the order established by the previous one, and the whole construction would collapse.

What's the practical cost? Each pass is $O(n + b)$, where $b$ is the base. There are $d$ passes, where $d$ is the number of digits in the largest value (which is $\log_b(\text{max\_val})$). Total: $O(d(n + b)) = O((n + b) \log_b(\text{max\_val}))$. For fixed-width integers (say, 32-bit), $d$ is bounded by a constant — at most 32 if you sort one bit at a time, at most 4 if you sort one byte at a time. Pick base 256 and you get **4 passes for 32-bit integers, 8 passes for 64-bit**, each running in $O(n + 256) = O(n)$ — genuinely linear in practice. That's the choice production radix sort implementations make.

## The three questions, applied

### Is it correct?

**Counting sort** is correct because the prefix sums tell you, for each value $v$, exactly which positions in the output should be filled with copies of $v$. After phase 2, `counts[i]` equals the number of input elements with value $\leq i$ — which is the position-just-past-the-last-$i$. The reverse-walk placement then fills those positions from the right inward, one element at a time, and the decrement before placement ensures the next copy of $v$ lands one slot earlier. Inductively, every input element ends up at its correct position in the sorted output.

**Radix sort** is correct by induction on the number of digits processed. After $j$ passes (least significant first), the array is sorted by the values' last $j$ digits — that is, by their value modulo $\text{base}^j$. The $(j+1)$-th pass is a stable sort by digit $j+1$, which extends the sortedness to the last $j+1$ digits without disturbing the lower-digit order from previous passes. After all $d$ passes, the array is sorted by the full value.

The stability of the per-digit sort is the crux of the inductive argument: if any pass scrambled equal-digit elements, the inductive step would fail. Stability isn't an aesthetic property of counting sort — it's the property that lets radix sort exist.

### How efficient is it?

**Counting sort** runs in $O(n + k)$ time and $O(n + k)$ space — the counts array is $O(k)$, the output array is $O(n)$. When $k$ is at most a constant multiple of $n$, the algorithm is strictly linear. When $k$ explodes (say, $k = 2^{32}$ for arbitrary integers), the algorithm collapses to uselessness because the counts array alone blows up memory.

**Radix sort** runs in $O(d(n + b))$ time and $O(n + b)$ space, where $d$ is the number of digits in the maximum value and $b$ is the base. For fixed-width integer types (the case you meet in real software), $d$ is a constant. So the time is $O(n)$ and the space is $O(n + b)$.

Plainly stated: counting sort is "make a histogram, then read it out in order"; radix sort is "do counting sort on every digit, from least to most significant, leaning on stability so earlier passes survive." Neither algorithm performs a single comparison between two input elements. Both algorithms read the *intrinsic structure* of the elements — the values themselves, or the digits of the values — and use that structure to compute placements directly.

### Is it optimal?

Yes, given the model, and the argument is the cheapest in the book: **the lower bound for sorting in any model is $\Omega(n)$** — you have to look at every element at least once, or an adversary can change the unexamined element to make your output wrong (the same adversary argument from chapter 1). Counting sort and radix sort both hit that bound exactly, in the regime where their structural assumptions hold.

What this chapter changed was *which* lower bound applies, not the bound for sorting itself. The $\Omega(n \log n)$ comparison-model bound from chapter 4 still holds for any algorithm that only compares pairs of elements. Counting sort and radix sort just aren't in that model. They use a stronger operation — array indexing by element value, digit extraction — and the lower bound for *that* richer model is the simpler $\Omega(n)$.

This is the reframing the chapter wants to leave you with: **lower bounds belong to models, not problems.** The decision-tree bound was a fact about what comparisons can resolve. Linear-time sorting was always possible — the algorithms in this chapter just had to enrich the model with operations the comparison-only world didn't allow.

## Lower bounds belong to models

Counting sort is correct because the prefix-sum array dictates exact placements; radix sort is correct because each stable per-digit pass extends sortedness by one digit without disturbing what earlier passes built. Both run in $O(n)$ when their structural assumptions hold — a bounded value range for counting sort, a fixed-width digit representation for radix sort. Both are optimal in their model — you cannot do better than linear because you must read every element at least once.

A lower bound says what an algorithm cannot do *within a given model*, not what it cannot do at all. Change the model and the bound changes. The comparison model's $\Omega(n \log n)$ bound on sorting is a statement about what binary decisions can resolve. The richer "look inside the element" model — direct addressing, digit extraction — gets a lower bound of $\Omega(n)$, because each operation extracts more bits of information than a single comparison does. The price for linear-time sorting was relaxing the opacity assumption hidden in chapters 3 through 5.

That same trick — exploit the *intrinsic structure* of the input rather than treating it as opaque — comes back throughout the rest of the book. Hash tables in Part II turn keys into addresses, which is exactly counting sort's value-is-the-address move generalized to any key type. Trees in Part III still use comparison, but they exploit the *order structure* of the keys to make every comparison cut a subtree in half. Suffix arrays and tries in Part IV exploit the *character structure* of strings to do pattern matching faster than comparison alone could ever achieve. The pattern recurs every time an algorithm decides to stop treating its input as opaque and start asking what's inside.

In the next chapter, the focus shifts from theoretical algorithms to the ones you use. Real-world sorting — what Python's `sorted()`, Java's `Arrays.sort`, and C++'s `std::sort` do under the hood — isn't any of the algorithms in this part of the book applied uniformly. It's a *composition* of them, hand-stitched to exploit the structure of real inputs. The chapter is short, the lesson is large: asymptotic optimality is necessary but not sufficient.

## Notes and further reading

Counting sort is folklore; the first published treatment is usually attributed to Harold Seward in 1954. CLRS (4th ed.) §8.2 gives the clean treatment. Radix sort goes back to Herman Hollerith's tabulating machines in the 1880s — it was a hardware algorithm long before it was a software one — and was formalized for digital computers in the 1950s. CLRS §8.3 covers LSD radix sort; there's also an MSD (most significant digit first) variant treated in Sedgewick's *Algorithms* (4th ed.) §5.1 that uses recursion in a way that mirrors quicksort more than counting sort. The model-vs-problem framing of the comparison lower bound — that $\Omega(n \log n)$ is a property of the comparison model rather than of sorting — is treated in CLRS §8.1; it's the same insight that this chapter built on, said two ways. The relationship between counting sort and hashing — both being "use the value as an address" — is sometimes called *direct addressing* in the data-structures literature; you'll meet it again in Part II.
