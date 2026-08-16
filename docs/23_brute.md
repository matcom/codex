# Sliding the pattern, comparing every shift

You have a long string — call it the *text* — and a much shorter string — call it the *pattern* — and you want to know where, if anywhere, the pattern occurs inside the text. That is the pattern-matching problem in its rawest form, and it is the question every algorithm in this part is going to answer, each one trading more preprocessing for less scanning. I want to start where the field starts, with the algorithm that does no preprocessing at all and gets surprisingly far on the strength of a simple double loop.

**A window of length $m$ slides across $n$ positions and tries each one.** That is the whole algorithm. There is no failure function, no rolling hash, no automaton. Just a window, a slide, and a character-by-character comparison at every shift. Every other pattern-matching algorithm in this part is the brute force, but skipping shifts I can prove are hopeless. The brute force is the baseline against which everything else justifies itself.

## Finding a needle in a string haystack

I want to be precise about the problem before writing anything. Given a text $T$ of length $n$ and a pattern $P$ of length $m$, with $m \le n$, find an index $i$ in $0 \le i \le n - m$ such that $T[i..i+m-1] = P$ — that is, the substring of $T$ starting at $i$ and running for $m$ characters matches $P$ exactly. If no such $i$ exists, report failure. For `find_all`, return every such $i$.

That is the spec `grep -F` is solving when you search for a fixed string (no regex). It is the spec your editor is solving when you press Ctrl-F. It is, with small variations, the spec a packet-inspection firewall is solving when it scans a stream for a signature. The reason this problem deserves an entire part of the book is that the obvious algorithm — try every starting position — has a worst-case behaviour bad enough to motivate four genuinely different cleverness moves, and an average-case behaviour good enough that the obvious algorithm wins anyway in the shape of most production code.

The first thing you might try is exactly what I'll write down in the next section: line the pattern up at position 0, compare it character by character, and if there's a mismatch, slide one position to the right and start again. There are $n - m + 1$ possible starting positions and the comparison at each one takes at most $m$ work, so the worst case is $O(nm)$ character comparisons. For a text of a million characters and a pattern of ten, that is ten million comparisons in the worst case and roughly a million in the average case — both numbers a modern CPU finishes in milliseconds. The story of why $O(nm)$ is "too much" and what to do instead starts in the next chapter; this chapter is about what $O(nm)$ actually costs.

## The double loop

Here is the simplest pattern matcher you can write. Two nested loops: the outer one slides a window of length $m$ along the text, the inner one walks the window and compares character by character. The instant a character disagrees, I bail out of the inner loop and slide the window one to the right.

```python {export=src/codex/strings/brute.py}
def find(text: str, pattern: str) -> int | None:
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
    if m > n:
        return None
    for i in range(n - m + 1):
        j = 0
        while j < m and text[i + j] == pattern[j]:
            j += 1
        if j == m:
            return i
    return None
```

The empty-pattern case returns 0 — by convention every string contains the empty string at position 0, matching Python's own `"".find("")` and `re.search("", ...)`. The pattern-longer-than-text case returns `None` immediately, since no window can fit. The body is the double loop I just described: for each shift $i$, advance $j$ as long as characters match, and if $j$ reaches $m$ then I've matched the whole pattern starting at $i$. Otherwise slide on.

Bilingually: I am holding a window of length $m$ and sliding it one position to the right at a time across the text; at each position I read characters until I find a disagreement, and the first position where I read all the way through is the match. There is nothing being remembered between shifts — every shift starts the inner comparison from scratch at $j = 0$, which is exactly the wastefulness chapter 25's KMP will eventually fix.

Now `find_all`. I want every starting index where the pattern occurs, and I have to make one design decision: do I report **overlapping** matches or **non-overlapping** ones? Consider the text `"aaaa"` and the pattern `"aa"`. The overlapping interpretation reports positions 0, 1, 2 — three matches that share characters. The non-overlapping interpretation reports 0, 2 — two matches that tile the text without sharing. Both are defensible. I'll pick overlapping, because that's the convention `re.finditer` uses for patterns without lookahead and it's the convention every subsequent chapter in this part will measure itself against. The cost is one extra integer add at each match site, which is nothing.

```python {export=src/codex/strings/brute.py}
def find_all(text: str, pattern: str) -> list[int]:
    n, m = len(text), len(pattern)
    if m == 0:
        return []
    if m > n:
        return []
    matches: list[int] = []
    for i in range(n - m + 1):
        j = 0
        while j < m and text[i + j] == pattern[j]:
            j += 1
        if j == m:
            matches.append(i)
    return matches
```

