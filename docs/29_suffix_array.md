# Indexing every substring with a sorted array

Every algorithm in Part IV up to that point answered "find these patterns in this text" — the patterns came first, fixed and known, and the text streamed past them. I want to flip the setup now. Preprocess the *text* once, build an index, and then answer pattern queries against that index — any pattern, as many as you like, each query much cheaper than re-scanning. That's the move full-text search engines make, the move biological-sequence aligners make, the move the Burrows-Wheeler transform makes before it compresses anything. The structure that does it, in its cleanest form, is the **suffix array**.

**The sorted list of every suffix's starting position — every substring of the text is a prefix of some suffix.** That's the entire structural insight, and once it lands the rest of the chapter is mechanics. A substring of $T$ starting at position $i$ with length $m$ is just the first $m$ characters of the suffix $T[i{:}]$. So if I have every suffix sorted lexicographically, any pattern occurrences cluster as a contiguous range in that sorted list — every suffix whose first $m$ characters spell the pattern sits together — and a pair of binary searches pulls the range out in $O(m \log n)$ time per query. Indexing reduces to sorting suffixes; pattern search reduces to binary search.

By the end of this chapter you'll have built the suffix array two ways — once with an explicit $O(n^2 \log n)$ sort, then again with the prefix-doubling trick that knocks it down to $O(n \log^2 n)$ — paired it with Kasai's beautiful $O(n)$ algorithm for the longest-common-prefix array, used it to answer pattern queries on the canonical text from earlier chapters in $O(m \log n)$ per query, and applied the LCP array to find the longest repeated substring of a text in linear time after the array is built.
## Every substring is a prefix of some suffix

I want to start where the suffix array starts: at the observation that every substring of a text $T$ has a name. Pick any substring; it begins at some position $i$ and ends at some position $j$. What you're looking at is $T[i:j]$, which is the same as the first $j - i$ characters of $T[i:]$ — the suffix that starts at position $i$. So if you write down every suffix of $T$ (there are exactly $n$ of them, one per starting position), every substring you could possibly care about is a *prefix* of one of those suffixes.

That observation has more force than it sounds at first. Pattern matching asks "does pattern $P$ appear in $T$, and if so where?" Rephrase it: "does $P$ appear as a *prefix* of any suffix of $T$, and if so which suffixes?" Same question, different shape — and the new shape is one that an ordering can help with.

Sort the suffixes lexicographically. Now suffixes that share a common prefix sit next to each other in the sorted order, because lex order's first move is to compare the first character. Suffixes that share two characters of common prefix sit even closer together. And suffixes that all start with the same length-$m$ string $P$ form a *contiguous block* in the sorted list — they're exactly the suffixes whose first $m$ characters spell $P$, and the lex order can't intersperse them with anything else, because anything else either has an earlier-character difference and falls outside the block on one side, or has a later-character difference within the prefix and the lex order separates them.

So if I had the sorted list, finding all matches of $P$ in $T$ would be: binary-search for the leftmost suffix whose first $m$ characters are $\geq P$, then binary-search for the leftmost suffix whose first $m$ characters are $> P$, and the suffixes between those two indices are exactly the matches. Each binary search does $O(\log n)$ comparisons, and each comparison is at most $m$ characters of substring compare, so the whole query is $O(m \log n)$. For a text of length $10^9$ and a pattern of length $30$, that's about $30 \cdot 30 = 900$ character reads per query, no matter how many matches there are.

The suffix array itself doesn't store the suffixes — that would cost $O(n^2)$ memory, since the suffixes of a length-$n$ text have total length $n(n+1)/2$. It stores something much cheaper: **the starting positions of the suffixes, in the order the suffixes themselves would be in if sorted.** A single array of $n$ integers. For `"banana"`, the suffix array is $[5, 3, 1, 0, 4, 2]$ — the suffixes starting at those positions, read in that order, are `"a"`, `"ana"`, `"anana"`, `"banana"`, `"na"`, `"nana"`, which is exactly the lex-sorted list of all six suffixes.

That's the data structure. The chapter from here is two questions: how do I build the array fast (the suffixes themselves are $O(n^2)$ to write down, so I can't afford to materialize them), and what else can I do with it once I have it?

## The naive sort

The first version is the one you'd write if you hadn't thought about cost yet. Generate every suffix, hand them to Python's sort, and read off the starting positions.

```python {export=src/codex/strings/suffix_array.py}
def suffix_array_naive(text: str) -> list[int]:
    """Build the suffix array by explicit sort of every suffix.
    O(n^2 log n) time, O(n^2) extra memory. Clear; not for large inputs.
    """
    n = len(text)
    indexed = sorted(range(n), key=lambda i: text[i:])
    return indexed
```

The whole function is one `sorted` call with a key function. `range(n)` is the list of starting positions; the key `lambda i: text[i:]` tells Python's sort to order positions by the suffix that starts at each one. Python's `sorted` returns a new list, and the result is the suffix array.

Let me run it on `"banana"` and walk through what comes out.

```python
from codex.strings.suffix_array import suffix_array_naive

text = "banana"
sa = suffix_array_naive(text)

print(f"text     = {text!r}")
print(f"suffix array = {sa}")
print()
print("sorted suffixes:")
for i in sa:
    print(f"  start={i}  suffix={text[i:]!r}")
```

