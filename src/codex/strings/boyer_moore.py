def bad_character_table(pattern: str) -> dict[str, int]:
    """For each character that appears in pattern, the rightmost index where
    it appears. Used by the bad-character heuristic.
    """
    table: dict[str, int] = {}
    for i, c in enumerate(pattern):
        table[c] = i
    return table
def good_suffix_shift(pattern: str, j: int) -> int:
    """Compute the good-suffix shift when the mismatch is at position j of the
    pattern (so pattern[j+1:m] matched against the text — the 'good suffix').

    Case 1: the rightmost reoccurrence of the good suffix elsewhere in the
    pattern, where the character preceding the reoccurrence differs from
    pattern[j] (so the same mismatch isn't repeated).

    Case 2: if no such reoccurrence, the longest prefix of pattern that is
    also a suffix of the good suffix.

    If neither applies, shift past the entire pattern (return m).
    """
    m = len(pattern)
    good_suffix = pattern[j + 1:]
    k = len(good_suffix)

    # Case 1
    for shift_pos in range(j - 1, -1, -1):
        end = shift_pos + 1 + k
        if end > m:
            continue
        if pattern[shift_pos + 1:end] == good_suffix and (
            shift_pos < 0 or pattern[shift_pos] != pattern[j]
        ):
            return j - shift_pos

    # Case 2
    for prefix_len in range(k, 0, -1):
        if good_suffix.endswith(pattern[:prefix_len]):
            return m - prefix_len

    return m
def good_suffix_table(pattern: str) -> list[int]:
    """Precompute good_suffix_shift for every mismatch position 0..m-1.
    Returns a list of length m where table[j] is the shift on mismatch at j.
    """
    m = len(pattern)
    return [good_suffix_shift(pattern, j) for j in range(m)]
def find(text: str, pattern: str) -> int | None:
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
    if m > n:
        return None
    bc = bad_character_table(pattern)
    gs = good_suffix_table(pattern)
    i = 0
    while i <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[i + j]:
            j -= 1
        if j < 0:
            return i
        bc_shift = max(1, j - bc.get(text[i + j], -1))
        gs_shift = gs[j]
        i += max(bc_shift, gs_shift)
    return None
def find_all(text: str, pattern: str) -> list[int]:
    """All matches. On a full match, shift by 1 to find every overlapping
    match. Proper overlap handling in BM requires an additional good-suffix
    preprocessing for the case-when-the-whole-pattern-matched, which I'm
    skipping for clarity; shift-by-1 is correct (just not necessarily fast).
    """
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []
    bc = bad_character_table(pattern)
    gs = good_suffix_table(pattern)
    matches: list[int] = []
    i = 0
    while i <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[i + j]:
            j -= 1
        if j < 0:
            matches.append(i)
            i += 1  # overlap-safe shift
        else:
            bc_shift = max(1, j - bc.get(text[i + j], -1))
            gs_shift = gs[j]
            i += max(bc_shift, gs_shift)
    return matches
def find_counting(text: str, pattern: str) -> tuple[int | None, int, int]:
    """Instrumented version: returns (first match index or None,
    number of character comparisons, number of window shifts).
    """
    n, m = len(text), len(pattern)
    if m == 0:
        return 0, 0, 0
    if m > n:
        return None, 0, 0
    bc = bad_character_table(pattern)
    gs = good_suffix_table(pattern)
    comparisons = 0
    shifts = 0
    i = 0
    while i <= n - m:
        shifts += 1
        j = m - 1
        while j >= 0:
            comparisons += 1
            if pattern[j] != text[i + j]:
                break
            j -= 1
        if j < 0:
            return i, comparisons, shifts
        bc_shift = max(1, j - bc.get(text[i + j], -1))
        gs_shift = gs[j]
        i += max(bc_shift, gs_shift)
    return None, comparisons, shifts
