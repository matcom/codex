# Failing forward, never backward

At the end of chapter 24 I left you with a confession. The DFA I built scans the text in $\Theta(n)$ and never backtracks — that part is perfect — but the price was a transition table of $\Theta(m \cdot |\Sigma|)$ entries, built in $O(m^3 \cdot |\Sigma|)$ time by a triple-nested loop I made no attempt to defend. For a pattern of ten characters over the alphabet of English text, the table fits in a few kilobytes; for a thousand-character pattern over a Unicode-flavored alphabet of 10,000 code points, the table is ten million slots and the construction is several orders of magnitude past defensible. Most of those slots, if you stared at the table from chapter 24 long enough, are answering the same question: "I just mismatched — how much of my previous progress is still salvageable?" The Knuth-Morris-Pratt algorithm — KMP — is what you get when you store the answer to that question *once per state* instead of once per state-character pair.

**The failure function tells you where to resume; the text pointer never moves backward.** That sentence is the entire algorithm in compressed form. Failure function, $m$ integers. Text pointer, one variable that strictly increases. KMP isn't a different algorithm from chapter 24's DFA — it's the same DFA stored in $\Theta(m)$ space instead of $\Theta(m \cdot |\Sigma|)$, and the chapter's closing section reconstructs the DFA cell-by-cell from the failure function to prove the compression is lossless.

## The DFA's wasted dimension

Look back at the transition table I built in chapter 24 for the pattern `"ababa"`. Six states, two columns (one per alphabet character), twelve entries total. Now ask a question I deliberately didn't ask in chapter 24: for any state $q$ and any character $c$, what are the possible values of $\delta(q, c)$? There are exactly two interesting cases.

Either $c$ equals $P[q]$ — the next character of the pattern — in which case $\delta(q, c) = q + 1$, the obvious extension. Or $c$ doesn't equal $P[q]$, in which case $\delta(q, c)$ is "the next state I'd reach from *some smaller state* on character $c$." The interesting work is all in the second case. In the first case, the table is storing the constant $q + 1$ for one specific character per state and ignoring the rest. In the second case, the table is storing the same answer many times — every state's mismatch behaviour on a particular character collapses down to "fall back to the longest prefix-of-pattern that's also a suffix of what I just had, then try again."

That collapse is the redundancy. If I knew, for each state $q$, the single number "what's the longest proper prefix of $P[0..q-1]$ that's also a suffix of $P[0..q-1]$?", I could reconstruct the entire mismatch column on the fly. I'd never need to store $\delta(q, c)$ explicitly for $c \ne P[q]$ — I'd compute it by chaining fallbacks until either the character matches or I hit state zero.

That single number, one per state, is the failure function.

## The failure function

Let me define it precisely. For a pattern $P$ of length $m$, the **failure function** is an array $\pi$ of length $m$, where

$$\pi[i] = \text{the length of the longest } \textit{proper} \text{ prefix of } P[0..i] \text{ that is also a suffix of } P[0..i].$$

The word *proper* is doing work — the prefix has to be strictly shorter than $P[0..i]$ itself. Otherwise $\pi[i]$ would always be $i + 1$, which is useless. By convention $\pi[0] = 0$: the only proper prefix of a single-character string is the empty string, whose length is zero.

That definition takes a few rereadings on the first encounter. Let me make it tangible on `"ababa"`. I'll walk through each $i$ from $0$ to $4$ and name the longest proper prefix-that-is-also-a-suffix.

At $i = 0$, the substring is `"a"`. Its only proper prefix is `""`, length 0. So $\pi[0] = 0$.

At $i = 1$, the substring is `"ab"`. Proper prefixes are `""` and `"a"`. Neither is a suffix of `"ab"` other than the empty one, because the only suffix of length 1 is `"b"`, and the empty suffix is, by definition, a suffix of every string. So the longest proper prefix-that-is-also-a-suffix is `""`, length 0. $\pi[1] = 0$.

At $i = 2$, the substring is `"aba"`. Proper prefixes: `""`, `"a"`, `"ab"`. The suffixes of `"aba"` are `""`, `"a"`, `"ba"`, `"aba"`. The intersection is $\{$ `""`, `"a"` $\}$ — the empty string and `"a"`. The longest is `"a"`, length 1. So $\pi[2] = 1$.

