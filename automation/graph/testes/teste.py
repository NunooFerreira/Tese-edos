import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter, HourLocator

# Configuration
INPUT_JSON = 'logs_yoyo-attack.json'   # JSON file with OpenCost-like data
OUTPUT_IMAGE = 'images/cpu_usage_percentage.png'
POD_PREFIX = 'knative-fn4-'

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_IMAGE), exist_ok=True)

# Load data from JSON file
with open(INPUT_JSON, 'r') as f:
    raw = json.load(f)

# Extract pod entries (first element under 'data')
all_pods = raw.get('data', [])[0] if raw.get('data') else {}

# Filter pods by prefix
knative_pods = {name: info for name, info in all_pods.items() if name.startswith(POD_PREFIX)}

# Parse pod intervals with CPU usage and request
pod_intervals = []
for info in knative_pods.values():
    try:
        start = datetime.fromisoformat(info['start'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(info['end'].replace('Z', '+00:00'))
        usage = info.get('cpuCoreUsageAverage', 0)
        request = info.get('cpuCoreRequestAverage', 0)
        pod_intervals.append((start, end, usage, request))
    except KeyError:
        continue

# Collect and sort unique time points
time_points = sorted({t for interval in pod_intervals for t in (interval[0], interval[1])})

# Compute CPU usage percentage at each interval start
x_values, y_values = [], []
for i in range(len(time_points) - 1):
    t = time_points[i]
    active = [iv for iv in pod_intervals if iv[0] <= t < iv[1]]
    if active:
        total_usage = sum(iv[2] for iv in active)
        total_request = sum(iv[3] for iv in active)
        percentage = (total_usage / total_request) * 100 if total_request > 0 else 0
    else:
        percentage = 0
    x_values.append(t)
    y_values.append(percentage)

# Extend final point for step plot
x_values.append(time_points[-1])
if y_values:
    y_values.append(y_values[-1])
else:
    y_values.append(0)

# Plot step chart
plt.figure(figsize=(12, 6))
plt.step(x_values, y_values, where='post', color='tab:blue')
plt.xlabel('Time')
plt.ylabel('CPU Usage Percentage (%)')
plt.title('CPU Usage Percentage Over Time for knative-fn4 Pods')

# Set hourly ticks on X axis
ax = plt.gca()
ax.xaxis.set_major_locator(HourLocator(interval=1))
ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))

# Improve layout and grid
plt.grid(True, linestyle='--', alpha=0.7)
plt.gcf().autofmt_xdate()
plt.tight_layout()

# Save plot
plt.savefig(OUTPUT_IMAGE, dpi=300)
plt.close()
print(f"Saved '{OUTPUT_IMAGE}' with hourly ticks on X axis")
