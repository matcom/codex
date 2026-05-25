import math
from typing import Hashable, Iterator


class BloomFilter:
    def __init__(self, expected_items: int, fp_rate: float = 0.01) -> None:
        if expected_items <= 0 or not 0 < fp_rate < 1:
            raise ValueError("expected_items > 0 and 0 < fp_rate < 1")
        self._n_expected = expected_items
        ln2 = math.log(2)
        # m = -n ln(ε) / (ln 2)^2
        m = -expected_items * math.log(fp_rate) / (ln2 ** 2)
        self._m = max(8, int(math.ceil(m)))
        # k = (m/n) ln 2
        k = (self._m / expected_items) * ln2
        self._k = max(1, int(round(k)))
        self._bits = bytearray((self._m + 7) // 8)
    def _hashes(self, item: Hashable) -> Iterator[int]:
        h1 = hash(item)
        h2 = hash((item, "salt"))
        for i in range(self._k):
            yield (h1 + i * h2) % self._m

    def add(self, item: Hashable) -> None:
        for pos in self._hashes(item):
            self._bits[pos // 8] |= 1 << (pos % 8)

    def __contains__(self, item: Hashable) -> bool:
        for pos in self._hashes(item):
            if not (self._bits[pos // 8] & (1 << (pos % 8))):
                return False
        return True
