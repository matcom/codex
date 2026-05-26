from collections import deque


class _ACNode:
    """Internal trie node with Aho-Corasick augmentations."""

    def __init__(self) -> None:
        self.children: dict[str, "_ACNode"] = {}
        self.fail: "_ACNode | None" = None
        self.output: list[str] = []  # patterns ending at this node or via fail-chain
        self.depth: int = 0
class AhoCorasick:
    """Multi-pattern matcher. Build once with a list of patterns, then scan
    arbitrarily many texts. Each scan is a single O(n + total_output) pass.
    """

    def __init__(self, patterns: list[str]) -> None:
        self._root = _ACNode()
        self._patterns = [p for p in patterns if p]  # drop empty patterns
        self._build_trie()
        self._build_failure_links()
    def _build_trie(self) -> None:
        for pat in self._patterns:
            node = self._root
            for c in pat:
                if c not in node.children:
                    child = _ACNode()
                    child.depth = node.depth + 1
                    node.children[c] = child
                node = node.children[c]
            node.output.append(pat)
    def _build_failure_links(self) -> None:
        # BFS so a node's fail link is computed only after its parent's is.
        queue: deque[_ACNode] = deque()
        for child in self._root.children.values():
            child.fail = self._root
            queue.append(child)
        while queue:
            current = queue.popleft()
            for c, child in current.children.items():
                # Walk fail-pointers from current looking for one with
                # a c-child, or hit the root.
                f = current.fail
                while f is not None and c not in f.children:
                    f = f.fail
                child.fail = self._root if f is None else f.children[c]
                # Merge fail-target's output into ours so a single output
                # check at scan time catches every pattern ending here or
                # via the fail-chain.
                child.output = child.output + (
                    child.fail.output if child.fail is not None else []
                )
                queue.append(child)
    def find_all(self, text: str) -> list[tuple[int, str]]:
        """Return (start_index, pattern) for every match of every pattern in
        text. Matches of overlapping patterns are all reported.
        """
        matches: list[tuple[int, str]] = []
        node = self._root
        for i, c in enumerate(text):
            # Follow fail-links looking for a node with a c-child, or hit root.
            while node is not self._root and c not in node.children:
                node = node.fail if node.fail is not None else self._root
            if c in node.children:
                node = node.children[c]
            # Emit all patterns ending at this node (or reachable via fail-chain,
            # already merged into output by _build_failure_links).
            for pat in node.output:
                matches.append((i - len(pat) + 1, pat))
        return matches
