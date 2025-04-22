import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter

# Path to your local JSON file (same structure as the API response)
input_file = "logs_yoyo-attack.json"

# Load JSON data from file instead of fetching via HTTP
with open(input_file, 'r') as f:
    data = json.load(f)

# Filter pods whose name starts with "knative-fn4-"
knative_pods = {}
for pod_name, pod_data in data["data"][0].items():
    if pod_name.startswith("knative-fn4-"):
        knative_pods[pod_name] = pod_data

# Extract intervals: start and end timestamps
pod_intervals = []
for pod_name, pod_data in knative_pods.items():
    start = datetime.fromisoformat(pod_data["start"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(pod_data["end"].replace("Z", "+00:00"))
    pod_intervals.append((start, end))

# Gather all unique time points (start and end) and sort them
time_points = sorted(set([interval[0] for interval in pod_intervals] + 
                           [interval[1] for interval in pod_intervals]))

# Count active pods at each time point
x_values = []
pod_counts = []
for t in time_points:
    count = sum(1 for interval in pod_intervals if interval[0] <= t < interval[1])
    x_values.append(t)
    pod_counts.append(count)

# Plot the step chart for pod counts
plt.figure(figsize=(12, 6))
plt.step(x_values, pod_counts, where='post', color='tab:blue')
plt.xlabel('Time')
plt.ylabel('Número de Pods Ativos')
plt.title('Comportamento do Autoscaler: Número de Pods Ativos (knative-fn4)')
plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
plt.gcf().autofmt_xdate()
plt.grid(True)

# Set discrete values for Y-axis\plt.yticks(range(0, max(pod_counts) + 1))

plt.tight_layout()
plt.savefig('images/pod_count2.png')
plt.close()
print("Gráfico 'pod_count.png' salvo.")
