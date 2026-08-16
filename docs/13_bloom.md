# Remembering a set without remembering its members

A Bloom filter is a data structure that answers "is this element in my set?" with two possible outputs: *definitely not*, with perfect confidence, or *probably yes*, with a tunable false-positive rate. For a million-element set you can build one in about a megabyte and a half of memory, with a false-positive rate below 1%. The same set stored in a hash table from the last chapter would cost you tens of megabytes, because each entry has to hold the key itself. The Bloom filter doesn't hold the keys at all. It just holds enough information to *recognize* them when they come back.

That trade — accepting probabilistic answers in exchange for vastly less memory — is what makes Bloom filters useful in the kinds of places where memory is genuinely the bottleneck. Web crawlers use them to remember which URLs they've already fetched without storing a hash table of every URL. Databases use them to skip disk reads when a query's key is definitely not in the table. Distributed systems use them to summarize what's on each node so other nodes can avoid expensive remote lookups for keys that aren't there.

**The price of compression is doubt.** A Bloom filter compresses a set by losing the ability to enumerate its members; that loss is what buys the space efficiency. You can't ask "what's in you?" You can only ask "is this in you?" — and the answer has a known error rate on the side that's allowed to be wrong. A bit array of $m$ bits plus $k$ hash functions yields the false-positive formula $\varepsilon = (1 - e^{-kn/m})^k$, from which optimal $k$ and $m$ fall out in closed form.

## A million keys, a megabyte of bits

A hash table from chapter 12 storing $n$ string keys costs roughly $\Theta(n \cdot \overline{|k|})$ memory, where $\overline{|k|}$ is the average key length in bytes. For URLs that's commonly 50–200 bytes per entry, plus the per-entry pointer overhead of the hash-table backing. A million URLs is tens of megabytes. A billion URLs — the kind of set a web crawler accumulates — is tens of gigabytes, which doesn't fit in RAM on a normal machine.

A Bloom filter for the same set, at the same 1% false-positive rate, costs $\approx 1.44 \cdot n \cdot \log_2(1/\varepsilon)$ bits, independent of the key length. For a million URLs at 1% FP rate, that's $1.44 \times 10^6 \times \log_2(100) \approx 9.6$ million bits, or about 1.2 megabytes. For a billion URLs, about 1.2 gigabytes. Two orders of magnitude smaller than the hash-table equivalent. What you give up: the ability to enumerate the keys you put in, and the certainty of *positive* answers. Negatives stay definite.

**No false negatives** is the guarantee that lets the structure be useful as a pre-filter (*"the cache definitely doesn't have this, don't bother checking it"*) or as a one-sided certificate (*"this URL might already be in the crawler queue, schedule a real check before adding it again"*). You wrap a Bloom filter around an expensive lookup and spend constant time plus a few bits of memory to avoid the expensive call most of the time. The 1% of false positives mean you do the real lookup anyway in those rare cases.

## One bit array, $k$ hashes

The structure has two parts: a bit array of $m$ bits (all initially zero), and $k$ independent hash functions $h_1, h_2, \ldots, h_k$, each mapping a key to a position in $\{0, 1, \ldots, m-1\}$. To add an item $x$, compute all $k$ hash positions and set those bits to 1. To check whether $x$ is present, compute the same $k$ positions and check whether *all* of them are 1.

If any of the $k$ bits is 0, the answer is *definitely-not*: if $x$ had been added, all $k$ of its bits would have been set, and zero of them would still be zero. If all $k$ are 1, the answer is *probably-yes*: those bits might all be 1 because $x$ was added, or because other items collectively set the same bits. The second case is a false positive, and its probability is what the next section computes.

The "$k$ independent hash functions" requirement is awkward in practice. You'd have to implement $k$ separate hash functions and tune them not to be correlated. The textbook trick (Kirsch and Mitzenmacher, 2006) is that you only need *two* independent hash functions $h_1$ and $h_2$. Then $h_i(x) = h_1(x) + i \cdot h_2(x) \pmod m$ for $i = 0, 1, \ldots, k-1$ behaves indistinguishably from $k$ independent hashes for the Bloom-filter analysis. The chapter-12 double-hashing trick, repurposed.

## Why $\varepsilon = (1 - e^{-kn/m})^k$

