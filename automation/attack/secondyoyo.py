import aiohttp
import asyncio
import time
from datetime import datetime


# This Script is an asynchronous "YoYo Attack" tool that performs a load test on (http://knative-fn4.default.127.0.0.1.nip.io/fib) by sending HTTP GET requests. 
# It alternates between high-concurrency "attack" phases (200 concurrent requests for 240 seconds) and no-request "cool down" phases (0 requests for 1200 seconds). 
# For each request, it calculates the response time and logs the timestamp, duration (in seconds), and either the HTTP status code or error message to a file (attack_metrics.log). 
# The script runs indefinitely until interrupted, displaying real-time progress (active tasks, elapsed, and remaining time). 
# It uses aiohttp for async requests, manages connections efficiently, and handles logging asynchronously to avoid blocking.


# Configuration
TARGET_URL = "http://knative-fn4.default.127.0.0.1.nip.io/fib"
NORMAL_CONCURRENCY = 0
ATTACK_CONCURRENCY = 200
ON_ATTACK_DURATION = 240
OFF_ATTACK_DURATION = 1200
CONNECTION_TIMEOUT = aiohttp.ClientTimeout(total=10)
LOG_FILE = "attack_metrics.log"

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

async def worker(session, stop_time, queue):
    """Async request worker with response time logging"""
    while time.time() < stop_time:
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

async def run_attack(concurrency, duration, queue):
    """Run async load test"""
    stop_time = time.time() + duration
    connector = aiohttp.TCPConnector(limit=0)
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=CONNECTION_TIMEOUT,
        auto_decompress=True
    ) as session:
        tasks = []
        for _ in range(concurrency):
            task = asyncio.create_task(worker(session, stop_time, queue))
            tasks.append(task)
        
        # Progress monitoring
        start_time = time.time()
        while time.time() < stop_time:
            elapsed = int(time.time() - start_time)
            remaining = int(stop_time - time.time())
            print(f"\rActive: {len(tasks)} | Elapsed: {elapsed}s | Remaining: {remaining}s", end="")
            await asyncio.sleep(1)
        
        # Cleanup
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

async def main():
    """Attack controller"""
    print("Async YoYo Attack Script")
    print(f"Target: {TARGET_URL}")
    print(f"Attack Concurrency: {ATTACK_CONCURRENCY}")
    with open(LOG_FILE, "a") as log_file:
        queue = asyncio.Queue()
        logger_task = asyncio.create_task(logger(queue, log_file))
        try:
            while True:
                print("\n=== ATTACK PHASE ===")
                await run_attack(ATTACK_CONCURRENCY, ON_ATTACK_DURATION, queue)
                print("\n=== COOL DOWN ===")
                await run_attack(NORMAL_CONCURRENCY, OFF_ATTACK_DURATION, queue)
        except KeyboardInterrupt:
            print("\nAttack stopped")
            await queue.put(None)
            await logger_task

if __name__ == "__main__":
    asyncio.run(main())