import requests
import concurrent.futures
import time
import statistics
from datetime import datetime

URL = "http://knative-fn4.default.127.0.0.1.nip.io/fib"
TOTAL_REQUESTS = 2     # Total requests to send
CONCURRENCY_LEVEL = 2   # Simultaneous connections
TIMEOUT = 15              # Seconds before timing out
RETRIES = 2               # Number of retry attempts

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
            
            # Track status codes
            status = response.status_code
            status_codes[status] = status_codes.get(status, 0) + 1
            
            if response.ok:
                response_times.append(duration)
                success_count += 1
                return (request_id, duration, status, None)
            
            # Retry server errors (5xx)
            elif 500 <= status < 600 and attempt < RETRIES:
                continue  
                
            else:
                failed_count += 1
                return (request_id, None, status, None)

        except Exception as e:
            if attempt < RETRIES:
                time.sleep(0.1 * (attempt + 1))  # Add backoff
                continue
            failed_count += 1
            errors.append(str(e))
            return (request_id, None, None, str(e))

    return (request_id, None, None, "Max retries exceeded")

print(f"🚀 Starting load test with {TOTAL_REQUESTS} requests @ {CONCURRENCY_LEVEL} concurrency")
start_total = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY_LEVEL) as executor:
    # Create all futures first
    futures = [executor.submit(send_request, i) for i in range(TOTAL_REQUESTS)]
    
    # Process results as they complete
    for i, future in enumerate(concurrent.futures.as_completed(futures)):
        req_id, duration, status, error = future.result()
        
        # Progress tracking
        if (i + 1) % 50 == 0:
            print(f"📊 Processed {i+1}/{TOTAL_REQUESTS} requests "
                  f"({(i+1)/TOTAL_REQUESTS:.1%})")
        
        # Output formatting
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
    'rps': success_count / total_duration if total_duration > 0 else 0
}

print("\n📈 Final Statistics")
print("-------------------")
print(f"Total requests:    {TOTAL_REQUESTS}")
print(f"Successful:        {success_count} ({success_count/TOTAL_REQUESTS:.1%})")
print(f"Failed:            {failed_count} ({failed_count/TOTAL_REQUESTS:.1%})")
print(f"Total duration:    {total_duration:.2f}s")
print(f"Requests/sec:      {metrics['rps']:.1f}")
print("\n⏱ Response Times (successful):")
print(f"Average:           {metrics['avg']:.3f}s")
print(f"Minimum:           {metrics['min']:.3f}s")
print(f"Maximum:           {metrics['max']:.3f}s")
print(f"95th percentile:   {metrics['p95']:.3f}s")
print("\n🔧 Technical Details:")
print(f"Concurrency level: {CONCURRENCY_LEVEL}")
print(f"Timeout:           {TIMEOUT}s")
print(f"Retries:           {RETRIES}")
print("Status code distribution:")
for code, count in status_codes.items():
    print(f" - HTTP {code}: {count} requests")
if errors:
    print("\n🚨 Top Errors:")
    for err in set(errors[:5]):  # Show unique errors
        print(f"- {err} ({errors.count(err)} occurrences)")
