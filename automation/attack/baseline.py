import csv
import requests
import concurrent.futures
import time
import statistics
from datetime import datetime

URL = "http://knative-fn4.default.127.0.0.1.nip.io/fib"
TOTAL_REQUESTS = 2  # For testing purposes; adjust this for your 24-hour run
CONCURRENCY_LEVEL = 2
TIMEOUT = 15
RETRIES = 2

# Metrics tracking
response_times = []
success_count = 0
failed_count = 0
status_codes = {}
errors = []

# Prepare CSV file for logging
csv_filename = "baseline_metrics.csv"
csv_fields = ["Request_ID", "Timestamp", "Response_Time", "HTTP_Status", "Error_Message"]

# Open CSV file in write mode
with open(csv_filename, "w", newline="") as csvfile:
    csv_writer = csv.DictWriter(csvfile, fieldnames=csv_fields)
    csv_writer.writeheader()

    def log_metrics(request_id, timestamp, duration, status, error):
        # Write metrics to CSV file
        csv_writer.writerow({
            "Request_ID": request_id,
            "Timestamp": timestamp,
            "Response_Time": duration if duration is not None else "",
            "HTTP_Status": status if status is not None else "",
            "Error_Message": error if error else ""
        })
        csvfile.flush()  # Make sure each record is saved immediately

    def send_request(request_id):
        nonlocal success_count, failed_count
        for attempt in range(RETRIES + 1):
            try:
                request_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                start_time = time.perf_counter()
                response = requests.get(URL, timeout=TIMEOUT)
                duration = time.perf_counter() - start_time

                status = response.status_code
                status_codes[status] = status_codes.get(status, 0) + 1

                if response.ok:
                    response_times.append(duration)
                    success_count += 1
                    log_metrics(request_id, request_timestamp, duration, status, None)
                    return (request_id, duration, status, None)
                elif 500 <= status < 600 and attempt < RETRIES:
                    continue  # Retry server errors
                else:
                    failed_count += 1
                    log_metrics(request_id, request_timestamp, None, status, None)
                    return (request_id, None, status, None)

            except Exception as e:
                if attempt < RETRIES:
                    time.sleep(0.1 * (attempt + 1))  # Backoff before retry
                    continue
                failed_count += 1
                error_msg = str(e)
                errors.append(error_msg)
                log_metrics(request_id, request_timestamp, None, None, error_msg)
                return (request_id, None, None, error_msg)

        log_metrics(request_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), None, None, "Max retries exceeded")
        return (request_id, None, None, "Max retries exceeded")

    # Optionally, print a minimal message for start up if needed
    # print(f"Starting load test with {TOTAL_REQUESTS} requests at {CONCURRENCY_LEVEL} concurrency")
    start_total = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY_LEVEL) as executor:
        futures = [executor.submit(send_request, i) for i in range(TOTAL_REQUESTS)]
        for future in concurrent.futures.as_completed(futures):
            _ = future.result()  # We no longer need to print per request results

    total_duration = time.perf_counter() - start_total

# Optionally, you can print a minimal final summary if needed
minimal_summary = (
    f"Load test completed: {TOTAL_REQUESTS} total requests, "
    f"{success_count} successful, {failed_count} failed, "
    f"total time: {total_duration:.2f}s."
)
print(minimal_summary)
