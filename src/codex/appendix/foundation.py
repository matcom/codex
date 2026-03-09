# Variables and f-strings
user_id: int = 101
precision_score: float = 0.985
is_verified: bool = True

# Python 3.12 f-string with nested quotes
status_message = f"User {user_id} is {"Active" if is_verified else "Pending"}"
# Iteration with range and enumerate
data_points = [10.5, 20.3, 15.7]

# range() for fixed iterations
for i in range(3):
    print(f"Iteration {i}")

# enumerate() for index-value pairs
for index, value in enumerate(data_points):
    print(f"Point {index} has value {value}")
def calculate_growth(initial: float, rate: float = 0.05) -> float:
    """Calculates growth based on a starting value and rate."""
    return initial * (1 + rate)

# Flexible invocation
result_a = calculate_growth(100.0)             # Uses default rate
result_b = calculate_growth(100.0, rate=0.08)  # Overrides default
