import requests
import concurrent.futures
import time
import statistics

URL = "http://knative-fn4.default.127.0.0.1.nip.io/fib"
TOTAL_REQUESTS = 149         # One request per thread
CONCURRENCY_LEVEL = 149      # Max concurrency to trigger scaling
TIMEOUT = 15
RETRIES = 0                  # We can skip retries for this test

# Metrics
response_times = []
success_count = 0
failed_count = 0
status_codes = {}
errors = []

def send_request(request_id):
    global success_count, failed_count
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
        else:
            failed_count += 1
            return (request_id, None, status, None)

    except Exception as e:
        failed_count += 1
        errors.append(str(e))
        return (request_id, None, None, str(e))

print(f"🚀 Sending {TOTAL_REQUESTS} concurrent requests to test autoscaling...")
start_total = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY_LEVEL) as executor:
    futures = [executor.submit(send_request, i) for i in range(TOTAL_REQUESTS)]
    
    for i, future in enumerate(concurrent.futures.as_completed(futures)):
        req_id, duration, status, error = future.result()
        if duration is not None:
            print(f"[{req_id}] ✅ {duration:.3f}s (HTTP {status})")
        else:
            error_msg = error if error else f"HTTP {status}"
            print(f"[{req_id}] ❌ {error_msg}")

total_duration = time.perf_counter() - start_total

# Print summary
print("\n📈 Summary")
print(f"Total requests:    {TOTAL_REQUESTS}")
print(f"Successful:        {success_count}")
print(f"Failed:            {failed_count}")
print(f"Total duration:    {total_duration:.2f}s")
if response_times:
    print(f"Avg response time: {statistics.mean(response_times):.3f}s")
    print("Status codes:")
    for code, count in status_codes.items():
        print(f" - HTTP {code}: {count}")
