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
