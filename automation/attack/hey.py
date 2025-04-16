import subprocess
import time

# Script com a Baseline...
while True:
    # Execute the hey command
    subprocess.run([
        "hey",
        "-z", "15s",
        "-c", "51",
        "http://knative-fn4.default.127.0.0.1.nip.io/fib"
    ])
    
    # Wait 3 seconds before next execution
    time.sleep(3)
    flag += 1
