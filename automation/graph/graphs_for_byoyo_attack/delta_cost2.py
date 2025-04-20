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

# Extract intervals: start, end, totalCost
pod_intervals = []
for pod_name, pod_data in knative_pods.items():
    start_str = pod_data["start"]
    end_str = pod_data["end"]
    # Parse ISO timestamps
    start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
    total_cost = pod_data["totalCost"]
    pod_intervals.append((start, end, total_cost))

# Gather all unique time points (start and end) and sort them
time_points = sorted(set([interval[0] for interval in pod_intervals] + 
                           [interval[1] for interval in pod_intervals]))

# Sum the cost of active pods at each time point
x_values = []
cost_sums = []
for t in time_points:
    active_cost = sum(interval[2] for interval in pod_intervals if interval[0] <= t < interval[1])
    x_values.append(t)
    cost_sums.append(active_cost)

# Compute cost change rate (delta per minute) between consecutive points
x_delta = []
cost_rate = []
for i in range(len(x_values) - 1):
    t1 = x_values[i]
    t2 = x_values[i + 1]
    dt_minutes = (t2 - t1).total_seconds() / 60.0
    delta_cost = cost_sums[i + 1] - cost_sums[i]
    rate = delta_cost / dt_minutes if dt_minutes > 0 else 0
    x_delta.append(t1)
    cost_rate.append(rate)

# Plot the step chart
plt.figure(figsize=(12, 6))
plt.step(x_delta, cost_rate, where='post', color='red')
plt.xlabel('Time')
plt.ylabel('Cost Rate ($/min)')
plt.title('Variação do Custo (Delta do totalCost) ao Longo do Tempo para knative-fn4')
plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
plt.gcf().autofmt_xdate()
plt.grid(True)
plt.tight_layout()
plt.savefig('images/cost_rate2.png')
plt.close()
print("Gráfico 'cost_rate.png' salvo.")