Same double loop as `find`, except instead of returning on the first complete match I append the index and keep going. The empty-pattern case returns an empty list — there is one reasonable convention here ("every position is a match") and one practical convention ("the empty pattern is degenerate, report nothing"), and I'm picking the practical one to avoid `find_all("hello", "")` returning a length-six list of zeros nobody asked for. That is a documented choice; if you want every-position semantics, you write three extra lines.

The walk is identical to `find`'s. The overlap behaviour is implicit in `range(n - m + 1)` — each shift increments by 1, not by `m`, so a match at position 0 doesn't stop me from finding another at position 1.

## Running it on the canonical text

I'll use a single text string across every chapter in this part, so you can compare algorithms side by side without having to re-orient on a new sentence each time. The text is short enough to read at a glance and rich enough to have interesting matches.

```python
from codex.strings.brute import find, find_all

TEXT = "the rain in spain stays mainly in the plain"

idx = find(TEXT, "ain")
print(f"first match of 'ain' at index {idx} — that's the start of 'ain' in 'rain'")

all_ain = find_all(TEXT, "ain")
print(f"all matches of 'ain': {all_ain}  (four occurrences: rain, spain, mainly, plain)")

all_in = find_all(TEXT, "in")
print(f"all matches of 'in': {all_in}  (six occurrences across the sentence)")

all_the = find_all(TEXT, "the")
print(f"all matches of 'the': {all_the}  (two — opening word and 'the plain')")

miss = find(TEXT, "frog")
print(f"searching for 'frog': {miss}  (no frogs in this sentence)")
```

The four `ain` matches sit inside `rain`, `spain`, `mainly`, and `plain`. The six `in` matches include those four plus the standalone words `in` (twice). The two `the` matches are the opening word and the one inside `the plain` at the end. Searching for `frog` returns `None` because there is no `f` anywhere in the text — the inner loop bails out at $j = 0$ for every shift.

To make the overlap behaviour I picked visible — and to convince you it actually matters — here is a deliberately overlap-prone input.

```python
from codex.strings.brute import find_all

print(f"find_all('aaaa', 'aa') = {find_all('aaaa', 'aa')}  (overlapping: 0, 1, 2)")
print(f"find_all('abababab', 'aba') = {find_all('abababab', 'aba')}  (overlapping: 0, 2, 4)")
```

The first call returns `[0, 1, 2]`, not `[0, 2]`. The second returns `[0, 2, 4]`, not just `[0]` or `[0, 4]`. The overlapping convention catches every position where the pattern starts, even when those positions share characters.

## When the worst case bites

The double loop is $O(nm)$ in the worst case, but on most realistic inputs the inner loop bails out after one or two character comparisons and the algorithm runs much closer to $O(n)$. I want to show you the construction that actually realizes the worst case, because it tells you exactly what kind of input you'd have to feed `grep` to make it suffer.

The canonical pathological input is a text and pattern that *almost* match at every shift but disagree at the very last character of the pattern. The simplest example: text `"aaaa...aab"` (many `a`s followed by a `b`), pattern `"aaa...ab"` (slightly fewer `a`s followed by a `b`). At every shift the inner loop reads through almost all of the pattern before finding the disagreement. Every shift pays full price.

To make this measurable, I'll factor out a counting variant that returns both the answer and the number of character comparisons it performed.

```python {export=src/codex/strings/brute.py}
def find_counting(text: str, pattern: str) -> tuple[int | None, int]:
    n, m = len(text), len(pattern)
    if m == 0:
        return 0, 0
    if m > n:
        return None, 0
    comparisons = 0
    for i in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1
            if text[i + j] != pattern[j]:
                break
            j += 1
        if j == m:
            return i, comparisons
    return None, comparisons
```

I unrolled the inner `while` slightly so I can bump `comparisons` once per character read — the original `find`'s `while j < m and text[i + j] == pattern[j]` does the comparison implicitly in the loop condition, which makes counting awkward. This version is semantically identical but explicit about where the comparison happens. Now I can feed it the pathological input and watch the numbers.