Six positions, six suffixes, sorted lex. Position 5 first (the bare `"a"`), then 3 (`"ana"`), then 1 (`"anana"`), then 0 (`"banana"`), then 4 (`"na"`), then 2 (`"nana"`). The `a`-starting suffixes cluster at the top because `a < b < n`; within the `a` block, the shorter suffix wins because lex comparison treats end-of-string as smaller than any character.

Now the cost. Python's sort is `O(n \log n)` comparisons. Each comparison is a string comparison between two suffixes, which in the worst case scans both suffixes to the end — $O(n)$ characters. So the total work is $O(n^2 \log n)$. For a text of length $10^6$, that's about $10^6 \cdot 20 \cdot 10^6 = 2 \cdot 10^{13}$ character comparisons — completely impractical. The memory cost is worse: the key function materializes a copy of every suffix as a separate string object, and the suffixes have total length $n(n+1)/2 = O(n^2)$, so the sort needs $O(n^2)$ extra memory. A million-character text would want a terabyte of suffix storage. Naive is the right word.

I'll keep `suffix_array_naive` around as a clarity check — I'll use it later to verify that the fast version produces the same array on a real input — but I won't run it on anything larger than `"banana"`-sized inputs.

## Manber-Myers and the doubling trick

The killer idea — Udi Manber and Gene Myers, 1993 — is that I don't have to compare suffixes character by character. Instead, I assign each suffix a **rank** based on how its first $k$ characters compare to every other suffix's first $k$ characters, and I increase $k$ by doubling between iterations.

The mechanic that makes this work: if I already know the rank of every suffix based on its first $k$ characters, then I can compute the rank based on the first $2k$ characters by sorting the suffixes by the *pair* $(\text{rank}[i],\ \text{rank}[i+k])$ — the rank of my own first $k$ characters, followed by the rank of the next $k$ characters, which is the rank of the suffix that starts at position $i + k$. Pairs are cheap to compare: two integer comparisons, $O(1)$ apiece. And $k$ doubles each iteration, so after $\lceil \log_2 n \rceil$ doublings, every suffix's rank reflects $n$ characters' worth of order, which is the entire suffix. At that point the rank order *is* the lex order, and I'm done.

The total work is $O(\log n)$ sorts. Each sort is over $n$ items with $O(1)$ comparisons, so each sort is $O(n \log n)$ using Python's timsort. Total: $O(n \log^2 n)$. The proper Manber-Myers algorithm uses radix sort on the pair keys for $O(n)$ per sort and $O(n \log n)$ total — I won't implement that; I'll let timsort eat the extra log factor and gain readability.

The initial rank — what I use at $k = 1$ — is just each suffix's first character. Two suffixes that start with the same character get the same rank; two that start with different characters get ranks ordered by the character order. The cleanest way to bootstrap is to set `rank[i] = ord(text[i])` directly — that's already a consistent ranking by first-character order, even if the rank values aren't dense integers like $0, 1, 2, \ldots$. The doubling step doesn't care about density; it only cares about the *order* the ranks induce.

Here's the function. The body is one outer loop over $k$ values, with two phases inside: sort by the pair key, then recompute ranks.

```python {export=src/codex/strings/suffix_array.py}
def suffix_array(text: str) -> list[int]:
    """Build the suffix array via prefix-doubling (Manber-Myers style).
    O(n log^2 n) using Python's timsort; the O(n log n) Manber-Myers
    proper would use radix sort instead — mentioned but not implemented.
    """
    n = len(text)
    if n == 0:
        return []
    sa = list(range(n))
    rank = [ord(c) for c in text]
    k = 1
    while True:
        def key(i: int) -> tuple[int, int]:
            return (rank[i], rank[i + k] if i + k < n else -1)
        sa.sort(key=key)
        new_rank = [0] * n
        new_rank[sa[0]] = 0
        for j in range(1, n):
            new_rank[sa[j]] = new_rank[sa[j - 1]]
            if key(sa[j]) != key(sa[j - 1]):
                new_rank[sa[j]] += 1
        rank = new_rank
        if rank[sa[n - 1]] == n - 1:
            break
        k *= 2
        if k >= n:
            break
    return sa
```

A few things are worth pointing at. The sentinel `-1` in the `key` function handles suffixes that fall off the end — a suffix starting at position $i$ with $i + k \geq n$ has no second half, and I want it to sort *before* any suffix that has a real character there. Using `-1` is one easy way to get that behavior, since any real `rank` value will be a non-negative integer. The early-exit condition `rank[sa[n - 1]] == n - 1` checks whether all ranks have become distinct (the largest rank equals $n - 1$, which happens only when every suffix has its own unique rank); when that condition fires, no further doubling can change the order and I'm done.

Let me trace the algorithm on `"banana"` so the doubling is concrete. Initial ranks are the character codes: `[ord('b'), ord('a'), ord('n'), ord('a'), ord('n'), ord('a')]` = `[98, 97, 110, 97, 110, 97]`.

