from typing import Iterator


class BSTNode[K, V]:
    def __init__(
        self,
        key: K,
        value: V,
        left: "BSTNode[K, V] | None" = None,
        right: "BSTNode[K, V] | None" = None,
    ) -> None:
        self.key = key
        self.value = value
        self.left = left
        self.right = right
class BST[K, V]:
    def __init__(self) -> None:
        self._root: BSTNode[K, V] | None = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size
    def insert(self, key: K, value: V) -> None:
        def _insert(node: BSTNode[K, V] | None) -> BSTNode[K, V]:
            if node is None:
                self._size += 1
                return BSTNode(key, value)
            if key < node.key:
                node.left = _insert(node.left)
            elif key > node.key:
                node.right = _insert(node.right)
            else:
                node.value = value  # replace existing value, leave size unchanged
            return node

        self._root = _insert(self._root)
    def search(self, key: K) -> V | None:
        node = self._root
        while node is not None:
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return node.value
        return None

    def __contains__(self, key: K) -> bool:
        return self.search(key) is not None
    def in_order(self) -> Iterator[tuple[K, V]]:
        def _walk(node: BSTNode[K, V] | None) -> Iterator[tuple[K, V]]:
            if node is None:
                return
            yield from _walk(node.left)
            yield (node.key, node.value)
            yield from _walk(node.right)

        yield from _walk(self._root)
    def _min_node(self, node: BSTNode[K, V]) -> BSTNode[K, V]:
        while node.left is not None:
            node = node.left
        return node
    def delete(self, key: K) -> None:
        def _delete(
            node: BSTNode[K, V] | None, k: K
        ) -> BSTNode[K, V] | None:
            if node is None:
                return None  # key not present — nothing to do
            if k < node.key:
                node.left = _delete(node.left, k)
                return node
            if k > node.key:
                node.right = _delete(node.right, k)
                return node
            # node.key == k — match site, dispatch on children
            if node.left is None:
                self._size -= 1
                return node.right  # leaf or right-only child
            if node.right is None:
                self._size -= 1
                return node.left   # left-only child
            # two children: copy successor's payload, then recursively delete the
            # successor from the right subtree (it has at most one child, so the
            # recursive call lands in one of the simpler cases above).
            succ = self._min_node(node.right)
            node.key = succ.key
            node.value = succ.value
            node.right = _delete(node.right, succ.key)
            return node

        self._root = _delete(self._root, key)
    def height(self) -> int:
        def _height(node: BSTNode[K, V] | None) -> int:
            if node is None:
                return -1  # empty: -1 so a single node ends up at height 0
            return 1 + max(_height(node.left), _height(node.right))

        return _height(self._root)
