import sys
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.rcParams.update({'font.size': 14})
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from scipy.signal import find_peaks

def main(filepath):
    # 1) Read & parse
    times, resp_times = [], []
    with open(filepath, 'r') as f:
        for line in f:
            if not line.strip(): continue
            ts_str, rt_str, _ = line.strip().split(',')
            dt = datetime.fromisoformat(ts_str)
            times.append(dt)
            resp_times.append(float(rt_str))
    # Ensure ascending
    times, resp_times = zip(*sorted(zip(times, resp_times)))
    resp_times = np.array(resp_times)

    # 2) Convert datetimes to matplotlib float days
    num_times = mdates.date2num(times)

    # 3) Find peaks (local maxima) in the response times
    peaks, _ = find_peaks(resp_times)

    # 4) Create the plot
    fig, ax = plt.subplots(figsize=(10,5))
    ax.set_title("Response Time Baseline Script with Horizontal Peak Connections", fontsize=16, pad=15)

    # Plot real values (scatter plot)
    ax.scatter(times, resp_times, color='tab:purple', zorder=2)

    # 5) Connect higher points with horizontal lines
    highest_value = resp_times[peaks[0]]  # Start with the first peak value
    x_points = [times[peaks[0]]]

    for i in range(1, len(peaks)):
        if resp_times[peaks[i]] >= highest_value:
            # Add the time of the current peak to the x_points list
            x_points.append(times[peaks[i]])
            # Draw the horizontal line between the previous and current peak
            ax.plot([x_points[-2], x_points[-1]], [highest_value, highest_value], color='tab:orange', linewidth=2, zorder=3)
            highest_value = resp_times[peaks[i]]  # Update the highest value

    # Axes styling
    ax.set_ylabel('Response Time [s]')
    ax.set_ylim(0.00, resp_times.max())  # Use max() directly to avoid scaling above 0.8
    ax.yaxis.grid(True)

    # Hourly ticks, HH:MM labels
    locator = mdates.HourLocator()
    formatter = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.set_xlabel('Time')

    # Set X-axis from 01:00 to 13:00 on 2025-04-20
    start_hour = datetime(2025, 4, 20, 1, 0)
    end_hour = datetime(2025, 4, 20, 13, 0)
    ax.set_xlim(start_hour, end_hour)

    fig.autofmt_xdate()
    fig.tight_layout(pad=1.0)
    outname = 'baseline_response_time_with_horizontal_peak_connections.png'
    fig.savefig(outname, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {outname}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <response_log.txt>")
        sys.exit(1)
    main(sys.argv[1])
