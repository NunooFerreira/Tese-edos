#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

# Configuration
DATA_TXT_PATH = "data/pods.txt"
OUTPUT_PNG = "images/running_pods_from_file.png"

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_PNG), exist_ok=True)

# Parsing function
def parse_pods_file(path):
    """
    Parses data/pods.txt expecting lines:
      # Timestamp (UTC)\tRunning Pods Count
      <ISO timestamp>\t<count>
    Returns two lists: timestamps (datetime), counts (int).
    """
    timestamps = []
    counts = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) != 2:
                continue
            ts_str, count_str = parts
            try:
                t = datetime.fromisoformat(ts_str)
                cnt = int(count_str)
            except Exception:
                continue
            timestamps.append(t)
            counts.append(cnt)
    return timestamps, counts

# Plotting function
def plot_running_pods(timestamps, counts, out_path):
    fig, ax = plt.subplots(figsize=(10, 4))
    # Step plot
    ax.step(timestamps, counts, where='post', color='tab:blue', linewidth=1.5)
    # X-axis formatting
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15, 45]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    # Y-axis integer ticks
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    # Pad X-axis limits by 30 minutes
    if timestamps:
        start_lim = timestamps[0] - timedelta(minutes=30)
        end_lim = timestamps[-1] + timedelta(minutes=30)
        ax.set_xlim(start_lim, end_lim)
    # Grid styling
    ax.grid(which='major', linestyle='--', alpha=0.5)
    ax.grid(which='minor', linestyle=':', alpha=0.3)
    ax.set_xlabel('Time')
    ax.set_ylabel('Running Pods')
    ax.set_title('Number of Running Pods Over Time (from data file)')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Plot saved as {out_path}")

# Main execution
def main():
    if not os.path.isfile(DATA_TXT_PATH):
        print(f"Data file not found: {DATA_TXT_PATH}")
        return

    timestamps, counts = parse_pods_file(DATA_TXT_PATH)
    if not timestamps:
        print("No data parsed from file.")
        return

    plot_running_pods(timestamps, counts, OUTPUT_PNG)

if __name__ == '__main__':
    main()