Walk through the analysis slowly. After inserting $n$ items, each setting $k$ bits, the bit array has been hit by a total of $nk$ hash positions. Assuming the hashes are independent and uniform, the probability that any *one specific* bit is *still zero* after those $nk$ writes is:

$$\Pr[\text{bit still 0}] = \left(1 - \frac{1}{m}\right)^{nk} \approx e^{-nk/m}$$

The approximation uses $\lim_{m \to \infty} (1 - 1/m)^{m} = 1/e$. For Bloom filters where $m$ is in the thousands at minimum, the gap is below $1/m$ and you can read $\approx$ as $=$.

Now ask the probability that any specific bit is 1: $1 - e^{-nk/m}$. And then the probability of a false positive — that all $k$ bits checked by a query for an item *not* in the set come back 1, assuming the $k$ probed positions are independent:

$$\varepsilon = \left(1 - e^{-nk/m}\right)^k$$

That's the false-positive rate. It depends on $n$ (how many items you've added), $m$ (how big the bit array is), and $k$ (how many hashes per item). $n$ is fixed by the workload; $m$ and $k$ are design parameters.

**More hashes hurt past a point.** More hashes set more bits per insertion, the array fills up faster, and the false-positive rate rises. The optimal $k$ minimizes $\varepsilon$ for a given $n$ and $m$.

Take the derivative of $\varepsilon$ with respect to $k$, set it to zero, and the optimal $k$ falls out cleanly:

$$k^* = \frac{m}{n} \ln 2$$

A clean closed form. The two pretty consequences: at the optimal $k$, exactly half the bits in the array are set on average (the algorithm packs the array as fully as it can without diminishing returns), and the false-positive rate at optimal $k$ simplifies to $\varepsilon = (1/2)^k = 2^{-k}$.

That second equation lets you solve for $m$ given $n$ and a target $\varepsilon$. Substituting $k^*$ back in and simplifying:

$$m^* = -\frac{n \ln \varepsilon}{(\ln 2)^2}$$

Or, using $\ln 2 \approx 0.693$ and $(\ln 2)^2 \approx 0.480$:

$$m^* \approx 1.44 \cdot n \cdot \log_2(1/\varepsilon)$$

That's the formula from the chapter opener. A Bloom filter holding $n$ items at false-positive rate $\varepsilon$ needs about $1.44 n \log_2(1/\varepsilon)$ bits, regardless of key length. For $\varepsilon = 0.01$, that's $1.44 \times \log_2(100) \approx 9.6$ bits per item.

## Thirty lines and a bytearray

The whole structure fits in about thirty lines of Python. The constructor takes the expected item count and the target false-positive rate, computes optimal $m$ and $k$ from the formulas above, and allocates a `bytearray` to hold the bits.

```python {export=src/codex/structures/bloom.py}
import math
from typing import Hashable, Iterator


class BloomFilter:
    def __init__(self, expected_items: int, fp_rate: float = 0.01) -> None:
        if expected_items <= 0 or not 0 < fp_rate < 1:
            raise ValueError("expected_items > 0 and 0 < fp_rate < 1")
        self._n_expected = expected_items
        ln2 = math.log(2)
        # m = -n ln(ε) / (ln 2)^2
        m = -expected_items * math.log(fp_rate) / (ln2 ** 2)
        self._m = max(8, int(math.ceil(m)))
        # k = (m/n) ln 2
        k = (self._m / expected_items) * ln2
        self._k = max(1, int(round(k)))
        self._bits = bytearray((self._m + 7) // 8)
```

The bit array lives inside a `bytearray`, a mutable sequence of 8-bit integers. To set bit $i$, you compute the byte index $i // 8$ and the bit-within-byte $i \bmod 8$, then OR in `1 << bit`. To test bit $i$, you AND with the same mask and check whether the result is nonzero. The standard bit-array idiom.

```python {export=src/codex/structures/bloom.py}
    def _hashes(self, item: Hashable) -> Iterator[int]:
        h1 = hash(item)
        h2 = hash((item, "salt"))
        for i in range(self._k):
            yield (h1 + i * h2) % self._m

    def add(self, item: Hashable) -> None:
        for pos in self._hashes(item):
            self._bits[pos // 8] |= 1 << (pos % 8)

    def __contains__(self, item: Hashable) -> bool:
        for pos in self._hashes(item):
            if not (self._bits[pos // 8] & (1 << (pos % 8))):
                return False
        return True
```

