class ArrayStack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def push(self, value: T) -> None:
        self._items.append(value)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise IndexError("peek of empty stack")
        return self._items[-1]
from codex.structures.linked import Node


class LinkedStack[T]:
    def __init__(self) -> None:
        self._top: Node[T] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._top is not None

    def push(self, value: T) -> None:
        self._top = Node(value, self._top)
        self._size += 1

    def pop(self) -> T:
        if self._top is None:
            raise IndexError("pop from empty stack")
        value = self._top.value
        self._top = self._top.next
        self._size -= 1
        return value

    def peek(self) -> T:
        if self._top is None:
            raise IndexError("peek of empty stack")
        return self._top.value
