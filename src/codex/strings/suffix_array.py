def suffix_array_naive(text: str) -> list[int]:
    """Build the suffix array by explicit sort of every suffix.
    O(n^2 log n) time, O(n^2) extra memory. Clear; not for large inputs.
    """
    n = len(text)
    indexed = sorted(range(n), key=lambda i: text[i:])
    return indexed
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
