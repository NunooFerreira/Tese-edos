import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter
import os
import numpy as np

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

# Create figure with appropriate size
plt.figure(figsize=(14, 6))

# Plot as bar chart instead of step
plt.bar(timestamps, pod_counts, width=0.0003, color='#1f77b4', edgecolor='#1f77b4', linewidth=1.2)

# Style improvements
plt.xlabel('Time', fontsize=12)
plt.ylabel('Número de Pods Ativos', fontsize=12)
plt.title('Comportamento do Autoscaler: Número de Pods Ativos (Knative)', fontsize=14)

# Format x-axis with date formatting
plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
plt.xticks(rotation=45)

# Y-axis with discrete values
max_pods = max(pod_counts)
plt.yticks(range(0, max_pods + 2))
plt.ylim(-0.1, max_pods + 0.5)

# Improved grid
plt.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig(output_image, dpi=300)
plt.close()
print(f"Gráfico '{output_image}' salvo.")