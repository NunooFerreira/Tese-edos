#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker  # <-- NEW

def read_pod_log(path):
    """
    Reads a log file where each line is:
      YYYY-MM-DD HH:MM:SS - Running Pods: N
    Returns two lists: datetimes, pod_counts
    """
    times = []
    counts = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ts_str, rest = line.split(' - ', 1)
            ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
            try:
                count = int(rest.split(':')[-1].strip())
            except ValueError:
                continue
            times.append(ts)
            counts.append(count)
    return times, counts
def plot_pods(times, counts, outpath):
    # ensure output directory exists
    outdir = os.path.dirname(outpath)
    if outdir and not os.path.isdir(outdir):
        os.makedirs(outdir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(times, counts, color='tab:blue', linewidth=1.5)

    # Major ticks: every 30 minutes
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # Minor ticks every 15 minutes
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15, 45]))

    # --- Force Y-axis to show only integer values ---
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # --- Set Y-axis limits to clean integer boundaries ---
    min_y = 0
    max_y = max(counts) + 1  # One extra for some margin
    ax.set_ylim(min_y, max_y)

    # --- Set X-axis limits ---
    start_time = times[0] - timedelta(minutes=30)
    end_time = times[-1] + timedelta(minutes=30)
    ax.set_xlim(start_time, end_time)

    # Grid styling
    ax.grid(which='major', linestyle='--', alpha=0.5)
    ax.grid(which='minor', linestyle=':', alpha=0.3)

    # Labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Running Pods')
    ax.set_title('Number of Running Pods Over Time')

    # Rotate major tick labels for readability
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(outpath)
    plt.close(fig)

if __name__ == '__main__':
    # --- CONFIGURATION ---
    LOG_FILE = 'baselinepods.txt'    # ← update to your logfile
    OUTPUT_PNG = 'images/runningpods.png'     # ← saved here
    # ----------------------

    times, counts = read_pod_log(LOG_FILE)
    if not times:
        print(f"No valid data found in {LOG_FILE}")
    else:
        plot_pods(times, counts, OUTPUT_PNG)
        print(f"Plot saved to {OUTPUT_PNG}")