At $k = 1$, the pair keys $(\text{rank}[i], \text{rank}[i+1])$ are: position 0 → $(98, 97)$, position 1 → $(97, 110)$, position 2 → $(110, 97)$, position 3 → $(97, 110)$, position 4 → $(110, 97)$, position 5 → $(97, -1)$. Sorting positions by these keys: $5$ ($97, -1$), then $1$ ($97, 110$), then $3$ ($97, 110$), then $0$ ($98, 97$), then $2$ ($110, 97$), then $4$ ($110, 97$). So `sa` after the first sort is $[5, 1, 3, 0, 2, 4]$. Recompute ranks: position 5 gets rank 0; positions 1 and 3 have equal keys to each other but different from 5's, so they both get rank 1; position 0 has a strictly larger key, rank 2; positions 2 and 4 have equal keys, both rank 3. The new rank array is `[2, 1, 3, 1, 3, 0]`. Largest rank is 3, not yet $n - 1 = 5$, so keep doubling.

At $k = 2$, the pair keys are now $(\text{rank}[i], \text{rank}[i+2])$: position 0 → $(2, 3)$, position 1 → $(1, 1)$, position 2 → $(3, 3)$, position 3 → $(1, 0)$, position 4 → $(3, -1)$, position 5 → $(0, -1)$. Sorting positions: $5$ ($0, -1$), then $3$ ($1, 0$), then $1$ ($1, 1$), then $0$ ($2, 3$), then $4$ ($3, -1$), then $2$ ($3, 3$). So `sa` after the second sort is $[5, 3, 1, 0, 4, 2]$ — and that matches the suffix array I got from the naive sort. Recompute ranks: every key is now distinct, so ranks come out $[3, 2, 5, 1, 4, 0]$ and the largest rank is $5 = n - 1$. Done in two doublings.

Time to actually run it.

```python
from codex.strings.suffix_array import suffix_array

text = "banana"
sa = suffix_array(text)

print(f"text     = {text!r}")
print(f"suffix array (prefix-doubling) = {sa}")
print()
print("sorted suffixes:")
for i in sa:
    print(f"  start={i}  suffix={text[i:]!r}")
```

Same array as the naive sort, computed without ever materializing the suffix strings. Two doublings sufficed for a length-6 text; for a length-$n$ text, $\lceil \log_2 n \rceil$ doublings is the worst-case bound, and many texts terminate early when their ranks become distinct.

Now a sanity check across a longer input — the canonical text I've been carrying through Part IV — to verify the two builders agree.

```python
from codex.strings.suffix_array import suffix_array_naive, suffix_array

TEXT = "the rain in spain stays mainly in the plain"
sa_slow = suffix_array_naive(TEXT)
sa_fast = suffix_array(TEXT)

print(f"length: {len(TEXT)}")
print(f"naive and prefix-doubling agree: {sa_slow == sa_fast}")
print(f"first 10 sorted suffixes:")
for i in sa_fast[:10]:
    print(f"  start={i:>2}  suffix={TEXT[i:]!r}")
```

The arrays match cell by cell. The fast version produced the same answer the naive version did, in much less work — and on a million-character input, the fast version would still be tractable while the naive version would have died long ago.

## Kasai's LCP in linear time

The suffix array on its own is enough to do pattern search. But there's a companion array that turns it into a much more powerful index, and the algorithm that computes it is one of the prettiest I know. The companion is the **longest-common-prefix array**, or **LCP**, defined as follows: `lcp[i]` is the length of the longest common prefix shared by the suffixes at `sa[i - 1]` and `sa[i]` — i.e., between consecutive entries in the sorted order. The first entry `lcp[0]` is defined to be 0 by convention (there's no `sa[-1]` to compare against).

The LCP captures *how similar* adjacent sorted suffixes are. For `"banana"`, the sorted suffixes are `"a"`, `"ana"`, `"anana"`, `"banana"`, `"na"`, `"nana"`, and reading the overlaps left-to-right: `"a"` vs `"ana"` share 1 character (`"a"`); `"ana"` vs `"anana"` share 3 characters (`"ana"`); `"anana"` vs `"banana"` share 0 characters (different first letter); `"banana"` vs `"na"` share 0; `"na"` vs `"nana"` share 2 (`"na"`). So `lcp = [0, 1, 3, 0, 0, 2]`.

The obvious way to compute LCP is to do it directly from the suffix array — for each adjacent pair, walk forward until characters disagree. That costs $O(n)$ per pair in the worst case, so $O(n^2)$ total. Kasai et al.'s 2001 algorithm does it in $O(n)$, by processing suffixes in a non-obvious order that lets the LCP from one suffix's computation jump-start the next.

The insight: process suffixes **in length order** (longest first, or equivalently in text-position order: position 0, 1, 2, …, $n - 1$). When I move from the suffix at position $i$ to the suffix at position $i + 1$, the new suffix has the same characters as the old one with the first character stripped off. So the LCP between $T[i+1:]$ and *any other* suffix $T[j+1:]$ is at least $h - 1$ if the LCP between $T[i:]$ and $T[j:]$ was $h$ — chopping one character off both can shrink the common prefix by at most one. That's the structural fact I want to exploit.