Three methods, three patterns. `_hashes` yields $k$ positions via the double-hashing trick. `add` sets all $k$ bits. `__contains__` checks all $k$ bits; if any is zero, return *False* (definitely-not); if all are one, return *True* (probably-yes).

Build one and verify the parameter computation:

```python
from codex.structures.bloom import BloomFilter

bf = BloomFilter(expected_items=10_000, fp_rate=0.01)
print(f"m = {bf._m} bits ({bf._m / 8:.0f} bytes)")
print(f"k = {bf._k}")
print(f"bits per item: {bf._m / 10_000:.2f}")
```

About 96 thousand bits (twelve kilobytes) to hold ten thousand items at 1% false-positive rate. Seven hash functions per item. The bits-per-item figure of about 9.6 matches the formula's $1.44 \log_2 100 \approx 9.6$.

Now the empirical validation. Insert ten thousand random strings, then query ten thousand *other* random strings and count how many come back as false positives.

```python
import random

bf = BloomFilter(expected_items=10_000, fp_rate=0.01)

random.seed(42)
alphabet = "abcdefghijklmnopqrstuvwxyz"

inserted = set()
while len(inserted) < 10_000:
    inserted.add("".join(random.choices(alphabet, k=8)))

for s in inserted:
    bf.add(s)

# no false negatives
print(f"all inserted are present: {all(s in bf for s in inserted)}")

# count false positives over 10,000 non-members
fp_count = 0
tested = 0
while tested < 10_000:
    s = "".join(random.choices(alphabet, k=8))
    if s in inserted:
        continue
    tested += 1
    if s in bf:
        fp_count += 1

print(f"false positives: {fp_count} out of {tested} non-members")
print(f"empirical FP rate: {fp_count / tested:.4f}")
print(f"predicted FP rate: 0.0100")
```

Empirical rate within a fraction of a percent of the predicted 1%. The agreement isn't an accident: the analysis is exact up to the $(1 - 1/m)^m \to 1/e$ approximation, which is wrong by less than $1/m$ at these table sizes. The only other randomness is from the choice of test strings, which is exactly the regime the formula models.

Sweep the parameter and watch the formula predict reality across a range:

```python
import math


def predicted_fp(n: int, m: int, k: int) -> float:
    return (1 - math.exp(-k * n / m)) ** k


for target_rate in [0.10, 0.01, 0.001]:
    bf = BloomFilter(expected_items=10_000, fp_rate=target_rate)
    for s in inserted:
        bf.add(s)
    pred = predicted_fp(10_000, bf._m, bf._k)
    print(f"target ε={target_rate:6.4f}  "
          f"m={bf._m:>6}  k={bf._k}  "
          f"predicted={pred:.4f}")
```

The predicted false-positive rate sits right on the target every time. The structure is parametric, not heuristic.

## No deletion, no enumeration, no resize

The list of operations a Bloom filter does *not* support is part of its contract. **Deletion isn't safe.** If you clear the $k$ bits for an item, you risk turning future *probably-yes* answers into spurious *definitely-not* answers for *other* items whose hash positions happened to overlap with the one you just deleted. The classic fix is a **counting Bloom filter**: replace each bit with a small counter (4–8 bits typically), increment on `add`, decrement on `remove`. That recovers deletion at the cost of multiplying the memory by the counter width. Mentioned here as a pointer, not implemented.

**Enumeration isn't supported.** There's no `for x in bf` operation, and there couldn't be — the keys themselves were never stored, and the bit pattern alone can't reconstruct them. The structure can answer "do you contain this specific thing?" but never "what do you contain?" The doubt the chapter opened on extends specifically to recovering the members.

**Resizing isn't easy.** If you've underestimated $n$, you can't just add bits: the hash positions depend on $m$, so the existing fingerprints become meaningless after a resize. The standard workaround is *scalable Bloom filters* (Almeida et al., 2007), which chain multiple smaller filters together with increasing $m$ and decreasing $\varepsilon$. Another pointer, not built here.

## The three questions, applied

### Is it correct?

The Bloom filter satisfies a *one-sided* correctness condition. Every item that was added returns *probably-yes* on subsequent membership checks — the `add` method sets exactly the bits that `__contains__` checks, so all $k$ bits will be set, and the check returns *True*. **No false negatives.** This is exact, not statistical.

