import requests
import matplotlib
# Set Matplotlib to use a non-interactive backend since there's no GUI
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter

# Fetch data from the OpenCost API
url = "http://10.255.32.113:32079/model/allocation?window=12h&aggregate=pod"
response = requests.get(url)
data = response.json()


# Filter pods starting with "knative-fn4-"
knative_pods = {}
for pod_name, pod_data in data["data"][0].items():
    if pod_name.startswith("knative-fn4-"):
        knative_pods[pod_name] = pod_data

# Parse pod data: start time, end time, CPU usage, and request
pod_intervals = []
for pod_name, pod_data in knative_pods.items():
    start_str = pod_data["start"]
    end_str = pod_data["end"]
    # Convert ISO 8601 strings to datetime objects
    start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
    usage = pod_data["cpuCoreUsageAverage"]
    request = pod_data["cpuCoreRequestAverage"]
    pod_intervals.append((start, end, usage, request))

# Collect all unique start and end times and sort them
time_points = sorted(set([interval[0] for interval in pod_intervals] + 
                         [interval[1] for interval in pod_intervals]))

# Calculate CPU usage percentage for each time interval
x_values = []
y_values = []
for i in range(len(time_points) - 1):
    t_start = time_points[i]
    # Find pods active at t_start (start <= t_start < end)
    active_pods = [pod for pod in pod_intervals if pod[0] <= t_start < pod[1]]
    if active_pods:
        total_usage = sum(pod[2] for pod in active_pods)
        total_request = sum(pod[3] for pod in active_pods)
        # Calculate percentage; set to 0 if total_request is 0
        percentage = (total_usage / total_request) * 100 if total_request > 0 else 0
    else:
        percentage = 0  # No active pods in this interval
    x_values.append(t_start)
    y_values.append(percentage)

# Add the final time point to complete the step plot
x_values.append(time_points[-1])
y_values.append(y_values[-1])  # Extend the last percentage

# Create the step plot
plt.figure(figsize=(12, 6))  # Set figure size
plt.step(x_values, y_values, where='post')  # 'post' means value applies after each x point
plt.xlabel('Time')
plt.ylabel('CPU Usage Percentage (%)')
plt.title('CPU Usage Percentage Over Time for knative-fn4 Pods')
plt.grid(True)  # Add a grid for readability

# Format the x-axis to show dates and times nicely
plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
plt.gcf().autofmt_xdate()  # Rotate date labels for better visibility

# Save the plot to a file
plt.savefig('images/cpu_usage.png')
plt.close()  # Close the figure to free memory

#The script calculates:

#Total Usage = 0.5 + 0.7 = 1.2

#Total Request = 0.3 + 0.4 = 0.7

#Percentage = (1.2 / 0.7) * 100 ≈ 171%