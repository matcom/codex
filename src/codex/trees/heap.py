from collections.abc import Iterable


class Heap[T]:
    def __init__(self, items: Iterable[T] | None = None) -> None:
        if items is None:
            self._heap: list[T] = []
        else:
            self._heap = list(items)
            for i in range(len(self._heap) // 2 - 1, -1, -1):
                self._sift_down(i)

    def __len__(self) -> int:
        return len(self._heap)
    def push(self, item: T) -> None:
        self._heap.append(item)
        self._sift_up(len(self._heap) - 1)

    def _sift_up(self, i: int) -> None:
        while i > 0:
            parent = (i - 1) // 2
            if self._heap[i] < self._heap[parent]:
                self._heap[i], self._heap[parent] = (
                    self._heap[parent],
                    self._heap[i],
                )
                i = parent
            else:
                return
    def peek_min(self) -> T:
        if not self._heap:
            raise IndexError("peek from empty heap")
        return self._heap[0]

    def pop_min(self) -> T:
        if not self._heap:
            raise IndexError("pop from empty heap")
        root = self._heap[0]
        last = self._heap.pop()
        if self._heap:
            self._heap[0] = last
            self._sift_down(0)
        return root
    def _sift_down(self, i: int, n: int | None = None) -> None:
        if n is None:
            n = len(self._heap)
        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            smallest = i
            if left < n and self._heap[left] < self._heap[smallest]:
                smallest = left
            if right < n and self._heap[right] < self._heap[smallest]:
                smallest = right
            if smallest == i:
                return
            self._heap[i], self._heap[smallest] = (
                self._heap[smallest],
                self._heap[i],
            )
            i = smallest
class HeapPriorityQueue[K, V]:
    def __init__(self) -> None:
        self._heap: Heap[tuple[K, V]] = Heap()

    def __len__(self) -> int:
        return len(self._heap)

    def push(self, priority: K, item: V) -> None:
        self._heap.push((priority, item))

    def pop(self) -> tuple[K, V]:
        return self._heap.pop_min()
