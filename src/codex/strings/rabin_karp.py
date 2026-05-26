def polynomial_hash(s: str, base: int, modulus: int) -> int:
    """Horner-form polynomial hash of s in base `base` modulo `modulus`.

    Reads s as a multi-digit number with each character treated as a digit
    in base `base`, then reduces modulo `modulus` to keep the integer
    bounded. Runs in O(len(s)) time and O(1) space.
    """
    h = 0
    for c in s:
        h = (h * base + ord(c)) % modulus
    return h
def find(
    text: str, pattern: str, base: int = 257, modulus: int = 1_000_000_007
) -> int | None:
    """First match index via Rabin-Karp rolling-hash with Las Vegas verification."""
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
    if m > n:
        return None
    pattern_hash = polynomial_hash(pattern, base, modulus)
    window_hash = polynomial_hash(text[:m], base, modulus)
    high_power = pow(base, m - 1, modulus)
    if window_hash == pattern_hash and text[:m] == pattern:
        return 0
    for i in range(1, n - m + 1):
        window_hash = (
            (window_hash - ord(text[i - 1]) * high_power) * base
            + ord(text[i + m - 1])
        ) % modulus
        if window_hash == pattern_hash and text[i : i + m] == pattern:
            return i
    return None
def find_all(
    text: str, pattern: str, base: int = 257, modulus: int = 1_000_000_007
) -> list[int]:
    """All overlapping match indices via Rabin-Karp."""
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []
    pattern_hash = polynomial_hash(pattern, base, modulus)
    window_hash = polynomial_hash(text[:m], base, modulus)
    high_power = pow(base, m - 1, modulus)
    matches: list[int] = []
    if window_hash == pattern_hash and text[:m] == pattern:
        matches.append(0)
    for i in range(1, n - m + 1):
        window_hash = (
            (window_hash - ord(text[i - 1]) * high_power) * base
            + ord(text[i + m - 1])
        ) % modulus
        if window_hash == pattern_hash and text[i : i + m] == pattern:
            matches.append(i)
    return matches
def find_counting(
    text: str, pattern: str, base: int = 257, modulus: int = 1_000_000_007
) -> tuple[int | None, int, int]:
    """Instrumented Rabin-Karp.

    Returns (first match index or None, hash collisions detected,
    full-string verifications performed). A 'collision' is a hash match
    that fails string comparison — a false positive caught by the
    Las Vegas verification. A 'verification' is any full string equality
    check that ran, including the eventual confirmation of a real match.
    """
    n, m = len(text), len(pattern)
    if m == 0:
        return 0, 0, 0
    if m > n:
        return None, 0, 0
    pattern_hash = polynomial_hash(pattern, base, modulus)
    window_hash = polynomial_hash(text[:m], base, modulus)
    high_power = pow(base, m - 1, modulus)
    collisions = 0
    verifications = 0
    if window_hash == pattern_hash:
        verifications += 1
        if text[:m] == pattern:
            return 0, collisions, verifications
        collisions += 1
    for i in range(1, n - m + 1):
        window_hash = (
            (window_hash - ord(text[i - 1]) * high_power) * base
            + ord(text[i + m - 1])
        ) % modulus
        if window_hash == pattern_hash:
            verifications += 1
            if text[i : i + m] == pattern:
                return i, collisions, verifications
            collisions += 1
    return None, collisions, verifications
