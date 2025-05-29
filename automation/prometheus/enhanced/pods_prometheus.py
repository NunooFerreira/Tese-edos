#!/usr/bin/env python3
import os
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from datetime import datetime, timezone, timedelta

# Configuration
PROM_HOST = "10.255.32.113:31752"  # <-- Change if needed
QUERY = """
count by (namespace) (
  kube_pod_status_phase{phase="Running", namespace="default"}
)
"""
# Hardcoded time window (UTC format!)
START_TIME_STR = "2025-05-28T00:49:00Z" 
END_TIME_STR   = "2025-05-28T12:51:00Z" 
STEP = "60"  # sampling interval

# Output paths
IMG_PATH      = "enhanced_images/running_pods_enhanced.png"
DATA_DIR      = "data"
PODS_TXT_PATH = os.path.join(DATA_DIR, "enhanced_data_pods.txt")

# Ensure directories exist
os.makedirs(os.path.dirname(IMG_PATH), exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Parse times
start_time = datetime.strptime(START_TIME_STR, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
end_time   = datetime.strptime(END_TIME_STR,   "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

# Prometheus API call
url = f"http://{PROM_HOST}/api/v1/query_range"
params = {
    "query": QUERY,
    "start": start_time.isoformat(),
    "end":   end_time.isoformat(),
    "step":  STEP
}

print(f"Requesting data from {params['start']} to {params['end']}...")

resp = requests.get(url, params=params)
resp.raise_for_status()
result = resp.json().get("data", {}).get("result", [])

# Extract time-series
timestamps = []
values     = []

if result:
    series = result[0]["values"]
    for ts, val in series:
        t = datetime.fromtimestamp(float(ts), tz=timezone.utc)
        v = float(val)
        timestamps.append(t)
        values.append(v)
else:
    print("No data returned for the query.")
    exit(1)

# --- Dump to text file ---
with open(PODS_TXT_PATH, "w") as f:
    f.write("# Timestamp (UTC)\tRunning Pods Count\n")
    for t, v in zip(timestamps, values):
        f.write(f"{t.isoformat()}\t{int(v)}\n")
print(f"Raw data saved to {PODS_TXT_PATH}")

# --- Plotting ---
fig, ax = plt.subplots(figsize=(10, 4))

# Step plot
ax.step(timestamps, values, where='post', color='tab:blue', linewidth=1.5)

# X axis - Time format and ticks
ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15, 45]))

# Y axis - Integers only
ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

# Set Y limits
min_y = 0
max_y = max(values) + 1 if values else 1
ax.set_ylim(min_y, max_y)

# Set X limits (+30 minutes before/after)
start_lim = timestamps[0] - timedelta(minutes=30)
end_lim   = timestamps[-1] + timedelta(minutes=30)
ax.set_xlim(start_lim, end_lim)

# Grid settings
ax.grid(which='major', linestyle='--', alpha=0.5)
ax.grid(which='minor', linestyle=':', alpha=0.3)

# Labels
ax.set_xlabel('Time')
ax.set_ylabel('Running Pods')
ax.set_title('Number of Running Pods Over Time')

# Rotate X labels
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig(IMG_PATH)
plt.close()

print(f"Plot saved as {IMG_PATH}")
