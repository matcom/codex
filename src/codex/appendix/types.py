from typing import Protocol, runtime_checkable
from dataclasses import dataclass

@runtime_checkable
class Comparable(Protocol):
    """A protocol for objects that can be compared for ordering."""
    def __lt__(self, other: "Comparable") -> bool: ...

# Modern generic syntax with a type bound to the Comparable protocol
def find_extremum[T: Comparable](collection: list[T], find_min: bool = True) -> T | None:
    """
    Finds either the minimum or maximum value in a collection.
    The type T is bound to the Comparable protocol, ensuring < is supported.
    """
    if not collection:
        return None
    
    result = collection[0]
    for item in collection[1:]:
        # The protocol ensures this comparison is type-safe
        if find_min:
            if item < result:
                result = item
        else:
            if result < item:
                result = item
    return result

@dataclass(frozen=True, order=True)
class Observation:
    timestamp: float
    value: float

# Observation implicitly satisfies Comparable because order=True generates __lt__
data = [Observation(1.2, 10.5), Observation(0.8, 15.2)]
best = find_extremum(data, find_min=False)
print(f"Top observation: {best.value} at {best.timestamp}")