For each position $i$ in text order, I look up its rank — `rank[i]` is the position of suffix $i$ in the sorted suffix array. If its rank is positive (it's not the lex-smallest suffix), I compare it against the suffix one rank lower, which is the suffix that immediately precedes it in sorted order. I walk the common prefix forward starting from offset `h` (the LCP I carried over from the previous text position), incrementing `h` for every matching character. When I move on to the next text position, I decrement `h` by one (because I'm comparing one-character-shorter suffixes), but never below zero.

The total work is bounded by a charging argument: `h` increases at most $n$ times in total across the whole algorithm (each increment reads a matched character, and any specific character pair is read at most once), and `h` decreases at most $n$ times (once per text-position transition), so the total time is $O(n)$. That's the magic.

Here's the algorithm.

```python {export=src/codex/strings/suffix_array.py}
def lcp_kasai(text: str, sa: list[int]) -> list[int]:
    """Kasai's O(n) algorithm. lcp[i] = length of longest common prefix
    of the suffixes at sa[i-1] and sa[i]. lcp[0] is defined to be 0.
    """
    n = len(text)
    if n == 0:
        return []
    rank = [0] * n
    for i in range(n):
        rank[sa[i]] = i
    lcp = [0] * n
    h = 0
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and text[i + h] == text[j + h]:
                h += 1
            lcp[rank[i]] = h
            if h > 0:
                h -= 1
        else:
            h = 0
    return lcp
```

The first block builds the inverse permutation `rank` from `sa` — if `sa[i] = j` then `rank[j] = i`. That's the lookup I need to turn "the suffix at position $i$" into "where does that suffix sit in the sorted order". The main loop walks $i$ from $0$ to $n - 1$ in *text-position* order, not sorted order. For each position, it finds the predecessor in sorted order (the suffix at `sa[rank[i] - 1]`, which I call $j$), extends the running `h` as long as the characters match, and records `lcp[rank[i]] = h`. The decrement `h -= 1` at the end of each iteration is the carry-over: by the structural fact above, the LCP at the next text position is at least the current LCP minus one, so I start with a head-start instead of from zero.

Let me run it on `"banana"` and check the trace I worked out by hand.

```python
from codex.strings.suffix_array import suffix_array, lcp_kasai

text = "banana"
sa = suffix_array(text)
lcp = lcp_kasai(text, sa)

print(f"text = {text!r}")
print()
print(f"  i   sa[i]   lcp[i]   suffix")
for i in range(len(sa)):
    print(f"  {i}   {sa[i]:>3}      {lcp[i]:>3}     {text[sa[i]:]!r}")
```

Reading the table: `lcp[1] = 1` because `"a"` and `"ana"` share the prefix `"a"`; `lcp[2] = 3` because `"ana"` and `"anana"` share the prefix `"ana"`; `lcp[3] = 0` because `"anana"` and `"banana"` share no prefix (`a` vs `b`); `lcp[4] = 0` because `"banana"` and `"na"` share no prefix; `lcp[5] = 2` because `"na"` and `"nana"` share the prefix `"na"`. Six suffixes, six LCP entries, all computed in a single linear pass over the text.

## Pattern search in $O(m \log n)$

With the suffix array built, pattern search is the binary-search lookup I sketched in the opening. I want the range of suffix-array entries whose suffixes begin with the pattern $P$ — call those entries `[left, right)` — and then I return the text positions `sa[left:right]` as the list of match positions.

I find the range with two binary searches. The first is a lower-bound: the smallest index `mid` such that the suffix `text[sa[mid]:]` is lexicographically `>= pattern` when compared up to `len(pattern)` characters. The second is an upper-bound: the smallest index `mid` such that the suffix is lex `> pattern`. Between them lies the contiguous block of matches.

One subtle point worth saying out loud: I compare the suffix's first $m$ characters (the slice `text[sa[mid]:sa[mid] + m]`) against the pattern, not the entire suffix. The truncation is what makes the comparison cost $O(m)$ per binary-search step instead of $O(n)$, and it's correct because a match is exactly the condition "the suffix's first $m$ characters equal the pattern." If the suffix is shorter than $m$ characters (the slice falls off the end), the slice is just the entire suffix, which is strictly shorter than the pattern and therefore lex-less than it — exactly the behavior I want, since a too-short suffix can't be a match.

The function returns `sorted(sa[left:right])` — the matches sorted by text position, not by suffix-array index. That ordering is the one every other chapter's `find_all` has used (Aho-Corasick, KMP, brute force) on the canonical `"ain"` query, so the suffix-array variant lines up with them position-by-position.

```python {export=src/codex/strings/suffix_array.py}
def find_all(text: str, sa: list[int], pattern: str) -> list[int]:
    """Binary-search the suffix array for the range of suffixes that
    start with the pattern. Return the (sorted) text positions of all
    matches. O(m log n) per query.
    """
    n, m = len(text), len(pattern)
    if m == 0:
        return list(range(n))
    if m > n:
        return []

    # lower bound: smallest mid such that text[sa[mid]:sa[mid]+m] >= pattern
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if text[sa[mid]:sa[mid] + m] < pattern:
            lo = mid + 1
        else:
            hi = mid
    left = lo

    # upper bound: smallest mid such that text[sa[mid]:sa[mid]+m] > pattern
    lo, hi = left, n
    while lo < hi:
        mid = (lo + hi) // 2
        if text[sa[mid]:sa[mid] + m] <= pattern:
            lo = mid + 1
        else:
            hi = mid
    right = lo

    return sorted(sa[left:right])
```

