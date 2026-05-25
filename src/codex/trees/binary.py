from collections import deque
from typing import Iterator


class BinaryNode[T]:
    def __init__(
        self,
        value: T,
        left: "BinaryNode[T] | None" = None,
        right: "BinaryNode[T] | None" = None,
    ) -> None:
        self.value = value
        self.left = left
        self.right = right
def preorder[T](node: BinaryNode[T] | None) -> Iterator[T]:
    if node is None:
        return
    yield node.value
    yield from preorder(node.left)
    yield from preorder(node.right)
def inorder[T](node: BinaryNode[T] | None) -> Iterator[T]:
    if node is None:
        return
    yield from inorder(node.left)
    yield node.value
    yield from inorder(node.right)
def postorder[T](node: BinaryNode[T] | None) -> Iterator[T]:
    if node is None:
        return
    yield from postorder(node.left)
    yield from postorder(node.right)
    yield node.value
def level_order[T](root: BinaryNode[T] | None) -> Iterator[T]:
    if root is None:
        return
    queue: deque[BinaryNode[T]] = deque([root])
    while queue:
        node = queue.popleft()
        yield node.value
        if node.left is not None:
            queue.append(node.left)
        if node.right is not None:
            queue.append(node.right)
def _rightmost[T](node: BinaryNode[T], stop: BinaryNode[T]) -> BinaryNode[T]:
    while node.right is not None and node.right is not stop:
        node = node.right
    return node
def morris_inorder[T](root: BinaryNode[T] | None) -> Iterator[T]:
    cur = root
    while cur is not None:
        if cur.left is None:
            yield cur.value
            cur = cur.right
            continue
        pred = _rightmost(cur.left, cur)
        if pred.right is None:
            pred.right = cur                 # install thread
            cur = cur.left
        else:
            pred.right = None                # remove thread, restore tree
            yield cur.value
            cur = cur.right
def serialize[T](root: BinaryNode[T] | None) -> str:
    tokens: list[str] = []

    def _walk(node: BinaryNode[T] | None) -> None:
        if node is None:
            tokens.append("#")
            return
        tokens.append(str(node.value))
        _walk(node.left)
        _walk(node.right)

    _walk(root)
    return " ".join(tokens)
def deserialize(s: str) -> BinaryNode[int] | None:
    tokens = iter(s.split())
    return _parse(tokens)
def _parse(tokens: Iterator[str]) -> BinaryNode[int] | None:
    token = next(tokens)
    if token == "#":
        return None
    node = BinaryNode(int(token))
    node.left = _parse(tokens)
    node.right = _parse(tokens)
    return node
