#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

# Configuration
DATA_TXT_PATH = "data/cpu_usage_mitigation_data.txt"
OUTPUT_PNG = "images/cpu_usage_from_file_mitigation.png"

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_PNG), exist_ok=True)

# Parsing function
def parse_cpu_usage_file(path):
    """
    Parses data/cpuusage.txt expecting lines:
      # Timestamp (UTC)\tCPU Usage (%)
      <ISO timestamp>\t<value>
    Returns two lists: timestamps (datetime), values (float).
    """
    timestamps = []
    values = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) != 2:
                continue
            ts_str, val_str = parts
            try:
                t = datetime.fromisoformat(ts_str)
                v = float(val_str)
            except Exception:
                continue
            timestamps.append(t)
            values.append(v)
    return timestamps, values

# Plotting function
def plot_cpu_usage(timestamps, values, out_path):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.step(timestamps, values, where='post', color='tab:blue', linewidth=1.5)

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
    ax.set_ylabel('CPU Usage (%)')
    ax.set_title('knative-fn4 Overall CPU Usage Percentage')

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

    timestamps, values = parse_cpu_usage_file(DATA_TXT_PATH)
    if not timestamps:
        print("No data parsed from file.")
        return

    plot_cpu_usage(timestamps, values, OUTPUT_PNG)

if __name__ == '__main__':
    main()
