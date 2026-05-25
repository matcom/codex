class DynamicArray[T]:
    def __init__(self, initial_capacity: int = 4) -> None:
        self._capacity = initial_capacity
        self._size = 0
        self._items: list[T | None] = [None] * initial_capacity

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, i: int) -> T:
        if not 0 <= i < self._size:
            raise IndexError(f"index {i} out of range for size {self._size}")
        return self._items[i]  # type: ignore[return-value]

    def __setitem__(self, i: int, value: T) -> None:
        if not 0 <= i < self._size:
            raise IndexError(f"index {i} out of range for size {self._size}")
        self._items[i] = value
    def append(self, value: T) -> None:
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._items[self._size] = value
        self._size += 1
    def _resize(self, new_capacity: int) -> None:
        new_items: list[T | None] = [None] * new_capacity
        for i in range(self._size):
            new_items[i] = self._items[i]
        self._items = new_items
        self._capacity = new_capacity
    def pop(self) -> T:
        if self._size == 0:
            raise IndexError("pop from empty array")
        self._size -= 1
        value = self._items[self._size]
        self._items[self._size] = None  # let the garbage collector reclaim it
        if 0 < self._size <= self._capacity // 4 and self._capacity > 1:
            self._resize(self._capacity // 2)
        return value  # type: ignore[return-value]
