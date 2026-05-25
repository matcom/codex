from dataclasses import dataclass
from typing import Iterator, Sequence
from codex.types import Ordering, default_order


@dataclass
class Node[T]:
    value: T
    next: "Node[T] | None" = None
class LinkedList[T]:
    def __init__(self) -> None:
        self.head: Node[T] | None = None
        self.tail: Node[T] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        cur = self.head
        while cur is not None:
            yield cur.value
            cur = cur.next
    def prepend(self, value: T) -> None:
        node = Node(value, self.head)
        if self.head is None:
            self.tail = node
        self.head = node
        self._size += 1
    def append(self, value: T) -> None:
        node = Node(value)
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self._size += 1
    def insert_after(self, node: Node[T], value: T) -> None:
        new_node = Node(value, node.next)
        node.next = new_node
        if node is self.tail:
            self.tail = new_node
        self._size += 1

    def delete_after(self, node: Node[T]) -> None:
        target = node.next
        if target is None:
            return
        node.next = target.next
        if target is self.tail:
            self.tail = node
        self._size -= 1
def reverse[T](head: Node[T] | None) -> Node[T] | None:
    prev: Node[T] | None = None
    cur = head
    while cur is not None:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev
def merge_sorted[T](
    a: Node[T] | None,
    b: Node[T] | None,
    order: Ordering[T] = default_order,
) -> Node[T] | None:
    dummy: Node[T] = Node(None)  # type: ignore[arg-type]
    tail = dummy
    while a is not None and b is not None:
        if order(a.value, b.value) <= 0:
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next
        tail = tail.next  # type: ignore[assignment]
    tail.next = a if a is not None else b
    return dummy.next
def floyd_cycle[T](head: Node[T] | None) -> Node[T] | None:
    tortoise = hare = head
    while hare is not None and hare.next is not None:
        assert tortoise is not None  # tortoise is at most as far as hare
        tortoise = tortoise.next
        hare = hare.next.next
        if tortoise is hare:
            tortoise = head
            while tortoise is not hare:
                assert tortoise is not None and hare is not None
                tortoise = tortoise.next
                hare = hare.next
            return tortoise
    return None
@dataclass
class DoublyLinkedNode[T]:
    value: T
    prev: "DoublyLinkedNode[T] | None" = None
    next: "DoublyLinkedNode[T] | None" = None


def detach[T](node: DoublyLinkedNode[T]) -> None:
    if node.prev is not None:
        node.prev.next = node.next
    if node.next is not None:
        node.next.prev = node.prev
    node.prev = None
    node.next = None
def make_circular[T](head: Node[T] | None) -> Node[T] | None:
    if head is None:
        return None
    cur = head
    while cur.next is not None:
        cur = cur.next
    cur.next = head
    return head
