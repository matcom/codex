# Set membership and set-theoretic operations
allowed_ids = {101, 102, 105, 110}
processed_ids = {101, 105}

# O(1) membership check
is_new = 103 not in allowed_ids

# Set difference to find remaining tasks
pending_ids = allowed_ids - processed_ids  # {102, 110}
def process_command(command):
    """Processes system commands using match/case with guards."""
    match command:
        case ["move", x, y] if x > 0 and y > 0:
            print(f"Moving to positive coordinates: ({x}, {y})")
        case ["move", x, y]:
            print(f"Moving to: ({x}, {y})")
        case ["load", filename]:
            print(f"Loading file: {filename}")
        case ["quit" | "exit"]:
            print("Shutting down...")
        case _:
            print("Unknown command received")
# Python 3.12 f-string with nested quotes and multiline logic
entries = ["success", "error", "pending"]
report = f"Status Summary:\n{"\n".join([f"- {e.upper()}" for e in entries])}"
print(report)
