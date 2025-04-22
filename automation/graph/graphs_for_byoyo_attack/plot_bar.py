import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter
import os

# File path
log_file = "pod_counts.log"
output_image = "images/pod_count.png"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_image), exist_ok=True)

# Lists to store data
timestamps = []
pod_counts = []

# Read and parse the log file
with open(log_file, 'r') as f:
    for line in f:
        if "Running Pods" in line:
            parts = line.strip().split(" - Running Pods: ")
            time_str = parts[0]
            pod_count = int(parts[1])
            
            timestamps.append(datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
            pod_counts.append(pod_count)

# Plot using step graph
plt.figure(figsize=(12, 6))
plt.step(timestamps, pod_counts, where='post', color='tab:blue')
plt.xlabel('Time')
plt.ylabel('Número de Pods Ativos')
plt.title('Comportamento do Autoscaler: Número de Pods Ativos (Knative)')
plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
plt.gcf().autofmt_xdate()
plt.grid(True)

# Y-axis with discrete values
plt.yticks(range(0, max(pod_counts) + 1))

plt.tight_layout()
plt.savefig(output_image)
plt.close()
print(f"Gráfico '{output_image}' salvo.")
