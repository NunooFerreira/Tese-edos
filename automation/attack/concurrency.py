import requests
import concurrent.futures
import time
import statistics
from datetime import datetime

URL = "http://knative-fn4.default.127.0.0.1.nip.io/fib"
TOTAL_REQUESTS = 151      # Total requests to send
TEST_DURATION = 30        # Spread requests over X seconds (critical!)
TIMEOUT = 15              # Seconds before timing out
RETRIES = 2               # Number of retry attempts

# Calculate delay between requests
REQUEST_INTERVAL = TEST_DURATION / TOTAL_REQUESTS

# Metrics tracking
response_times = []
success_count = 0
failed_count = 0
status_codes = {}
errors = []

def send_request(request_id):
    # ... (keep the existing send_request function unchanged) ...

print(f"🚀 Starting load test: {TOTAL_REQUESTS} requests over {TEST_DURATION}s")
start_total = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for i in range(TOTAL_REQUESTS):
        # Submit requests with spacing
        futures.append(executor.submit(send_request, i))
        time.sleep(REQUEST_INTERVAL)  # Critical pacing

    # Process results as they complete
    for i, future in enumerate(concurrent.futures.as_completed(futures)):
        # ... (keep existing result processing logic) ...

total_duration = time.perf_counter() - start_total