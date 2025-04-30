import aiohttp
import asyncio
import time
from datetime import datetime
import os

# ── CONFIGURATION ──────────────────────────────────────────────────────────────

TARGET_URL = "http://knative-fn4.default.127.0.0.1.nip.io/fib"
PARALLEL_REQUESTS = 50           # ← Change this to adjust how many parallel requests
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)
LOG_FILE = "logs20/50requests.log"
BURST_INTERVAL = 1                # Seconds to wait between bursts
RUN_DURATION = 12 * 60 * 60       # Total run time in seconds (12 hours)

# ── LOGGER ─────────────────────────────────────────────────────────────────────

async def logger(queue, log_fp):
    loop = asyncio.get_running_loop()
    while True:
        msg = await queue.get()
        if msg is None:
            break
        # offload file I/O so we don’t block the event loop
        await loop.run_in_executor(None, log_fp.write, msg)
        await loop.run_in_executor(None, log_fp.flush)

# ── SINGLE REQUEST ──────────────────────────────────────────────────────────────

async def send_one(session, idx):
    """
    Fire one GET, measure duration, and return a CSV log line.
    """
    start = time.perf_counter()
    ts = datetime.now().isoformat()
    try:
        async with session.get(TARGET_URL) as resp:
            await resp.text()  # ensure full read
            dur = time.perf_counter() - start
            return f"{ts},req-{idx},{dur:.3f},HTTP {resp.status}\n"
    except Exception as e:
        dur = time.perf_counter() - start
        return f"{ts},req-{idx},{dur:.3f},ERROR,{e!r}\n"

# ── MAIN EXECUTION ─────────────────────────────────────────────────────────────

async def main():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    start_time = time.time()

    # Open log and start logger task
    with open(LOG_FILE, "a") as log_fp:
        queue = asyncio.Queue()
        log_task = asyncio.create_task(logger(queue, log_fp))

        connector = aiohttp.TCPConnector(limit=0)
        async with aiohttp.ClientSession(connector=connector,
                                         timeout=REQUEST_TIMEOUT) as session:
            print(f"Starting async parallel load: {PARALLEL_REQUESTS} reqs per burst → {TARGET_URL}")
            iteration = 0

            try:
                while time.time() - start_time < RUN_DURATION:
                    iteration += 1
                    print(f"\rBurst #{iteration}: launching {PARALLEL_REQUESTS} requests...", end="")

                    # Schedule PARALLEL_REQUESTS calls all at once
                    tasks = [
                        asyncio.create_task(send_one(session, i))
                        for i in range(PARALLEL_REQUESTS)
                    ]
                    # Wait for all to complete (errors returned as strings)
                    results = await asyncio.gather(*tasks)

                    # Enqueue their log lines
                    for line in results:
                        await queue.put(line)

                    # throttle between bursts if desired
                    await asyncio.sleep(BURST_INTERVAL)

            except asyncio.CancelledError:
                pass
            except KeyboardInterrupt:
                print("\nInterrupted by user.")

        # signal logger to finish & wait
        await queue.put(None)
        await log_task

    print("Load test complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
