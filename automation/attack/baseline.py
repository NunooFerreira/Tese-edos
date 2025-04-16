import requests
import time
from datetime import datetime

URL = "http://knative-fn4.default.127.0.0.1.nip.io/fib"
TIMEOUT = 15
RETRIES = 2
LOG_FILE = "baseline_metrics.log"

def send_request():
    for attempt in range(RETRIES + 1):
        try:
            start_time = time.perf_counter()
            response = requests.get(URL, timeout=TIMEOUT)
            duration = time.perf_counter() - start_time

            if response.ok:
                return (duration, response.status_code, None)
            elif 500 <= response.status_code < 600 and attempt < RETRIES:
                continue
            else:
                return (None, response.status_code, None)
        except Exception as e:
            if attempt < RETRIES:
                time.sleep(0.1 * (attempt + 1))
                continue
            return (None, None, str(e))
    return (None, None, "Max retries exceeded")

# Start loop
with open(LOG_FILE, "a") as log:
    print(f"Baseline script started at {datetime.now().isoformat()}")
    log.write(f"Baseline run started at {datetime.now().isoformat()}\n")

    while True:
        timestamp = datetime.now().isoformat()
        duration, status, error = send_request()

        if duration is not None:
            log.write(f"{timestamp}, {duration:.3f}, HTTP {status}\n")
        else:
            error_msg = error if error else f"HTTP {status}"
            log.write(f"{timestamp}, FAIL, {error_msg}\n")

        log.flush()
        time.sleep(0.5)  # optional: prevent overloading the service (adjust as needed)
