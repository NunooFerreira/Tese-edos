import requests
import concurrent.futures
import time
import statistics
from datetime import datetime

URL = "http://knative-fn4.default.127.0.0.1.nip.io/fib"
TOTAL_REQUESTS = 151      # Total requests to send
TEST_DURATION = 30        # Spread requests over X seconds (critical for autoscaling)
TIMEOUT = 15              # Seconds before timing out
RETRIES = 2               # Number of retry attempts

# Calculate delay between request starts
REQUEST_INTERVAL = TEST_DURATION / TOTAL_REQUESTS

# Metrics tracking
response_times = []
success_count = 0
failed_count = 0
status_codes = {}
errors = []

def send_request(request_id):
    global success_count, failed_count
    for attempt in range(RETRIES + 1):
        try:
            start_time = time.perf_counter()
            response = requests.get(URL, timeout=TIMEOUT)
            duration = time.perf_counter() - start_time
            
            status = response.status_code
            status_codes[status] = status_codes.get(status, 0) + 1
            
            if response.ok:
                response_times.append(duration)
                success_count += 1
                return (request_id, duration, status, None)
            
            elif 500 <= status < 600 and attempt < RETRIES:
                continue  # Retry server errors
                
            else:
                failed_count += 1
                return (request_id, None, status, None)

        except Exception as e:
            if attempt < RETRIES:
                time.sleep(0.1 * (attempt + 1))
                continue
            failed_count += 1
            errors.append(str(e))
            return (request_id, None, None, str(e))

    return (request_id, None, None, "Max retries exceeded")

print(f"🚀 Starting load test: {TOTAL_REQUESTS} requests over {TEST_DURATION}s")
print(f"📈 Target rate: {TOTAL_REQUESTS/TEST_DURATION:.1f} requests/sec")
start_total = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    
    # Schedule requests with pacing
    for i in range(TOTAL_REQUESTS):
        futures.append(executor.submit(send_request, i))
        if i < TOTAL_REQUESTS - 1:  # No sleep after last request
            time.sleep(REQUEST_INTERVAL)

    # Process results as they complete
    for i, future in enumerate(concurrent.futures.as_completed(futures)):
        req_id, duration, status, error = future.result()
        
        # Progress tracking
        if (i + 1) % 50 == 0:
            elapsed = time.perf_counter() - start_total
            print(f"📊 Processed {i+1}/{TOTAL_REQUESTS} requests "
                  f"({(i+1)/TOTAL_REQUESTS:.1%}) in {elapsed:.1f}s")
        
        # Result output
        if duration is not None:
            print(f"[{req_id}] ✅ {duration:.3f}s (HTTP {status})")
        else:
            error_msg = error if error else f"HTTP {status}"
            print(f"[{req_id}] ❌ {error_msg}")

total_duration = time.perf_counter() - start_total

# Calculate statistics
metrics = {
    'avg': statistics.mean(response_times) if response_times else 0,
    'min': min(response_times) if response_times else 0,
    'max': max(response_times) if response_times else 0,
    'p95': statistics.quantiles(response_times, n=100)[94] if response_times else 0,
    'rps': success_count / total_duration if total_duration > 0 else 0,
    'target_rps': TOTAL_REQUESTS / TEST_DURATION
}

print("\n📈 Final Statistics")
print("-------------------")
print(f"Total requests:    {TOTAL_REQUESTS}")
print(f"Test duration:     {total_duration:.1f}s (target: {TEST_DURATION}s)")
print(f"Successful:        {success_count} ({success_count/TOTAL_REQUESTS:.1%})")
print(f"Failed:            {failed_count} ({failed_count/TOTAL_REQUESTS:.1%})")
print(f"\n🏎️  Throughput:")
print(f"Target RPS:        {metrics['target_rps']:.1f}")
print(f"Actual RPS:        {metrics['rps']:.1f}")
print("\n⏱ Response Times (successful):")
print(f"Average:           {metrics['avg']:.3f}s")
print(f"Minimum:           {metrics['min']:.3f}s")
print(f"Maximum:           {metrics['max']:.3f}s")
print(f"95th percentile:   {metrics['p95']:.3f}s")
print("\n🔧 Technical Details:")
print(f"Timeout:           {TIMEOUT}s")
print(f"Retries:           {RETRIES}")
print("Status code distribution:")
for code, count in status_codes.items():
    print(f" - HTTP {code}: {count} requests")
if errors:
    print("\n🚨 Top Errors:")
    for err in set(errors[:3]):
        print(f"- {err} ({errors.count(err)}x)")

print("\n💡 Pro Tip: If scaling isn't triggering, try:")
print("- Increase TEST_DURATION to 60+ seconds")
print("- Make your endpoint slower (e.g., compute fib(35))")
print("- Adjust Knative's target concurrency in your YAML")