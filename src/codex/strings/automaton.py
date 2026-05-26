def _delta(pattern: str, q: int, c: str) -> int:
    candidate = pattern[:q] + c
    m = len(pattern)
    for length in range(min(q + 1, m), 0, -1):
        if candidate.endswith(pattern[:length]):
            return length
    return 0
def build_dfa(
    pattern: str, alphabet: str | None = None
) -> tuple[list[dict[str, int]], int]:
    m = len(pattern)
    if alphabet is None:
        alphabet = "".join(sorted(set(pattern)))
    transitions: list[dict[str, int]] = []
    for q in range(m + 1):
        row: dict[str, int] = {}
        for c in alphabet:
            row[c] = _delta(pattern, q, c)
        transitions.append(row)
    return transitions, m
def find(text: str, pattern: str) -> int | None:
    if not pattern:
        return 0
    if len(pattern) > len(text):
        return None
    transitions, accept = build_dfa(pattern)
    state = 0
    for idx, c in enumerate(text):
        state = transitions[state].get(c, 0)
        if state == accept:
            return idx - accept + 1
    return None
def find_all(text: str, pattern: str) -> list[int]:
    if not pattern or len(pattern) > len(text):
        return []
    transitions, accept = build_dfa(pattern)
    matches: list[int] = []
    state = 0
    for idx, c in enumerate(text):
        state = transitions[state].get(c, 0)
        if state == accept:
            matches.append(idx - accept + 1)
    return matches
