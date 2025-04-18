import aiohttp
import asyncio
import time
from datetime import datetime

# Configuration
TARGET_URL = "http://knative-fn4.default.127.0.0.1.nip.io/fib"
CONCURRENCY = 1              # Constant concurrency to simulate legitimate traffic
CONNECTION_TIMEOUT = aiohttp.ClientTimeout(total=10)
LOG_FILE = "logs/baseline_metrics.log"
SLEEP_INTERVAL = 1            # Seconds between requests for each worker
RUN_DURATION = 12 * 60 * 60   # Total run time in seconds (12 hours)

async def logger(queue, log_file):
    loop = asyncio.get_running_loop()
    while True:
        message = await queue.get()
        if message is None:
            break
        await loop.run_in_executor(None, write_log, log_file, message)


def write_log(log_file, message):
    log_file.write(message)
    log_file.flush()

async def worker(session, queue):
    """Async worker that makes requests, logs metrics, sleeps, and repeats until cancelled"""
    while True:
        start_time = time.perf_counter()
        timestamp = datetime.now().isoformat()
        try:
            async with session.get(TARGET_URL) as response:
                await response.text()
                end_time = time.perf_counter()
                duration = end_time - start_time
                status = response.status
                message = f"{timestamp},{duration:.3f},HTTP {status}\n"
        except Exception as e:
            end_time = time.perf_counter()
            duration = end_time - start_time
            error_msg = str(e)
            message = f"{timestamp},FAIL,{error_msg}\n"
        await queue.put(message)
        await asyncio.sleep(SLEEP_INTERVAL)

async def main():
    print("Async Baseline Simulation Script (12 hours)")
    print(f"Target: {TARGET_URL}")
    print(f"Concurrency: {CONCURRENCY}")

    start_time = time.time()
    with open(LOG_FILE, "a") as log_file:
        queue = asyncio.Queue()
        logger_task = asyncio.create_task(logger(queue, log_file))

        connector = aiohttp.TCPConnector(limit=0)
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=CONNECTION_TIMEOUT,
            auto_decompress=True
        ) as session:
            tasks = [asyncio.create_task(worker(session, queue)) for _ in range(CONCURRENCY)]

            # Log start
            await queue.put(f"Baseline simulation started at {datetime.now().isoformat()}\n")

            # Run for RUN_DURATION seconds
            try:
                while time.time() - start_time < RUN_DURATION:
                    elapsed = int(time.time() - start_time)
                    print(f"\rActive workers: {len(tasks)} | Elapsed: {elapsed}s", end="")
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                pass

            print("\nReached 12 hours. Stopping simulation.")
            # Cancel workers
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

            # Log stop
            await queue.put(f"Simulation stopped at {datetime.now().isoformat()}\n")

        # Signal logger to exit
        await queue.put(None)
        await logger_task

if __name__ == "__main__":
    asyncio.run(main())
