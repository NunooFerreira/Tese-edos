#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

# -----------------------
# Configuration
# -----------------------
DATA_TXT_PATH = "data/deltacostdata.txt"
OUTPUT_PNG    = "cost_rate_from_file.png"
POD_PREFIX    = "knative-fn4-"

# -----------------------
# Parsing Functions
# -----------------------

def parse_deltacost_file(path):
    """
    Returns two lists:
      intervals: [(pod_name, start_dt, end_dt, cost), ...]
      rates:     [(time_dt, rate), ...]
    Assumes file has two sections separated by a blank line:
      1) pod intervals: pod_name   start_iso   end_iso   $cost
      2) computed rates: time_iso   rate
    """
    intervals = []
    rates     = []
    section = 0

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                section += 1
                continue
            # Skip comment lines
            if line.startswith("#"):
                continue

            parts = line.split()
            if section == 0:
                # pod_name, start, end, cost
                pod, start_s, end_s, cost_s = parts
                start = datetime.fromisoformat(start_s)
                end   = datetime.fromisoformat(end_s)
                cost  = float(cost_s.lstrip('$'))
                intervals.append((pod, start, end, cost))
            else:
                # time, rate
                time_s, rate_s = parts
                t = datetime.fromisoformat(time_s)
                r = float(rate_s)
                rates.append((t, r))

    return intervals, rates

# -----------------------
# Plotting Function
# -----------------------

def plot_cost_rate_from_data(rates, out_path):
    """
    Step-plot of cost rate over time with styled axes,
    matching the Prometheus-driven version’s look.
    """
    if not rates:
        print("No rate data to plot.")
        return

    # Split into x and y
    times, vals = zip(*rates)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.step(times, vals, where='post', color='tab:blue', linewidth=1.5)

    # Major ticks every 30 minutes; minor every 15
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0,30]))
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15,45]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # Integer Y ticks
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # X padding ±30 min
    ax.set_xlim(times[0] - timedelta(minutes=30),
                times[-1] + timedelta(minutes=30))

    # Grid styling
    ax.grid(which='major', linestyle='--', alpha=0.5)
    ax.grid(which='minor', linestyle=':', alpha=0.3)

    ax.set_xlabel('Time')
    ax.set_ylabel('Cost Rate ($/min)')
    ax.set_title('Cost Rate for knative-fn4 Functions\n(from data/deltacostdata.txt)')

    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Plot saved as {out_path}")

# -----------------------
# Main Execution
# -----------------------

def main():
    if not os.path.isfile(DATA_TXT_PATH):
        print(f"Data file not found: {DATA_TXT_PATH}")
        return

    intervals, rates = parse_deltacost_file(DATA_TXT_PATH)

    # (optional) verify intervals match prefix
    intervals = [iv for iv in intervals if iv[0].startswith(POD_PREFIX)]
    if not intervals:
        print("Warning: no intervals matching prefix found in data file.")

    plot_cost_rate_from_data(rates, OUTPUT_PNG)

if __name__ == "__main__":
    main()