Two binary searches, each $O(\log n)$ iterations with $O(m)$ comparison work per iteration, total $O(m \log n)$. The final `sorted` is over at most $z$ entries where $z$ is the number of matches; for typical queries $z$ is much smaller than $n$, so the sort cost is dominated by the binary searches.

Run it on the canonical text.

```python
from codex.strings.suffix_array import suffix_array, find_all

TEXT = "the rain in spain stays mainly in the plain"
sa = suffix_array(TEXT)

pattern = "ain"
matches = find_all(TEXT, sa, pattern)
print(f"text    = {TEXT!r}")
print(f"pattern = {pattern!r}")
print(f"matches at text positions: {matches}")
print()

# Same query as every previous Part IV chapter — should match exactly.
for start in matches:
    print(f"  position {start:>2}: {TEXT[start:start + len(pattern) + 5]!r}")
```

The match positions are `[5, 14, 25, 40]` — exactly the same four positions every previous Part IV chapter found for the same query on the same text. The difference is that every previous algorithm re-scanned the text from scratch per pattern; here I built the suffix array once and the query did four binary-search comparisons, each touching $O(m \log n) \approx 3 \cdot \log_2 43 \approx 17$ characters of work. Even more strikingly, if I run a second pattern against the same index I pay the cost of *only the new query*, not another full text scan.

```python
from codex.strings.suffix_array import find_all

# Same suffix array, several different queries — the build cost amortizes.
for pattern in ["the", "in", "plain", "missing"]:
    matches = find_all(TEXT, sa, pattern)
    summary = matches if matches else "no matches"
    print(f"  pattern {pattern!r:>10}  ->  {summary}")
```

Four queries, one suffix array, four small binary-search costs. That's the build-once-query-many shape the chapter opened by promising — the same operational mode Aho-Corasick gave you for multi-pattern matching, but now in the orthogonal direction: arbitrary patterns against a fixed text, instead of fixed patterns against arbitrary text.

## Finding the longest repeated substring

Here's where the LCP array starts paying off. The longest substring that appears at least twice in $T$ has a beautiful characterization in terms of LCP: **it's the substring whose length is the maximum value in the LCP array**, and its text position is the suffix-array entry at that LCP index.

Why? Any substring that appears twice in $T$ is a common prefix of two distinct suffixes — namely, the two suffixes starting at the two occurrence positions. Sort all the suffixes; the two suffixes whose common prefix is this substring don't have to be adjacent in the sorted order, but the LCP between *adjacent* sorted suffixes is at least the common-prefix length whenever the two suffixes nest within an LCP-monotone block. More precisely: the longest repeated substring's length equals the maximum LCP value, because two suffixes with a long common prefix must be adjacent in the sorted order (otherwise the suffix sandwiched between them would also share that prefix, contradicting either the maximality argument or just demonstrating an even-longer repeat). So the maximum entry in the LCP array tells me the length of the longest repeat, and the corresponding suffix-array entry tells me where one occurrence starts — I can read off the substring as `text[sa[i]:sa[i] + lcp[i]]`.

Let me show it on a text with a non-trivial repeat. `"abracadabra"` is the classic example — the substring `"abra"` appears twice, at positions 0 and 7, and that's the longest repeated substring in the text.

```python {export=src/codex/strings/suffix_array.py}
def longest_repeated_substring(text: str) -> tuple[int, str]:
    """Find the longest substring appearing at least twice in text.
    Returns (length, substring). If text has no repeated substring of
    positive length, returns (0, "").
    """
    n = len(text)
    if n < 2:
        return (0, "")
    sa = suffix_array(text)
    lcp = lcp_kasai(text, sa)
    idx = max(range(n), key=lambda i: lcp[i])
    length = lcp[idx]
    if length == 0:
        return (0, "")
    return (length, text[sa[idx]:sa[idx] + length])
```

The function builds the suffix array and the LCP, picks the index of the maximum LCP entry, and returns the substring at that suffix-array position with that length. Three lines of real work after the two builders. The whole cost is dominated by the suffix-array construction at $O(n \log^2 n)$; everything else — the LCP build, the linear scan for the maximum — is $O(n)$.

```python
from codex.strings.suffix_array import longest_repeated_substring

for text in ["abracadabra", "banana", "abcabcaa", "mississippi", "no_repeats"]:
    length, substring = longest_repeated_substring(text)
    if length == 0:
        print(f"  {text!r:>15}  ->  no repeated substring")
    else:
        print(f"  {text!r:>15}  ->  {substring!r} (length {length})")
```

`"abracadabra"` → `"abra"` (length 4). `"banana"` → `"ana"` (length 3). `"abcabcaa"` → `"abca"` (length 4, appearing at positions 0 and 3). `"mississippi"` → `"issi"` (length 4). The application is the kind of thing that would be expensive to do by brute force — comparing every pair of substrings is $O(n^4)$ — and the suffix-array approach brings it down to the build cost plus linear time.