At $i = 3$, the substring is `"abab"`. Proper prefixes: `""`, `"a"`, `"ab"`, `"aba"`. Suffixes: `""`, `"b"`, `"ab"`, `"bab"`, `"abab"`. The intersection is $\{$ `""`, `"ab"` $\}$. The longest is `"ab"`, length 2. So $\pi[3] = 2$.

At $i = 4$, the substring is `"ababa"`. Proper prefixes: everything up to `"abab"`. Suffixes: `""`, `"a"`, `"ba"`, `"aba"`, `"baba"`, `"ababa"`. The intersection is $\{$ `""`, `"a"`, `"aba"` $\}$. The longest is `"aba"`, length 3. So $\pi[4] = 3$.

Failure function for `"ababa"` is therefore $[0, 0, 1, 2, 3]$. Read it as a hint sheet: if I matched four characters of `"ababa"` and the fifth disagrees, $\pi[3] = 2$ tells me my recent two characters were `"ab"`, which is a prefix of the pattern, so I should resume comparing from $P[2]$ — saving two characters of re-scanning. That hint is what the brute force in chapter 23 was throwing away at every shift.

## Computing the failure function

The algorithm that computes $\pi$ is, beautifully, KMP running on the pattern itself, against itself shifted by one. I'm walking $i$ from $1$ to $m - 1$, maintaining a variable $k$ that's the current "candidate length of the matching prefix" — exactly the same kind of state the matching loop will maintain when it walks the text.

Here's the function.

```python {export=src/codex/strings/kmp.py}
def failure_function(pattern: str) -> list[int]:
    m = len(pattern)
    pi = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and pattern[k] != pattern[i]:
            k = pi[k - 1]
        if pattern[k] == pattern[i]:
            k += 1
        pi[i] = k
    return pi
```

Three things happen per iteration. First, the `while` loop falls back: as long as my current candidate length $k$ is positive and the character at position $k$ of the pattern doesn't match the character at position $i$, I shrink $k$ to $\pi[k - 1]$ — the next-best candidate. Second, after the loop, if the characters now match, I extend $k$ by one. Third, I record $k$ as $\pi[i]$ and move on.

Let me trace on `"ababa"` so you can watch $k$ evolve. Start with $k = 0$ and $\pi = [0, 0, 0, 0, 0]$.

At $i = 1$: $k = 0$, the `while` doesn't enter (the guard $k > 0$ fails immediately). Is `pattern[0] == pattern[1]`? `'a' == 'b'`? No. So $k$ stays at 0. $\pi[1] = 0$.

At $i = 2$: $k = 0$ still. The `while` skips. Is `pattern[0] == pattern[2]`? `'a' == 'a'`? Yes. So $k$ becomes 1. $\pi[2] = 1$.

At $i = 3$: $k = 1$. Is `pattern[1] == pattern[3]`? `'b' == 'b'`? Yes. So the `while` doesn't enter (the second clause is false). $k$ becomes 2. $\pi[3] = 2$.

At $i = 4$: $k = 2$. Is `pattern[2] == pattern[4]`? `'a' == 'a'`? Yes. The `while` doesn't enter. $k$ becomes 3. $\pi[4] = 3$.

Final $\pi = [0, 0, 1, 2, 3]$. Matches the hand derivation above, character-for-character.

```python
from codex.strings.kmp import failure_function

print(f"failure_function('ababa') = {failure_function('ababa')}")
print(f"failure_function('abracadabra') = {failure_function('abracadabra')}")
print(f"failure_function('aaaa') = {failure_function('aaaa')}  (every prefix is a suffix)")
print(f"failure_function('abcd') = {failure_function('abcd')}  (no overlaps anywhere)")
```

You can see the structure in all four. `"aaaa"` has $\pi = [0, 1, 2, 3]$ because every prefix is also a suffix — the pattern is its own degenerate cycle. `"abcd"` has $\pi = [0, 0, 0, 0]$ because no proper prefix of any of its substrings matches any suffix — there's no internal repetition to fall back on. `"abracadabra"` is the one I want to look at more carefully in a moment, because it's the canonical demo.

