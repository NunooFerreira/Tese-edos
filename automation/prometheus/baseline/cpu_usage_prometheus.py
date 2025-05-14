#!/usr/bin/env python3
import os
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from datetime import datetime, timezone, timedelta

# URL + a query que quero:
PROM_HOST       = "10.255.32.113:31752"  # Prometheus host:port
QUERY           = """
(
  sum(rate(container_cpu_usage_seconds_total{namespace="default",pod=~"knative-fn4-.*",container!=""}[5m]))
  /
  sum(kube_pod_container_resource_requests{namespace="default",pod=~"knative-fn4-.*",resource="cpu"})
) * 100
"""
# Meter a window do ataque ou mitigation que preciso:
START_TIME_STR = "2025-05-06T11:08:00Z" 
END_TIME_STR   = "2025-05-06T22:58:00Z" 
STEP           = "30s"                   # High resolution

# Output paths
IMG_PATH      = "baseline_images/cpu_usage_baseline.png"
DATA_DIR      = "data"
DATA_TXT_PATH   = os.path.join(DATA_DIR, "yoyo_cpu_usage.txt")

# Caso os direc nao tenham sido criados:
os.makedirs(os.path.dirname(IMG_PATH), exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Parse times para UTC
start_time = datetime.strptime(START_TIME_STR, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
end_time   = datetime.strptime(END_TIME_STR,   "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

# Aqui fazer o requests da Query em si da Prometheus API 
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

# Escrever no ficheiro para ver se esta tudo ok
with open(DATA_TXT_PATH, "w") as f:
    f.write("# Timestamp (UTC)\tCPU Usage (%)\n")
    for t, v in zip(timestamps, values):
        f.write(f"{t.isoformat()}\t{v:.5f}\n")
print(f"Raw data saved to {DATA_TXT_PATH}")

# -Plot
fig, ax = plt.subplots(figsize=(10, 4))

# Step plot
ax.step(timestamps, values, where='post', linewidth=1.5)

# X axis -
ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15, 45]))

# Y axis 
ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

# Set Y limits
min_y = 0
max_y = max(values) + 5 if values else 100
ax.set_ylim(min_y, max_y)

# Set X limits (+30 minutes before/after)
start_lim = timestamps[0] - timedelta(minutes=30)
end_lim   = timestamps[-1] + timedelta(minutes=30)
ax.set_xlim(start_lim, end_lim)

# Grid settings
ax.grid(which='major', linestyle='--', alpha=0.5)
ax.grid(which='minor', linestyle=':', alpha=0.3)

# Labels & title
ax.set_xlabel('Time')
ax.set_ylabel('CPU Usage (%)')
ax.set_title(f'CPU Usage Percentage Over Time')

# Rotate X labels
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig(IMG_PATH)
plt.close()

print(f"Graph saved as {IMG_PATH}")