The construction generalizes. The $k$-th longest repeated substring drops out by sorting LCP entries; the *longest substring repeating at least $k$ times* drops out by sliding a window of length $k - 1$ over the LCP array and taking the maximum of the per-window minima; the longest substring common to two texts drops out by concatenating them with a separator character and running the same algorithm. The LCP array is the workhorse.

## What about suffix trees and suffix automata?

The **suffix tree** is the older structure — Weiner 1973, McCreight 1976, Ukkonen 1995 — and it stores the suffixes as the leaves of a compressed trie. Every internal node has at least two children, the edges are labeled with substrings of $T$, and the path from the root to any leaf spells a suffix. The structure is $O(n)$ in size if you use a clever edge-labeling scheme, and it supports an enormous range of string-processing queries in time proportional to the query size, not the text size: pattern matching in $O(m)$, longest common substring of two texts, all pairs of repeated substrings, and more.

The suffix tree is gorgeous in theory and a pain in practice. The constant factor on the size is large — typically $15$–$20$ bytes per character of the input — and the implementations of Ukkonen's $O(n)$ construction are notoriously fiddly. The suffix array gives you almost everything the suffix tree gives you (modulo a $\log$ factor on some queries) at $4$–$8$ bytes per character and with an implementation you can write in fifty lines. Almost every modern library — `bowtie` and `bwa` for genomics, `sa-is` and `divsufsort` as standalone libraries, the BWT-based compressors like `bzip2` and `xz` — uses a suffix array (or a variant like the FM-index built from one), not a suffix tree.

The **suffix automaton** is a different beast — Blumer et al.'s 1985 directed acyclic word graph (DAWG) — which is the minimal DFA recognizing every substring of $T$. It's the right structure when you want online construction (build it character by character as the text streams in) and is the basis of some very fast string-matching libraries. Its space is also $O(n)$, and its construction is famously elegant. Outside that niche, the suffix array is still usually the right call.

What about achieving $O(n)$ suffix-array construction? It's possible — the **SA-IS algorithm** by Nong, Zhang, and Chan (2009) achieves it via an induced-sorting scheme that exploits the structure of LMS-suffixes ("leftmost S-type"), and several other linear-time algorithms exist (DC3 by Kärkkäinen-Sanders 2003, KA by Kärkkäinen-Aluru 2003). I'm not going to implement any of them; they're significantly harder to get right than Manber-Myers, and for most workloads $O(n \log^2 n)$ on a length-$n$ text is fast enough. The pointer if you want the linear-time version: SA-IS is the modern standard, and `divsufsort` is the reference C implementation.

## The three questions, applied

### Is it correct?

There are three correctness claims to nail down: the suffix-array builders return the right permutation; the LCP builder returns the right LCP values; and the pattern-search routine returns exactly the set of match positions.

For the **suffix-array builders**, `suffix_array_naive` is correct by appeal to Python's sort: `sorted(range(n), key=lambda i: text[i:])` returns the positions in the order of their suffixes' lex order, which is the suffix-array definition. For `suffix_array`, the invariant maintained across iterations is: **after the $k$th iteration, the array `rank` assigns each suffix a value such that `rank[i] < rank[j]` if and only if the first $k$ characters of suffix $i$ are lex-less than the first $k$ characters of suffix $j$, with the sentinel `-1` treated as smaller than any character.** That invariant holds at $k = 1$ because the initial ranks are character codes. It's preserved by the doubling step because the pair $(\text{rank}[i], \text{rank}[i + k])$ encodes exactly the first $2k$ characters of suffix $i$ under the previous invariant, and re-ranking by sorted-key order under that pair gives the new rank that satisfies the $2k$-character version of the invariant. Termination at $\text{rank}[\text{sa}[n - 1]] = n - 1$ means all ranks are distinct, which means the lex order is fully determined, which means `sa` is the suffix array.

For **Kasai's LCP**, the invariant is on the running `h`: at the top of iteration $i$ of the outer loop, `h` equals the length of the common prefix between `text[i:]` and `text[sa[rank[i]] - 1] + ...` — wait, that's not quite right. Let me restate it. The invariant is that when I enter iteration $i$, `h` is a *lower bound* on the LCP I'm about to compute, justified by the structural fact that chopping one character off two suffixes shrinks their LCP by at most one. The inner `while` loop extends `h` to the actual LCP by matching forward, and the `h -= 1` at the end of the iteration carries the lower bound forward to iteration $i + 1$ for free. Each value of `lcp[rank[i]]` is set to the correct LCP at the moment of assignment, because the inner loop runs until characters disagree (or one of the suffixes ends), which is the definition of LCP.

For **`find_all`**, the two binary searches compute the lower and upper bounds of the range of suffix-array entries whose suffixes have first $m$ characters equal to the pattern. Lex order's transitivity makes the binary search correct: suffixes with first $m$ characters less than the pattern form a contiguous prefix of `sa`, suffixes with first $m$ characters equal to the pattern form a contiguous middle block, and suffixes with first $m$ characters greater than the pattern form a contiguous suffix. The lower-bound search finds the boundary between the first two; the upper-bound search finds the boundary between the last two. The slice `sa[left:right]` is exactly the set of starting positions of matching suffixes, which is exactly the set of match positions in the text.

