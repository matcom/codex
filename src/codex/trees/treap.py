import random
from typing import Iterator


class TreapNode[K, V]:
    def __init__(
        self,
        key: K,
        value: V,
        priority: float,
        left: "TreapNode[K, V] | None" = None,
        right: "TreapNode[K, V] | None" = None,
    ) -> None:
        self.key = key
        self.value = value
        self.priority = priority
        self.left = left
        self.right = right
def _rotate_right[K, V](node: TreapNode[K, V]) -> TreapNode[K, V]:
    assert node.left is not None
    new_root = node.left
    node.left = new_root.right
    new_root.right = node
    return new_root


def _rotate_left[K, V](node: TreapNode[K, V]) -> TreapNode[K, V]:
    assert node.right is not None
    new_root = node.right
    node.right = new_root.left
    new_root.left = node
    return new_root
class Treap[K, V]:
    def __init__(self, rng: random.Random | None = None) -> None:
        self._root: TreapNode[K, V] | None = None
        self._size: int = 0
        self._rng: random.Random = rng if rng is not None else random.Random()

    def __len__(self) -> int:
        return self._size

    def height(self) -> int:
        def _h(node: TreapNode[K, V] | None) -> int:
            if node is None:
                return -1
            return 1 + max(_h(node.left), _h(node.right))

        return _h(self._root)
    def insert(self, key: K, value: V) -> None:
        priority = self._rng.random()
        self._root = self._insert(self._root, key, value, priority)

    def _insert(
        self,
        node: TreapNode[K, V] | None,
        key: K,
        value: V,
        priority: float,
    ) -> TreapNode[K, V]:
        if node is None:
            self._size += 1
            return TreapNode(key, value, priority)
        if key < node.key:
            node.left = self._insert(node.left, key, value, priority)
            if node.left.priority > node.priority:
                return _rotate_right(node)
        elif key > node.key:
            node.right = self._insert(node.right, key, value, priority)
            if node.right.priority > node.priority:
                return _rotate_left(node)
        else:
            node.value = value  # overwrite, no priority change, no rotation
        return node
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
        def _walk(node: TreapNode[K, V] | None) -> Iterator[tuple[K, V]]:
            if node is None:
                return
            yield from _walk(node.left)
            yield (node.key, node.value)
            yield from _walk(node.right)

        yield from _walk(self._root)
    def delete(self, key: K) -> None:
        self._root = self._delete(self._root, key)

    def _delete(
        self,
        node: TreapNode[K, V] | None,
        key: K,
    ) -> TreapNode[K, V] | None:
        if node is None:
            return None  # key not present — silent no-op
        if key < node.key:
            node.left = self._delete(node.left, key)
            return node
        if key > node.key:
            node.right = self._delete(node.right, key)
            return node
        return self._rotate_down_and_remove(node)
    def _rotate_down_and_remove(
        self,
        node: TreapNode[K, V],
    ) -> TreapNode[K, V] | None:
        if node.left is None and node.right is None:
            self._size -= 1
            return None
        if node.left is None:
            self._size -= 1
            return node.right
        if node.right is None:
            self._size -= 1
            return node.left
        # both children — rotate target past the higher-priority child
        if node.left.priority > node.right.priority:
            new_root = _rotate_right(node)
            new_root.right = self._rotate_down_and_remove(node)
            return new_root
        new_root = _rotate_left(node)
        new_root.left = self._rotate_down_and_remove(node)
        return new_root
