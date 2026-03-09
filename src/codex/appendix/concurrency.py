def fibonacci_generator(limit: int):
    """
    A generator function for Fibonacci numbers.
    Maintains O(1) space complexity regardless of the 'limit'.
    """
    a, b = 0, 1
    for _ in range(limit):
        yield a
        a, b = b, a + b

# Processing a billion numbers without allocating a massive list
for value in fibonacci_generator(1_000_000_000):
    if value > 10**20:
        break
    # Logic performed on 'value'
import asyncio

async def fetch_resource(resource_id: int, delay: float) -> str:
    """Simulates an asynchronous network request."""
    await asyncio.sleep(delay)
    return f"Data from {resource_id}"

async def run_concurrent_fetches():
    """Demonstrates structured concurrency with TaskGroups."""
    try:
        async with asyncio.TaskGroup() as tg:
            # Tasks are registered and managed by the group
            t1 = tg.create_task(fetch_resource(1, 0.5))
            t2 = tg.create_task(fetch_resource(2, 0.2))
            
        # Results are accessed only after the group successfully closes
        print(f"Fetched: {t1.result()}, {t2.result()}")
    except* Exception as eg:
        # Exceptions from all failed tasks are caught here
        for error in eg.exceptions:
            print(f"Task encountered error: {error}")

# asyncio.run(run_concurrent_fetches())
