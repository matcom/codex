def hamming(a: str, b: str) -> int:
    """Number of positions at which two equal-length strings differ.
    Raises ValueError if lengths disagree."""
    if len(a) != len(b):
        raise ValueError(f"hamming requires equal lengths, got {len(a)} vs {len(b)}")
    return sum(1 for x, y in zip(a, b) if x != y)
def levenshtein(a: str, b: str) -> int:
    """Minimum number of insert/delete/substitute edits to transform a into b.
    Bottom-up DP, O(nm) time, O(nm) space."""
    n, m = len(a), len(b)
    if n == 0:
        return m
    if m == 0:
        return n
    # dp[i][j] = edit distance between a[:i] and b[:j]
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # delete a[i-1]
                    dp[i][j - 1],      # insert b[j-1]
                    dp[i - 1][j - 1],  # substitute a[i-1] with b[j-1]
                )
    return dp[n][m]
def align(a: str, b: str) -> list[tuple[str, str]]:
    """Edit-distance alignment as a list of (char_a, char_b) pairs.
    '-' is the gap marker. Reconstructed via backtracking through the DP
    table from dp[n][m] to dp[0][0]."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],
                    dp[i][j - 1],
                    dp[i - 1][j - 1],
                )

    # Backtrack to reconstruct alignment
    alignment: list[tuple[str, str]] = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
            alignment.append((a[i - 1], b[j - 1]))
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            alignment.append((a[i - 1], b[j - 1]))  # substitute
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            alignment.append((a[i - 1], "-"))  # delete from a
            i -= 1
        else:
            alignment.append(("-", b[j - 1]))  # insert into a (delete from b)
            j -= 1
    alignment.reverse()
    return alignment
def lcs(a: str, b: str) -> str:
    """Longest common subsequence — a string that is a subsequence of both
    a and b, of maximum length. Returns one such LCS (there can be many)."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    # Backtrack
    result: list[str] = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            result.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(result))
def lcss(a: str, b: str) -> str:
    """Longest common SUBSTRING — a contiguous run of characters appearing
    in both a and b, of maximum length."""
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return ""
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    best_len = 0
    best_end_in_a = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > best_len:
                    best_len = dp[i][j]
                    best_end_in_a = i
    return a[best_end_in_a - best_len:best_end_in_a]
