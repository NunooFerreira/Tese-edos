import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

# Define the start and end times
start_time = datetime.datetime(2025, 4, 23, 2, 0) # Year, month, day don't really matter here
end_time = datetime.datetime(2025, 4, 23, 14, 0)

# Create a list of times for the bars
times = []
current_time = start_time
while current_time <= end_time:
    times.append(current_time)
    current_time += datetime.timedelta(minutes=15)

# Create the figure and axes
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the bars
for t in times:
    ax.bar(t, 5, width=datetime.timedelta(minutes=1), color='tab:blue', align='center')

# Set the x-axis limits and format
ax.set_xlim(start_time, end_time)
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

# Set the y-axis limits
ax.set_ylim(0, 5)

# Add labels and title
ax.set_xlabel('Time')
ax.set_ylabel('Value')
ax.set_title('Bar Chart with 15-minute Intervals')

# Add grid lines
ax.grid(True)

# Save the figure
plt.savefig('bar_chart.png')

# Show the plot (optional)
plt.show()