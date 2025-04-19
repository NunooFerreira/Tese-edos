import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter

# Sample data points extracted from your original graph
# Format: (timestamp string, pod count)
data_points = [
    ("2025-04-18 14:00", 1),
    ("2025-04-18 14:15", 5),
    ("2025-04-18 14:30", 1),
    ("2025-04-18 14:45", 5),
    ("2025-04-18 15:00", 1),
    ("2025-04-18 15:15", 5),
    ("2025-04-18 15:30", 1),
    ("2025-04-18 15:45", 5),
    ("2025-04-18 16:00", 1),
    ("2025-04-18 16:15", 5),
    ("2025-04-18 16:30", 1),
    ("2025-04-18 16:45", 5),
    ("2025-04-18 17:00", 1),
    ("2025-04-18 17:15", 5),
    ("2025-04-18 17:30", 1),
    ("2025-04-18 17:45", 5),
    ("2025-04-18 18:00", 1),
    ("2025-04-18 18:15", 5),
    ("2025-04-18 18:30", 1),
    ("2025-04-18 18:45", 5),
    ("2025-04-18 19:00", 1),
    ("2025-04-18 19:15", 5),
    ("2025-04-18 19:30", 1),
    ("2025-04-18 19:45", 5),
    ("2025-04-18 20:00", 1),
    ("2025-04-18 20:15", 5),
    ("2025-04-18 20:30", 1),
    ("2025-04-18 20:45", 5),
    ("2025-04-18 21:00", 1),
    ("2025-04-18 21:15", 5),
    ("2025-04-18 21:30", 1),
    ("2025-04-18 21:45", 5),
    ("2025-04-18 22:00", 1),
    ("2025-04-18 22:15", 5),
    ("2025-04-18 22:30", 1),
    ("2025-04-18 22:45", 5),
    ("2025-04-18 23:00", 1),
    ("2025-04-18 23:15", 2),  # This will be changed to 5
    ("2025-04-18 23:30", 1),
    ("2025-04-18 23:45", 5),
    ("2025-04-19 00:00", 1),
    ("2025-04-19 00:15", 2),  # This will be changed to 5
    ("2025-04-19 00:30", 0)
]

# Parse timestamps and modify pod counts (change 2 to 5)
x_values = []
pod_counts = []

for timestamp_str, count in data_points:
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
    x_values.append(timestamp)
    # Change any count of 2 to 5
    modified_count = 5 if count == 2 else count
    pod_counts.append(modified_count)

# Plot the graph with modified data
plt.figure(figsize=(12, 6))
plt.step(x_values, pod_counts, where='post', color='purple')
plt.xlabel('Time')
plt.ylabel('Número de Pods Ativos')
plt.title('Comportamento do Autoscaler: Número de Pods Ativos (knative-fn4)')
plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
plt.gcf().autofmt_xdate()
plt.grid(True)

# Set discrete values for Y-axis
plt.yticks(range(0, max(pod_counts)+1))

plt.tight_layout()
plt.savefig('pod_count_modified.png')
plt.close()
print("Gráfico 'pod_count_modified.png' salvo.")