Bilingually: the loop reads $i$ from 1 to $m - 1$ exactly once, and $k$ is bounded above by $i$, so the amortized cost is $O(m)$. Each iteration either increments $k$ (at most $m$ times total across the whole loop) or shrinks $k$ via the `while` (each shrink reduces $k$ by at least one, and $k$ can only shrink as many times as it has been incremented). That amortized accounting gives the entire failure-function build in linear time — a factor of $m^2 \cdot |\Sigma|$ improvement over chapter 24's `_delta`-by-brute-force.

## The matching loop

Now the matching algorithm itself. It looks structurally identical to the failure-function build — same `while`/`if`/extend skeleton — but operates on the text instead of the pattern.

```python {export=src/codex/strings/kmp.py}
def find(text: str, pattern: str) -> int | None:
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
    if m > n:
        return None
    pi = failure_function(pattern)
    j = 0
    for i in range(n):
        while j > 0 and pattern[j] != text[i]:
            j = pi[j - 1]
        if pattern[j] == text[i]:
            j += 1
        if j == m:
            return i - m + 1
    return None
```

Two invariants do all the work. The first: **the text pointer `i` runs once over the text, left to right, and never decreases.** That's the literal text of the `for` loop — there's no inner mechanism that ever resets or rewinds $i$. Every character of the text is read exactly once, and the entire scan is therefore $\Theta(n)$, period. The brute force from chapter 23 had nothing like this — its inner loop re-read text characters at every shift.

The second invariant: **on a mismatch, `j` falls back via $\pi$ to the longest pattern prefix that's still salvageable as a suffix of the text I've just read.** That's the `while` loop's job. The line `j = pi[j - 1]` says "I just matched $j$ characters, the next one disagrees, so my recent text suffix of length $j$ equals $P[0..j-1]$, and the longest proper prefix of that string that's also a suffix is $\pi[j - 1]$ characters long. Resume the comparison from there." After enough fallbacks, either the next character of the pattern at the new $j$ matches the current text character (and the algorithm extends), or $j$ has fallen all the way to zero (and the algorithm gives up on the current text character and moves on).

When $j$ reaches $m$, the entire pattern has matched, ending at text position $i$. The match started at $i - m + 1$. For `find`, I return that index immediately.

`find_all` is the same loop, with two differences: I append the match index instead of returning, and on $j == m$ I set $j = \pi[m - 1]$ instead of zero. That's the same trick chapter 24's `find_all` used — the DFA's accept state has its own outgoing transitions, and the failure function encodes them. Setting $j$ to $\pi[m - 1]$ keeps the longest possible amount of context alive for overlapping matches.

```python {export=src/codex/strings/kmp.py}
def find_all(text: str, pattern: str) -> list[int]:
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []
    pi = failure_function(pattern)
    matches: list[int] = []
    j = 0
    for i in range(n):
        while j > 0 and pattern[j] != text[i]:
            j = pi[j - 1]
        if pattern[j] == text[i]:
            j += 1
        if j == m:
            matches.append(i - m + 1)
            j = pi[m - 1]
    return matches
```

Eight lines of loop body. No backtracking on the text. One bounded fallback chain per text character. The total work across all text positions is $\Theta(n)$ by the same amortized argument that bounded the failure-function build: $j$ increments at most $n$ times total, and the `while` decrements it, so the total number of decrement steps across the whole scan is at most $n$ too. Linear in the text length, independent of the pattern's internal structure.

## Running on the canonical text

Time to verify everything works on the same input I've been using since chapter 23. Pattern `"ain"` on the canonical text.

```python
from codex.strings.kmp import find, find_all

TEXT = "the rain in spain stays mainly in the plain"

idx = find(TEXT, "ain")
print(f"first match of 'ain' at index {idx} — same answer as ch 23 and ch 24")

all_ain = find_all(TEXT, "ain")
print(f"all matches of 'ain': {all_ain}  (four occurrences, identical to ch 23 and ch 24)")

miss = find(TEXT, "frog")
print(f"searching for 'frog': {miss}  (no 'f' anywhere — j stays at 0 throughout)")
```

Four matches at 5, 14, 25, 40 — the same answer chapter 23's brute force and chapter 24's DFA produced. KMP did it in $\Theta(n)$ scan time with $\Theta(m)$ preprocessing instead of the DFA's $\Theta(m \cdot |\Sigma|)$ preprocessing. Same answer, cheaper preparation.

