from dataclasses import dataclass

@dataclass(slots=True, kw_only=True)
class SearchNode:
    """
    A memory-efficient search node for graph traversal algorithms.
    Using 'slots=True' minimizes the overhead of millions of instances.
    'kw_only=True' prevents errors by forcing explicit parameter names.
    """
    state: str
    parent: "SearchNode | None" = None
    action: str | None = None
    path_cost: float = 0.0
    heuristic_value: float = 0.0

    @property
    def total_cost(self) -> float:
        """The f(n) = g(n) + h(n) value used in algorithms like A*."""
        return self.path_cost + self.heuristic_value

# Instantiation requires explicit keywords, enhancing readability and safety
root = SearchNode(state="Root")
child = SearchNode(
    state="Goal", 
    parent=root, 
    action="MoveRight", 
    path_cost=1.5, 
    heuristic_value=10.0
)
