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
