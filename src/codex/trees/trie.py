class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.terminal: bool = False
        self.value: object | None = None
class Trie:
    def __init__(self) -> None:
        self._root = TrieNode()
        self._size = 0

    def __len__(self) -> int:
        return self._size
    def insert(self, key: str, value: object = None) -> None:
        node = self._root
        for ch in key:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        if not node.terminal:
            self._size += 1
        node.terminal = True
        node.value = value
    def _descend(self, key: str) -> TrieNode | None:
        node = self._root
        for ch in key:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
    def __contains__(self, key: str) -> bool:
        node = self._descend(key)
        return node is not None and node.terminal

    def get(self, key: str) -> object | None:
        node = self._descend(key)
        if node is None or not node.terminal:
            return None
        return node.value
    def starts_with(self, prefix: str) -> list[str]:
        node = self._descend(prefix)
        if node is None:
            return []
        results: list[str] = []
        self._collect(node, prefix, results)
        return results
    def _collect(self, node: TrieNode, path: str, results: list[str]) -> None:
        if node.terminal:
            results.append(path)
        for ch, child in node.children.items():
            self._collect(child, path + ch, results)
    def longest_prefix_of(self, query: str) -> str | None:
        node = self._root
        deepest: str | None = None
        for i, ch in enumerate(query):
            if ch not in node.children:
                break
            node = node.children[ch]
            if node.terminal:
                deepest = query[: i + 1]
        return deepest
class RadixNode:
    def __init__(self) -> None:
        self.children: dict[str, "RadixNode"] = {}
        self.terminal: bool = False
        self.value: object | None = None
class RadixTrie:
    def __init__(self) -> None:
        self._root = RadixNode()
        self._size = 0

    def __len__(self) -> int:
        return self._size
    def insert(self, key: str, value: object = None) -> None:
        node = self._root
        rest = key
        while rest:
            edge = self._matching_edge(node, rest[0])
            if edge is None:
                leaf = RadixNode()
                leaf.terminal = True
                leaf.value = value
                node.children[rest] = leaf
                self._size += 1
                return
            n_common = self._common_prefix_length(edge, rest)
            if n_common == len(edge):
                # consume the whole edge, descend
                node = node.children[edge]
                rest = rest[n_common:]
                continue
            self._split_edge(node, edge, n_common, rest[n_common:], value)
            self._size += 1
            return
        if not node.terminal:
            self._size += 1
        node.terminal = True
        node.value = value
    def _matching_edge(self, node: RadixNode, ch: str) -> str | None:
        for edge in node.children:
            if edge[0] == ch:
                return edge
        return None
    def _common_prefix_length(self, a: str, b: str) -> int:
        i = 0
        while i < len(a) and i < len(b) and a[i] == b[i]:
            i += 1
        return i
    def _split_edge(
        self,
        node: RadixNode,
        edge: str,
        n_common: int,
        rest: str,
        value: object,
    ) -> None:
        original_child = node.children[edge]
        split = RadixNode()
        split.children[edge[n_common:]] = original_child
        del node.children[edge]
        node.children[edge[:n_common]] = split
        if rest:
            leaf = RadixNode()
            leaf.terminal = True
            leaf.value = value
            split.children[rest] = leaf
        else:
            split.terminal = True
            split.value = value
    def __contains__(self, key: str) -> bool:
        node = self._root
        rest = key
        while rest:
            edge = self._matching_edge(node, rest[0])
            if edge is None or not rest.startswith(edge):
                return False
            node = node.children[edge]
            rest = rest[len(edge):]
        return node.terminal