```python
from codex.strings.brute import find_counting

# pathological case: pattern almost matches at every shift, fails at the last char
text = "a" * 20 + "b"
pattern = "a" * 4 + "b"

result, comps = find_counting(text, pattern)
n, m = len(text), len(pattern)
shifts = n - m + 1

print(f"text = {text!r}  (n = {n})")
print(f"pattern = {pattern!r}  (m = {m})")
print(f"shifts tried = {shifts}")
print(f"comparisons = {comps}")
print(f"upper bound n*m = {n * m}")
print(f"match at index {result}")
```

You should see something close to $shifts \times m$ comparisons — every shift before the match reads almost the whole pattern before bailing, and the matching shift reads all of it. The exact count is $\text{shifts} \times m$ in this construction, which lands right on the $O(nm)$ ceiling. Bilingually: on this input, the algorithm does the maximum amount of work it's theoretically capable of doing — there's no shift it gets to skip cheaply, because every shift looks like a near-match.

Compare with a benign input where the inner loop bails out at $j = 0$ for almost every shift.

```python
text = "the rain in spain stays mainly in the plain"
result, comps = find_counting(text, "frog")
n, m = len(text), 4
print(f"searching for 'frog' in the canonical text — n={len(text)}, m=4")
print(f"comparisons = {comps}  (close to n, because 'f' doesn't appear)")
```

Searching for `"frog"` in the canonical text does only as many comparisons as there are shifts, because every shift fails on the first character — there are no `f`s for the inner loop to advance past. That is the average case in disguise: when the alphabet is large and the pattern's first character is rare, the inner loop is a near-no-op. The $O(nm)$ ceiling is a worst case, not a typical case, and the gap between them is what makes the brute force competitive in practice.

## Why grep still ships it

Knowing that the worst case exists and knowing that production code uses it anyway are not in contradiction — production code knows the worst case exists and chooses to live with it, because the average case is fast and the constant factor is unbeatable. CPython's `str.find` runs a variant of this exact algorithm, called the *two-way* algorithm, which adds a small skip table on top of the naive scan but keeps the inner loop's character-by-character shape; GNU `memmem`'s default implementation uses a similar two-way variant with SIMD-friendly chunk reads when the pattern is short enough to fit in a register. The reason these libraries don't reach for KMP or Boyer-Moore on every call is that the brute-force inner loop is *one tight loop with no branches*, and that runs faster on modern hardware than any algorithm whose inner loop has to consult a precomputed table on every step. The asymptote loses; the cache wins.

## The three questions, applied

### Is it correct?

The invariant I'm maintaining is: **after the outer loop has examined shifts $0, 1, \ldots, i - 1$ and not returned, the pattern does not occur at any of those positions.** The inner loop establishes that invariant for each $i$ — it reads characters in order until it finds either a disagreement (so the pattern doesn't match at $i$, and I move on) or runs off the end of the pattern (so it matches, and I return $i$). When the outer loop terminates without returning, every shift in $0, \ldots, n - m$ has been examined and rejected, and no other shift is possible because a window of length $m$ starting at $i > n - m$ would run past the end of the text. So `find` returns either the smallest matching index or `None` if none exists, which is exactly the spec.

`find_all` differs only in that it appends instead of returning. The invariant strengthens to: **after the outer loop has examined shifts $0, 1, \ldots, i - 1$, `matches` contains exactly the indices in that range at which the pattern occurs.** When the loop ends, that's every shift, so `matches` is the complete overlapping-match set. `find_counting` is `find` with an extra integer that ticks every time the inner loop's equality check runs — it doesn't change what gets returned, only what gets reported alongside.

### How efficient is it?

The cost is bounded by the number of character comparisons, which is at most $m$ per shift over $n - m + 1$ shifts. So the worst case is $O((n - m + 1) \cdot m) = O(nm)$, achieved by the `"aaa...ab"` construction above. The best case is $\Omega(n)$ — every shift bails out at $j = 0$ — which happens whenever the pattern's first character is rare in the text.

Bilingually: on a text of a million characters and a pattern of ten, you'll do at most ten million comparisons and at least about a million. The average behaviour on natural-language text with a typical-length pattern sits much closer to the lower bound than the upper, because the pattern's first character only matches a small fraction of text positions and the inner loop bails after one comparison for the rest.

Space is $O(1)$ for `find` and `find_counting` — three integers and the index variables, nothing allocated per shift. `find_all` is $O(k)$ for the output list, where $k$ is the number of matches.

