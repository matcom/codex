from typing import Iterator


class AVLNode[K, V]:
    def __init__(
        self,
        key: K,
        value: V,
        left: "AVLNode[K, V] | None" = None,
        right: "AVLNode[K, V] | None" = None,
    ) -> None:
        self.key = key
        self.value = value
        self.left = left
        self.right = right
        self.height = 0  # leaf height under the root-at-depth-0 convention
def _height(node: "AVLNode | None") -> int:
    return node.height if node is not None else -1


def _update_height(node: "AVLNode") -> None:
    node.height = 1 + max(_height(node.left), _height(node.right))


def _balance_factor(node: "AVLNode") -> int:
    return _height(node.left) - _height(node.right)
def _rotate_right(node: "AVLNode") -> "AVLNode":
    assert node.left is not None  # caller's responsibility
    new_root = node.left
    node.left = new_root.right    # B in the diagram
    new_root.right = node
    _update_height(node)          # update the descended node first
    _update_height(new_root)      # then the new root (depends on the descended node's height)
    return new_root
def _rotate_left(node: "AVLNode") -> "AVLNode":
    assert node.right is not None
    new_root = node.right
    node.right = new_root.left
    new_root.left = node
    _update_height(node)
    _update_height(new_root)
    return new_root
def _rebalance(node: "AVLNode") -> "AVLNode":
    _update_height(node)
    bf = _balance_factor(node)
    if bf > 1:                                # left-heavy
        assert node.left is not None
        if _balance_factor(node.left) < 0:    # LR: left child is right-heavy
            node.left = _rotate_left(node.left)
        return _rotate_right(node)            # LL or LR final step
    if bf < -1:                               # right-heavy
        assert node.right is not None
        if _balance_factor(node.right) > 0:   # RL: right child is left-heavy
            node.right = _rotate_right(node.right)
        return _rotate_left(node)             # RR or RL final step
    return node                                # already balanced
class AVL[K, V]:
    def __init__(self) -> None:
        self._root: AVLNode[K, V] | None = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def height(self) -> int:
        return _height(self._root)
    def insert(self, key: K, value: V) -> None:
        def _insert(node: AVLNode[K, V] | None) -> AVLNode[K, V]:
            if node is None:
                self._size += 1
                return AVLNode(key, value)
            if key < node.key:
                node.left = _insert(node.left)
            elif key > node.key:
                node.right = _insert(node.right)
            else:
                node.value = value            # overwrite, no rebalance needed
                return node
            return _rebalance(node)

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
        def _walk(node: AVLNode[K, V] | None) -> Iterator[tuple[K, V]]:
            if node is None:
                return
            yield from _walk(node.left)
            yield (node.key, node.value)
            yield from _walk(node.right)

        yield from _walk(self._root)
    def _min_node(self, node: AVLNode[K, V]) -> AVLNode[K, V]:
        while node.left is not None:
            node = node.left
        return node
    def delete(self, key: K) -> None:
        def _delete(
            node: AVLNode[K, V] | None, k: K
        ) -> AVLNode[K, V] | None:
            if node is None:
                return None
            if k < node.key:
                node.left = _delete(node.left, k)
            elif k > node.key:
                node.right = _delete(node.right, k)
            else:
                if node.left is None:
                    self._size -= 1
                    return node.right
                if node.right is None:
                    self._size -= 1
                    return node.left
                succ = self._min_node(node.right)
                node.key = succ.key
                node.value = succ.value
                node.right = _delete(node.right, succ.key)
            return _rebalance(node)

        self._root = _delete(self._root, key)