### How efficient is it?

The cost table for the suffix-array family on a text of length $n$ and a pattern of length $m$:

| Operation | Time | Extra space |
|-----------|------|-------------|
| `suffix_array_naive(text)` | $O(n^2 \log n)$ | $O(n^2)$ |
| `suffix_array(text)` | $O(n \log^2 n)$ | $O(n)$ |
| `lcp_kasai(text, sa)` | $O(n)$ | $O(n)$ |
| `find_all(text, sa, pattern)` | $O(m \log n + z)$ | $O(z)$ |
| `longest_repeated_substring(text)` | $O(n \log^2 n)$ | $O(n)$ |

The $O(n \log^2 n)$ on the prefix-doubling build comes from $O(\log n)$ doubling iterations, each doing a Python sort over $n$ pair-keys at $O(n \log n)$ cost. The proper Manber-Myers algorithm replaces each sort with a radix sort over the pair-keys at $O(n)$ per pass, giving the overall $O(n \log n)$ bound — the same bound a comparison-sort-of-suffixes would naturally hit if each comparison were $O(1)$ instead of $O(n)$.

Kasai's $O(n)$ LCP is the showcase of the family. The amortization argument is the one I sketched in the section: `h` increases at most $n$ times across the whole algorithm (each increment matches one character pair, and any specific text position can be the right endpoint of an LCP extension at most once), and `h` decreases at most $n$ times (once per text-position iteration). So the total work in the inner loop is $O(n)$, and the outer loop adds another $O(n)$ for the bookkeeping.

Pattern search is $O(m \log n)$ per query, where $m \log n$ is the cost of $O(\log n)$ binary-search steps each doing an $O(m)$ substring comparison. The plus-$z$ term is the cost of returning the $z$ matches (the final `sorted` over the slice). For typical workloads $z \ll n$, so the binary searches dominate.

Bilingually: on a megabyte-sized text, building the suffix array does about $10^6 \cdot 20^2 = 4 \cdot 10^8$ work in the prefix-doubling version — fast enough to run in a few seconds in Python, fraction of a second in C. Each subsequent pattern query at length 30 does $30 \cdot 20 = 600$ characters of work, which is essentially instantaneous. Run a million queries against the same text and you've paid the build cost once and amortized it across all of them. Compare with Aho-Corasick from chapter 28: same operational mode, but Aho-Corasick fixes the patterns at build time and lets the text vary, whereas the suffix array fixes the text at build time and lets the patterns vary. They occupy orthogonal niches.

### Is it optimal?

For suffix-array construction, the lower bound is $\Omega(n)$ — every text character must be examined to encode it into the array — and the **SA-IS** algorithm by Nong et al. (2009) achieves $O(n)$ matching that bound. My prefix-doubling implementation hits $O(n \log^2 n)$, a $\log^2 n$ factor above optimal; the original Manber-Myers algorithm with radix sort hits $O(n \log n)$, a $\log n$ factor above optimal. Both are widely used in production despite being suboptimal because their constant factors are small and their implementations are tractable, whereas SA-IS is fiddly enough that most production systems ship a non-linear variant unless they care about asymptotic performance on very large inputs.

For LCP construction, **Kasai's $O(n)$** matches the trivial $\Omega(n)$ lower bound exactly — you can't do better, and you don't need to. The algorithm is optimal.

For pattern search, $O(m \log n)$ per query is optimal *for a comparison-based search over a sorted suffix-array structure*. With auxiliary data — specifically, an **enhanced suffix array** that augments the SA + LCP with additional tables for $O(1)$ range-minimum queries — pattern search drops to $O(m)$ per query, matching the suffix-tree bound. Abouelhoda, Kurtz, and Ohlebusch (2004) is the canonical reference for that construction. I won't implement it; the bookkeeping is significant and the $\log n$ factor on top of $m$ is usually invisible in practice.

The suffix-tree alternative gives strict $O(m)$ pattern search and $O(n)$ size, but with much larger constants, harder construction, and a clumsy memory profile. The trade-off favors the suffix array in essentially every real workload — that's why the modern string-processing libraries are built on it.

Two big lessons from this chapter, and one observation about the role the suffix array plays inside the wider Codex.

**First, sort the *positions* of an object, not the object itself.** The naive suffix-array build materializes every suffix as a separate string — total memory $O(n^2)$ — and that's what makes it impractical. The smart move is to recognize that the suffixes don't need to be materialized; the algorithm only needs to *compare* them, and comparison can be expressed in terms of the underlying text and a few index lookups. So I sort positions (which take $O(n)$ memory) and use the positions to do comparisons against the text on the fly. This pattern shows up all over the book: chapter 5's argsort takes a sequence and returns the indices in sorted order rather than reshuffling the values; chapter 21's segment tree stores aggregates of array slices rather than the slices themselves; chapter 28's Aho-Corasick stores trie nodes representing patterns rather than the patterns inline. When you find yourself about to materialize an exponential set of derived objects to sort or process, ask whether you can index into them on the fly instead.