Now the overlap case that made the DFA's accept-state transitions interesting in chapter 24 — pattern `"ababa"` on `"ababababa"`.

```python
from codex.strings.kmp import find_all

matches = find_all("ababababa", "ababa")
print(f"find_all('ababababa', 'ababa') = {matches}  (three overlapping matches: 0, 2, 4)")
```

Three matches at 0, 2, 4 — exactly what chapter 24's DFA produced for the same input. The mechanism is different (a failure-function fallback to $\pi[4] = 3$ on match versus an explicit DFA transition out of state 5), but the externally observable behaviour is identical. That's the cross-chapter consistency I want — KMP and the DFA agree on every input, by design.

## abracadabra: the canonical demo

The pattern `"abracadabra"` is the canonical KMP demo for a reason. It's long enough to have non-trivial internal structure (the prefix `"abra"` reappears as the suffix), short enough to trace by hand, and recognizable enough that the matching examples are memorable. Its failure function is $[0, 0, 0, 1, 0, 1, 0, 1, 2, 3, 4]$ — let me walk through what those numbers mean.

```python
from codex.strings.kmp import failure_function

pattern = "abracadabra"
pi = failure_function(pattern)
print(f"pattern = {pattern!r}")
print(f"pi      = {pi}")
print()
print("by index:")
for i, val in enumerate(pi):
    prefix = pattern[:i + 1]
    overlap = pattern[:val] if val > 0 else '""'
    print(f"  pi[{i:>2}] = {val}   substring {prefix!r:>14}   longest proper prefix=suffix: {overlap}")
```

The interesting indices are 7 through 10. At $i = 7$, the substring is `"abracada"` — eight characters — and the longest proper prefix that's also a suffix is `"a"`, length 1. At $i = 8$, the substring is `"abracadab"` and the answer is `"ab"`, length 2. At $i = 9$, the substring is `"abracadabr"` and the answer is `"abr"`, length 3. At $i = 10$, the full pattern `"abracadabra"`, and the answer is `"abra"`, length 4 — the four-character prefix that also closes out the pattern.

That last value, $\pi[10] = 4$, is what `find_all` uses after a successful match. After reading the full pattern, the algorithm keeps four characters of context alive — the trailing `"abra"` — instead of restarting from scratch. If the text continues with `"cadabra..."`, those four characters are immediately reusable as the prefix of a second match.

Let me trace one mismatch fallback by hand, so you can see the failure function in action. Suppose I'm scanning the text `"abracadabrx"` (note the `'x'` at the end where `'a'` should be) with pattern `"abracadabra"`.

At text positions 0 through 9, the algorithm extends $j$ once per text character: $j$ goes $1, 2, 3, 4, 5, 6, 7, 8, 9, 10$. Now at text position 10, the text character is `'x'` but `pattern[10]` is `'a'`. Mismatch. The `while` enters: $j = \pi[9] = 3$. Is `pattern[3] == text[10]`? `pattern[3]` is `'a'`. Still `'x'`. Mismatch again. Fall back: $j = \pi[2] = 0$. Loop exits (because $j$ is no longer positive). Now check if `pattern[0] == text[10]`: `'a' == 'x'`? No. $j$ stays at 0. Move on to text position 11.

What just happened: the algorithm matched ten characters of the pattern, mismatched on the eleventh, and the failure function let it skip directly to "what if my recent suffix of length three (`"abr"`) is the start of a new match?" without re-scanning any of those three characters in the text. Two fallbacks total, then a clean reset. That skipping is the KMP win, made visible.

```python
from codex.strings.kmp import find, find_all

text = "abracadabra is a magic abracadabra"
matches = find_all(text, "abracadabra")
print(f"matches of 'abracadabra' in {text!r}: {matches}")
print(f"first match index: {find(text, 'abracadabra')}")
```

Two matches at positions 0 and 23. KMP reads each of the 34 text characters exactly once and reports both. The failure-function fallbacks happen invisibly inside the inner `while`, never costing more than amortized constant time per text character.

## KMP and the DFA are the same machine

Now the punchline. I claimed at the top of this chapter that KMP is the DFA from chapter 24 in a smaller storage format, and I want to make that claim concrete by reconstructing the entire DFA from the failure function alone, cell by cell, and verifying that the two tables agree everywhere.