The other direction is the statistical guarantee. Items that were never added can return *probably-yes* (a false positive) with probability bounded by $\varepsilon$, the design parameter. That bound is *expected* over the randomness of the hash functions, not worst-case — an adversary who can construct keys to exploit your specific hash functions can drive the FP rate higher, the same caveat from chapter 12.

### How efficient is it?

The `add` and `__contains__` operations each run in $\Theta(k)$ time and $O(1)$ space. With $k = (m/n) \ln 2$, that's $O(\ln(1/\varepsilon))$ — proportional to the number of bits of confidence you want, not to the size of the set. For $\varepsilon = 0.01$, $k = 7$. For $\varepsilon = 0.0001$, $k = 14$. For $\varepsilon = 10^{-9}$, $k = 30$. The cost grows logarithmically in inverse FP rate; you can have very rare false positives for cheap.

Space is $\Theta(m) = \Theta(n \log(1/\varepsilon))$ bits — linear in $n$, logarithmic in inverse error tolerance. At $\varepsilon = 0.01$ that's about 10 bits per item. Compare with a hash table storing the keys themselves, which costs roughly $8 \times \overline{|k|}$ bits per item (where $\overline{|k|}$ is average key length in bytes). For typical key sizes the Bloom filter is one to two orders of magnitude smaller.

### Is it optimal?

The information-theoretic lower bound for a structure supporting one-sided $\varepsilon$-error membership testing on a set of size $n$ is $n \log_2(1/\varepsilon)$ bits. You need at least that many bits to distinguish "any of the $n$ members" from "everything else" with error $\varepsilon$. The Bloom filter at optimal $k$ achieves $1.44 n \log_2(1/\varepsilon)$ bits, within a factor of $1.44 = 1/\ln 2$ of the lower bound. That constant is the cost of using $k$-independent hash functions; with $k = 1$ and a perfectly correlated hash, you could match the bound, but that hash function doesn't exist for arbitrary keys.

Structures that get closer to the lower bound exist — *quotient filters* (Bender et al., 2012), *cuckoo filters* (Fan et al., 2014), *Morton filters* (Breslow & Jayasena, 2018) — and they trade additional complexity (mostly around supporting deletion and resize) for a tighter space bound. For the canonical "remember a set, accept some false positives" problem, the basic Bloom filter is within a small constant of optimal, and that's the form that ships in every production caching system.

## Trade certainty for space

A Bloom filter achieves its memory efficiency precisely by giving up the ability to enumerate or reconstruct what it holds. The trade isn't a bug; it's the point. Asymmetric error guarantees — definite negatives, probable positives — are what make the structure useful as a pre-filter even when the positives have a known error rate.

This pattern shows up across the probabilistic-data-structures family in Part IX. Count-Min sketch trades exactness for space when *counting* frequencies of items in a stream. HyperLogLog trades exactness for space when *counting distinct items* in a stream, getting the count of a billion-element multiset accurate to within 2% using a kilobyte of memory. Each is a different version of the same move: identify exactly what the workload needs to know, and design a structure that stores only *that*, with a known error rate on the side you're allowed to be wrong.

The Bloom filter itself is correct in the one-sided sense (no false negatives, false positives at a tunable rate), runs in $\Theta(k)$ per operation, and uses $\Theta(n \log(1/\varepsilon))$ bits, within a constant factor of the information-theoretic lower bound.

## Notes and further reading

Burton Bloom's 1970 paper "Space/Time Trade-offs in Hash Coding with Allowable Errors" is the original construction; it's short, accessible, and worth reading. The optimal-parameter analysis given here is folklore but is treated rigorously in Mitzenmacher and Upfal's *Probability and Computing* §5. The double-hashing trick that lets you simulate $k$ independent hashes from two is Kirsch and Mitzenmacher's 2006 ESA paper "Less Hashing, Same Performance: Building a Better Bloom Filter." The counting variant is Fan, Cao, Almeida, and Broder's 2000 IEEE/ACM Transactions on Networking paper "Summary Cache." For the tighter-than-Bloom alternatives, see Bender et al.'s "Don't Thrash" (quotient filters) and Fan et al.'s "Cuckoo Filter: Practically Better Than Bloom" — both are concise and implementable. CLRS doesn't cover Bloom filters; the standard textbook entry point is Sedgewick & Wayne's *Algorithms* §3.5 exercises or the Mitzenmacher-Upfal chapter cited above.