**Second, the right processing order can collapse quadratic work to linear.** Kasai's algorithm is the cleanest example I've ever seen of this lesson. The naive LCP construction processes adjacent sorted-suffix pairs in the order they appear in the suffix array; that's $O(n)$ pairs, each costing $O(n)$ to compute, total $O(n^2)$. Kasai processes the same set of pairs in *text-position order* instead, which lets the LCP from the previous text position seed the LCP for the next one with a one-character drop. Same outputs, different order, asymptotically less work. The pattern shows up elsewhere — chapter 26's Boyer-Moore preprocesses patterns in reverse character order to enable forward skipping, KMP's failure function builds in pattern-prefix-length order rather than left-to-right — and the meta-lesson is that when you have an apparently-quadratic loop nest, look at the dependency structure between iterations and see whether reordering them creates carry-over opportunities.

The chapter sits at the boundary between Part IV's pattern-matching arc and the broader string-indexing world that opens up after it. Chapters 23–28 all answered the question "given these patterns, find them in this text" with progressively more sophisticated machinery. This chapter answered a different question — "given this text, prepare it so any pattern query is fast" — and that pivot is what the suffix array exists for. Full-text search engines, biological sequence aligners, the Burrows-Wheeler transform underlying `bzip2` and the FM-index, plagiarism detectors looking for long shared substrings, document deduplication systems: every one of those applications builds a suffix-array variant once and runs millions of queries against it. The pattern-matching arc of Part IV led you here, and the door opens onto a much wider field of string algorithms that all start with "first, build the suffix array of $T$."

## Notes and further reading

The suffix array was introduced by Udi Manber and Gene Myers in their 1993 paper "Suffix arrays: A new method for on-line string searches," published in *SIAM Journal on Computing* 22(5):935–948. The paper presents the prefix-doubling algorithm (with radix sort) and the $O(m \log n)$ pattern-search procedure I've implemented here. The motivation was as an alternative to the suffix tree — Manber and Myers wanted a structure with smaller constant-factor memory cost and a simpler implementation, while preserving the asymptotic indexing benefits.

Kasai's linear-time LCP algorithm appears in Toru Kasai, Gunho Lee, Hiroki Arimura, Setsuo Arikawa, and Kunsoo Park's 2001 paper "Linear-time longest-common-prefix computation in suffix arrays and its applications," published in *Proceedings of CPM 2001*, LNCS 2089, pp. 181–192. The paper is short and worth reading directly — the amortized-cost argument for the $O(n)$ bound is presented cleanly there, and the paper also introduces several of the LCP-based applications I gestured at (longest repeated substring, longest common substring, etc.).

The $O(n)$ suffix-array construction algorithm I named — **SA-IS** — is from Ge Nong, Sen Zhang, and Wai Hong Chan's 2009 paper "Linear suffix array construction by almost pure induced-sorting," published in the *2009 Data Compression Conference* (DCC '09), pp. 193–202. It's the modern standard for production suffix-array construction; Yuta Mori's `sa-is` C implementation is the reference. Earlier linear-time algorithms — Kärkkäinen and Sanders's **DC3** (2003), and Kim, Sim, Park, and Park's **KSPP** (2003) — are also worth knowing about as historical context.

CLRS does not cover suffix arrays directly. Sedgewick and Wayne's *Algorithms* (4th ed.) discusses them briefly in §6.4. The modern textbook reference is Maxime Crochemore, Christophe Hancart, and Thierry Lecroq's *Algorithms on Strings* (Cambridge University Press, 2007), which devotes chapter 4 to suffix arrays and chapter 5 to the related suffix tree and suffix automaton — read those three chapters together for the full landscape. Mohamed Abouelhoda, Stefan Kurtz, and Enno Ohlebusch's 2004 paper "Replacing suffix trees with enhanced suffix arrays" (*Journal of Discrete Algorithms* 2(1):53–86) is the canonical reference for the enhanced-suffix-array construction that achieves suffix-tree-equivalent query times.

Applications I touched on: the **Burrows-Wheeler transform** by Michael Burrows and David Wheeler (1994 technical report, later published in *Communications of the ACM*) is computed by sorting all rotations of the input, which turns out to be equivalent to constructing the suffix array of `text + "$"` and reading off the previous character at each suffix-array position. The BWT is what powers `bzip2` compression and the FM-index used by `bowtie` and `bwa` for short-read alignment in genomics. The **FM-index** itself was introduced by Paolo Ferragina and Giovanni Manzini in their 2000 paper "Opportunistic data structures with applications" (*Proc. FOCS 2000*), and it provides $O(m)$ pattern-counting queries with $O(n H_k(T))$ space — where $H_k(T)$ is the $k$-th order empirical entropy of $T$ — which is sublinear in the text size for compressible inputs.

In the next chapter I'll leave string indexing and turn to a different kind of string problem entirely: not "where do these patterns appear?" but "how *similar* are two strings to each other?" Edit distance — the minimum number of insertions, deletions, and substitutions to turn one string into another — is the question, and dynamic programming over a 2D table is the answer. That chapter closes Part IV.