The reconstruction rule is short. For a pattern $P$ of length $m$, the DFA transition $\delta(q, c)$ — defined for states $0 \le q \le m$ and characters $c$ — can be written recursively using only $\pi$ and the pattern itself.

For $q = 0$: $\delta(0, c) = 1$ if $P[0] = c$, else $0$. (Either the first character matches, or it doesn't.)

For $0 < q < m$: $\delta(q, c) = q + 1$ if $P[q] = c$, else $\delta(\pi[q-1], c)$. (Either the next pattern character matches and I extend by one, or I fall back to the failure-function state and recursively ask the same question there.)

For $q = m$ (the accept state, which has no $P[m]$): $\delta(m, c) = \delta(\pi[m-1], c)$. (After accepting, I fall back to the longest proper-prefix-suffix and continue from there.)

That recursion always terminates because $\pi[q-1] < q$ — each recursive step strictly decreases $q$ — and the base case $q = 0$ is non-recursive.

Here's the function that implements that rule.

```python
def dfa_transition_via_failure(pattern: str, pi: list[int], q: int, c: str) -> int:
    m = len(pattern)
    if q < m and pattern[q] == c:
        return q + 1
    if q == 0:
        return 0
    return dfa_transition_via_failure(pattern, pi, pi[q - 1], c)
```

I'm letting the recursion bottom out via `pi[q - 1]` chains. The recursion depth is bounded by the chain length of repeated failure-function applications starting from $q$, which is at most $O(\log m)$ on most patterns and at most $O(m)$ in the worst case (a pathological pattern like `"aaaa..."`). For the patterns I'm running it on here, the recursion is shallow.

Now let me build chapter 24's DFA on `"ababa"` and the KMP failure function on `"ababa"`, then reconstruct the full DFA from the failure function and compare cell-by-cell against the original.

```python
from codex.strings.automaton import build_dfa
from codex.strings.kmp import failure_function

pattern = "ababa"
transitions, accept = build_dfa(pattern)
pi = failure_function(pattern)
alphabet = "ab"

print(f"pattern = {pattern!r}")
print(f"pi (failure function) = {pi}")
print()
print(f"reconstructing DFA from pi, comparing to build_dfa output:")
print(f"  state | char | build_dfa | via_pi | match")
print(f"  ------+------+-----------+--------+------")

all_match = True
for q in range(len(pattern) + 1):
    for c in alphabet:
        dfa_val = transitions[q].get(c, 0)
        pi_val = dfa_transition_via_failure(pattern, pi, q, c)
        ok = dfa_val == pi_val
        all_match = all_match and ok
        print(f"    {q}   |  {c}   |     {dfa_val}     |   {pi_val}    |  {ok}")

print()
print(f"all cells agree: {all_match}")
```

Every cell matches. The DFA built in chapter 24 by brute-force enumeration of suffix-prefix overlaps and the DFA reconstructed here from KMP's failure function are character-for-character the same table. The failure function loses no information about the DFA — it's a different encoding of the same object.

Run the same check on `"abracadabra"` for a more substantial example.

```python
from codex.strings.automaton import build_dfa
from codex.strings.kmp import failure_function

pattern = "abracadabra"
transitions, accept = build_dfa(pattern)
pi = failure_function(pattern)
alphabet = "abcdr"  # the characters that actually appear in the pattern

mismatches = 0
for q in range(len(pattern) + 1):
    for c in alphabet:
        dfa_val = transitions[q].get(c, 0)
        pi_val = dfa_transition_via_failure(pattern, pi, q, c)
        if dfa_val != pi_val:
            mismatches += 1

cells = (len(pattern) + 1) * len(alphabet)
print(f"pattern = {pattern!r}")
print(f"DFA cells checked: {cells}")
print(f"mismatches between build_dfa and dfa_transition_via_failure: {mismatches}")
```

Sixty cells checked, zero mismatches. The compression is exact on every pattern I've tried, and the chapter's claim is now verified by code: KMP and the DFA are the same machine.

The storage difference is dramatic. The DFA for `"abracadabra"` over its 5-character alphabet has $12 \cdot 5 = 60$ integer slots. The failure function has $11$ integer slots. That's a five-and-a-half-fold reduction, and it grows with $|\Sigma|$ — the larger the alphabet, the bigger the relative win for KMP. The trade-off, of course, is that each text character now costs a bounded number of failure-pointer chases instead of a single table lookup. In practice that overhead is small: the amortized fallback cost across the whole scan is $\Theta(n)$, same as the DFA's lookup cost.

## The three questions, applied

### Is it correct?

I need two invariants. The first is on the failure function itself: **after `failure_function` returns, $\pi[i]$ equals the length of the longest proper prefix of $P[0..i]$ that is also a suffix of $P[0..i]$, for every $i \in [0, m-1]$.** That follows by induction on $i$. At $i = 0$, $\pi[0] = 0$ is correct by convention and by the lack of any proper prefix. For $i > 0$, suppose $\pi[0..i-1]$ are all correct. The variable $k$ entering iteration $i$ equals $\pi[i-1]$ — the longest proper prefix-suffix of $P[0..i-1]$. If $P[k] == P[i]$, then $P[0..k]$ is a prefix-suffix of $P[0..i]$ of length $k + 1$, and you can show it's the longest such by contradiction (any longer one would imply, after dropping the last character, a prefix-suffix of $P[0..i-1]$ longer than $k$, which contradicts the induction hypothesis). If $P[k] \ne P[i]$, the fallback chain $k = \pi[k-1]$ enumerates candidate shorter prefix-suffixes in decreasing length until one extends or none do, and the first extension is the answer.

The second invariant is on the matching loop: **at the top of each iteration of the `for i` loop, the variable $j$ equals the length of the longest prefix of $P$ that is also a suffix of $T[0..i-1]$.** This is the same invariant the DFA from chapter 24 maintained on its `state` variable — exactly the same. The `while` loop's role is to maintain it across a mismatch: starting from "I just matched $j$ characters and the next one disagrees," the longest still-salvageable prefix is the longest proper prefix-suffix of $P[0..j-1]$ — which is $\pi[j-1]$ by definition. Chaining until either the character matches or $j$ reaches zero finds the longest prefix that the new character can extend.

When $j$ reaches $m$, the invariant says my recent text suffix of length $m$ equals $P$, i.e., the pattern just finished matching at position $i$. Reporting $i - m + 1$ as the match start is then correct by arithmetic. `find_all` is correct because setting $j = \pi[m-1]$ after a match preserves the invariant for the next iteration — the longest proper prefix-suffix of $P$ is exactly the longest prefix that's still alive as a candidate continuation.

### How efficient is it?

The failure function builds in $\Theta(m)$ amortized time and $\Theta(m)$ space. The matching loop runs in $\Theta(n)$ amortized time and $O(m)$ extra space (for $\pi$). Total time for `find` or `find_all` is $\Theta(n + m)$; total space is $\Theta(m)$ for the failure function plus $O(k)$ for the output if you're collecting matches.

The amortized argument is the same on both halves. In `failure_function`, the variable $k$ is incremented at most $m - 1$ times (once per iteration when the character matches), and the `while` decrements it — each decrement strictly reduces $k$, and $k$ can only decrease as many times as it has been increased. So total `while` work across the whole function is $O(m)$, and the outer loop is $O(m)$. In `find`, the same accounting holds with $j$ in place of $k$ and $n$ in place of $m$.

Bilingually: searching a million-character text for a hundred-character pattern costs about a million read operations for the scan and about a hundred read operations for the preprocessing. The DFA from chapter 24 would have done the same million-read scan but with about a million preprocessing operations on a 26-letter alphabet — a ten-thousand-fold preprocessing reduction for KMP, with the same scan time. For a single search in a large text, the preprocessing savings dominate; for repeated searches with the same pattern across many texts, the savings compound the way they do for the DFA, because the failure function is computed once and reused.

### Is it optimal?

For exact pattern matching, $\Omega(n)$ is the lower bound on the text scan — every character has to be read to be sure the pattern doesn't appear at that position. KMP matches that bound and the DFA matches that bound; they're both worst-case optimal on the scan.

The preprocessing is more nuanced. KMP's $\Theta(m)$ preprocessing is information-theoretically tight: any algorithm that wants to use the structure of the pattern at scan time needs to spend $\Omega(m)$ time reading the pattern at least once. Galil's 1979 paper proved that $\Theta(m)$ preprocessing combined with a $\Theta(n)$ scan is optimal even in a stricter delay-bounded model, where every text character is required to be processed in $O(1)$ worst-case time rather than amortized. KMP's amortized $O(1)$-per-character bound can be tightened to a worst-case $O(1)$-per-character bound with a small modification, which is what Galil's variant achieves.

So KMP is optimal for the exact-matching problem in essentially every formal sense — preprocessing time, scan time, total space — except for the constant factor in the scan, where the brute force from chapter 23 still wins on cache-friendly hardware whenever the average case is what matters. The next chapter starts answering "what if I'm willing to do *more* preprocessing in exchange for *sublinear* scanning?" — which is the door Boyer-Moore opens.

Two lessons I want you to carry forward.

**First, the right representation can collapse an algorithm down to one variable.** Chapter 24's DFA stored a two-dimensional table — state by character — and chapter 25's KMP stores a one-dimensional array, the failure function. Same algorithm, same scan-time behaviour, dramatically less space. The collapse happened because most of the table's entries were answering the same question ("on a mismatch, what's the longest still-salvageable prefix?") and that question has a one-number answer per state. When you see a table whose rows are dense but whose entries collapse along a single axis, you have a candidate for a sparse-encoding rewrite. Compilers, parsers, regular-expression engines, and string-matching libraries all live on variants of this idea.

**Second, an algorithm that "never goes backward" deserves a closer look.** The text pointer in KMP is a one-way variable: it strictly increases over the scan, and that monotonicity is the entire reason the scan is $\Theta(n)$. Whenever you can convert a re-scan into a stay-and-fall-back, you turn a multiplicative cost into an additive one. This pattern recurs across the whole book — the Knuth-Morris-Pratt matcher, the linear-time amortized analyses of dynamic arrays, the union-find with path compression, the Fibonacci-heap decrease-key — every one of them is a story about replacing repeated traversal with a smarter local-state update. KMP is the cleanest example of the pattern, which is why it's a fixture of algorithms curricula.

## Notes and further reading

KMP was introduced in Knuth, Morris, and Pratt's 1977 paper "Fast Pattern Matching in Strings" in *SIAM Journal on Computing* 6(2):323–350. The paper proves both correctness and the linear-time scan bound using an amortized potential argument — the technique I sketched in the "How efficient is it?" section is theirs, simplified. The historical context is worth knowing: Morris and Pratt independently invented the algorithm in 1970, Knuth saw a connection to automaton theory and contributed the DFA construction that chapter 24 covers, and the three of them published jointly. The DFA-first presentation I've been using over the past two chapters mirrors Knuth's own preferred exposition.

CLRS section 32.4 covers KMP directly — same algorithm, slightly different notation. Sedgewick and Wayne's *Algorithms* (4th ed.) section 5.3 covers KMP without the DFA detour, presenting the failure function as a stand-alone trick rather than as a compression of the DFA. I prefer the DFA-first path because it makes the failure function feel inevitable, but the failure-function-first path is the more common textbook treatment and worth seeing for contrast.

Zvi Galil's 1979 paper "On Improving the Worst-Case Running Time of the Boyer-Moore String Matching Algorithm" in *Communications of the ACM* 22(9):505–508 — confusingly titled, given the topic — also contains the optimization of KMP that achieves true $O(1)$-per-character delay rather than the amortized bound. The technique is to precompute, in addition to the failure function, a second table called the "delay function" or "next function" that handles the mismatch case in true constant time. Most production KMP implementations don't bother — amortized is fast enough — but the result is theoretically clean.

For deeper reading on the connection between automata and string matching, Crochemore, Hancart, and Lecroq's *Algorithms on Strings* (Cambridge 2007) is the modern reference. The book treats KMP, the DFA construction from chapter 24, Aho-Corasick (chapter 28), and the entire family of suffix-prefix algorithms as variations on a single theme — the same theme I've been pointing at across these last three chapters.

In the next chapter I'll change the lens completely. Instead of scanning the text left to right and using preprocessing to skip work after a mismatch, I'll scan each window right-to-left and use preprocessing to skip *entire windows* on a mismatch — the Boyer-Moore algorithm, whose best case beats $\Theta(n)$ by reading only a fraction of the text characters and whose worst case is the question that motivated Galil's paper.
