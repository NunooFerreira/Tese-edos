import aiohttp
import asyncio
import time
from datetime import datetime

# Configuration
TARGET_URL = "http://knative-fn4.default.127.0.0.1.nip.io/fib"
MAX_CONCURRENCY = 150          # max lopp
PAUSE_BETWEEN_ROUNDS = 30      # Seconds to wait between each concurrency level
CONNECTION_TIMEOUT = aiohttp.ClientTimeout(total=10)
LOG_FILE = "logs/responsetime_killchain.log"

async def logger(queue, log_file):
    """Asynchronously write log messages from the queue to the file."""
    loop = asyncio.get_running_loop()
    while True:
        message = await queue.get()
        if message is None:
            break
        # Use run_in_executor to avoid blocking
        await loop.run_in_executor(None, write_log, log_file, message)


def write_log(log_file, message):
    """Helper to write and flush a message to the log file."""
    log_file.write(message)
    log_file.flush()

async def send_request(session, queue):
    """Send a single GET request and put the result into the queue."""
    start_time = time.perf_counter()
    timestamp = datetime.now().isoformat()
    try:
        async with session.get(TARGET_URL) as response:
            await response.text()
            duration = time.perf_counter() - start_time
            status = response.status
            message = f"{timestamp},{duration:.3f},HTTP {status}\n"
    except Exception as e:
        duration = time.perf_counter() - start_time
        message = f"{timestamp},{duration:.3f},FAIL,{str(e)}\n"
    await queue.put(message)

async def main():
    print("Async Concurrency Sweep Script")
    print(f"Target: {TARGET_URL}")
    print(f"Max concurrency: {MAX_CONCURRENCY}")
    start_overall = time.time()

    # Open log file and start logger task
    with open(LOG_FILE, "a") as log_file:
        queue = asyncio.Queue()
        logger_task = asyncio.create_task(logger(queue, log_file))

        connector = aiohttp.TCPConnector(limit=0)
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=CONNECTION_TIMEOUT,
            auto_decompress=True
        ) as session:

            # Log start of the sweep
            await queue.put(f"Concurrency sweep started at {datetime.now().isoformat()}\n")

            # Loop through concurrency levels
            for concurrency in range(1, MAX_CONCURRENCY + 1):
                round_start = datetime.now().isoformat()
                print(f"\nStarting concurrency level: {concurrency} requests")
                await queue.put(f"\n--- Starting concurrency {concurrency} at {round_start} ---\n")

                # Launch concurrent requests
                tasks = [asyncio.create_task(send_request(session, queue))
                         for _ in range(concurrency)]
                # Await completion of all requests for this round
                await asyncio.gather(*tasks)

                # Log completion of this level
                round_end = datetime.now().isoformat()
                await queue.put(f"--- Finished concurrency {concurrency} at {round_end} ---\n")
                print(f"Finished {concurrency} requests. Pausing {PAUSE_BETWEEN_ROUNDS}s...")

                # Pause before next concurrency level
                await asyncio.sleep(PAUSE_BETWEEN_ROUNDS)

            # Log end of the sweep
            await queue.put(f"Concurrency sweep completed at {datetime.now().isoformat()}\n")

        # Signal logger to exit
        await queue.put(None)
        await logger_task

if __name__ == "__main__":
    asyncio.run(main())
