class CircularBuffer[T]:
    def __init__(self, capacity: int) -> None:
        self._items: list[T | None] = [None] * capacity
        self._capacity = capacity
        self._head = 0
        self._tail = 0
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def is_full(self) -> bool:
        return self._size == self._capacity
    def enqueue(self, value: T) -> None:
        if self._size == self._capacity:
            raise OverflowError("circular buffer is full")
        self._items[self._tail] = value
        self._tail = (self._tail + 1) % self._capacity
        self._size += 1

    def dequeue(self) -> T:
        if self._size == 0:
            raise IndexError("dequeue from empty buffer")
        value = self._items[self._head]
        self._items[self._head] = None
        self._head = (self._head + 1) % self._capacity
        self._size -= 1
        return value  # type: ignore[return-value]
from codex.structures.linked import Node


class LinkedQueue[T]:
    def __init__(self) -> None:
        self._head: Node[T] | None = None
        self._tail: Node[T] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._head is not None

    def enqueue(self, value: T) -> None:
        node = Node(value)
        if self._tail is None:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node
        self._size += 1

    def dequeue(self) -> T:
        if self._head is None:
            raise IndexError("dequeue from empty queue")
        value = self._head.value
        self._head = self._head.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return value
from codex.structures.linked import DoublyLinkedNode


class Deque[T]:
    def __init__(self) -> None:
        self._head: DoublyLinkedNode[T] | None = None
        self._tail: DoublyLinkedNode[T] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._head is not None
    def push_front(self, value: T) -> None:
        node = DoublyLinkedNode(value, prev=None, next=self._head)
        if self._head is None:
            self._tail = node
        else:
            self._head.prev = node
        self._head = node
        self._size += 1

    def push_back(self, value: T) -> None:
        node = DoublyLinkedNode(value, prev=self._tail, next=None)
        if self._tail is None:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node
        self._size += 1

    def pop_front(self) -> T:
        if self._head is None:
            raise IndexError("pop_front from empty deque")
        node = self._head
        self._head = node.next
        if self._head is None:
            self._tail = None
        else:
            self._head.prev = None
        self._size -= 1
        return node.value

    def pop_back(self) -> T:
        if self._tail is None:
            raise IndexError("pop_back from empty deque")
        node = self._tail
        self._tail = node.prev
        if self._tail is None:
            self._head = None
        else:
            self._tail.next = None
        self._size -= 1
        return node.value

    def peek_front(self) -> T:
        if self._head is None:
            raise IndexError("peek_front of empty deque")
        return self._head.value

    def peek_back(self) -> T:
        if self._tail is None:
            raise IndexError("peek_back of empty deque")
        return self._tail.value
from typing import Sequence


def monotonic_window_max(items: Sequence[int], k: int) -> list[int]:
    result: list[int] = []
    dq: Deque[int] = Deque()  # holds indices
    for i, x in enumerate(items):
        # drop indices that have just slid out of the window
        while dq and dq.peek_front() <= i - k:
            dq.pop_front()
        # drop back-indices whose values are dominated by the new one
        while dq and items[dq.peek_back()] <= x:
            dq.pop_back()
        dq.push_back(i)
        if i >= k - 1:
            result.append(items[dq.peek_front()])
    return result
