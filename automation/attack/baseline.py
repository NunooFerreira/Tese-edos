import aiohttp
import asyncio
import time
from datetime import datetime

# Configuration
TARGET_URL = "http://knative-fn4.default.127.0.0.1.nip.io/fib"
CONCURRENCY = 1          # Constant concurrency to simulate legitimate traffic
CONNECTION_TIMEOUT = aiohttp.ClientTimeout(total=10)
LOG_FILE = "logs/baseline_metrics.log"
SLEEP_INTERVAL = 1        # Sleep time in seconds between requests for each worker

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
    """Async worker that makes requests, logs metrics, sleeps, and repeats indefinitely"""
    while True:
        start_time = time.perf_counter()
        timestamp = datetime.now().isoformat()
        try:
            async with session.get(TARGET_URL) as response:
                await response.text()  # Consume response
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
    """Main function to simulate continuous legitimate traffic"""
    print("Async Baseline Simulation Script")
    print(f"Target: {TARGET_URL}")
    print(f"Concurrency: {CONCURRENCY}")
    with open(LOG_FILE, "a") as log_file:
        queue = asyncio.Queue()
        logger_task = asyncio.create_task(logger(queue, log_file))
        connector = aiohttp.TCPConnector(limit=0)
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=CONNECTION_TIMEOUT,
            auto_decompress=True
        ) as session:
            tasks = []
            for _ in range(CONCURRENCY):
                task = asyncio.create_task(worker(session, queue))
                tasks.append(task)
            start_time = time.time()
            await queue.put(f"Baseline simulation started at {datetime.now().isoformat()}\n")
            try:
                while True:
                    elapsed = int(time.time() - start_time)
                    print(f"\rActive workers: {len(tasks)} | Elapsed: {elapsed}s", end="")
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\nSimulation stopped")
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                await queue.put(f"Simulation stopped at {datetime.now().isoformat()}\n")
        await queue.put(None)
        await logger_task

if __name__ == "__main__":
    asyncio.run(main())