| Operation | Time (worst) | Time (best) | Space |
|-----------|--------------|-------------|-------|
| `find(text, pattern)` | $O(nm)$ | $\Omega(n)$ | $O(1)$ |
| `find_all(text, pattern)` | $O(nm)$ | $\Omega(n)$ | $O(k)$ output |
| `find_counting(text, pattern)` | $O(nm)$ | $\Omega(n)$ | $O(1)$ |

### Is it optimal?

For exact pattern matching with no preprocessing, $\Omega(n)$ is the lower bound — you have to at least read every character of the text to be sure the pattern doesn't appear, because a single mismatch at any unread position could hide a match elsewhere. The brute force matches that lower bound in its best case but blows past it by a factor of $m$ in the worst case, so it is *not* optimal in the worst-case sense.

The algorithms in the next four chapters all run in $O(n + m)$ worst-case time — the brute force's $O(n)$ best case made worst-case-tight. KMP gets there with a precomputed failure function that lets shifts reuse work from previous shifts. Boyer-Moore gets there (well, $O(nm)$ worst-case, $O(n/m)$ best-case) by reading the pattern right-to-left and skipping whole regions on a mismatch. Rabin-Karp gets there in expectation with a rolling hash that compares fingerprints instead of full strings. The finite-automaton view of chapter 24 is the conceptual bridge that explains why KMP and Aho-Corasick are the same idea in different costumes.

So the brute force is optimal in the best case and a factor of $m$ off in the worst case — and yet it's the algorithm production code most often ships. The next four chapters are about closing the worst-case gap, and one of the things you'll watch is each algorithm fighting to keep the brute force's best-case behaviour while neutralizing its worst case.

There's a temptation to read "brute force" as an insult — the algorithm you ship before you've thought hard about the problem. I want you to read it differently. The brute force is the algorithm that does *only the work the problem definition forces it to do*. It does not preprocess, it does not memoize, it does not skip. Every comparison it makes is one the spec couldn't have asked it not to make without giving it extra information.

What the next four chapters do is *give the algorithm extra information*. KMP gives it information about the pattern (a failure function precomputed in $O(m)$ time). Boyer-Moore gives it two tables — a bad-character table and a good-suffix table — also computed from the pattern. Rabin-Karp gives it a hash function over windows of the text. Aho-Corasick generalizes the failure-function idea to many patterns at once. Each chapter pays a preprocessing cost in exchange for skipping shifts the brute force would have examined, and each chapter justifies its cleverness against the brute force's tight inner loop.

The meta-lesson — and it's one you'll keep meeting in the rest of this part — is that *the obvious algorithm is the baseline you have to beat with your cleverness, not a competitor you can ignore*. When the obvious algorithm has a tight inner loop and a workload-favourable average case, beating it is hard. Sometimes you don't, and the obvious algorithm ships. Sometimes you do, and the gap you opened is exactly the value your cleverness produced. Either way the brute force is the reference frame, not the wrong answer.

## Notes and further reading

The brute-force string-matching algorithm is so old it has no clear inventor — it predates the formal study of algorithms by some margin, and every introduction to the topic begins with it. CLRS covers it in section 32.1 ("The naive string-matching algorithm") with the same $O((n - m + 1)m)$ worst-case bound I derived above. Sedgewick and Wayne's *Algorithms* (4th ed.) section 5.3 ("Substring Search") opens with the brute force before moving to KMP and Boyer-Moore, and is worth reading for its diagrams of the shift-and-compare process.

The reason I leaned on `grep` and `str.find` in this chapter is that the brute force is genuinely what production code runs — CPython's `str.find` uses Crochemore and Perrin's *two-way* algorithm, which is the brute force with a small skip table; GNU `memmem` in glibc 2.9+ uses a similar two-way variant; the Rust standard library's `str::find` uses two-way on short patterns and a hash-based variant on long ones. The relevant academic citation is Crochemore and Perrin's 1991 *Journal of the ACM* paper "Two-way string-matching", which is a refinement of the brute force, not an abandonment of it. Wojciech Mucha's 2013 paper "Speeding up string matching by weak factor recognition" is a more recent variant in the same lineage. The brute force isn't a place algorithm design moved past; it's the substrate every production matcher sits on.

In the next chapter I switch the lens — I'll show you what happens if you read the pattern not as a string but as a tiny *automaton*, with one state per prefix and a transition on each character, and you'll see why that reframing is exactly what KMP needs to skip the work the brute force redoes.
