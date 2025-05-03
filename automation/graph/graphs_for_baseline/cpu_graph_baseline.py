#!/usr/bin/env python3
import json
import argparse
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

def load_data_from_file(filepath):
    """Load and return the JSON data from a local file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def extract_pod_intervals(data, prefix="knative-fn4-"):
    """
    From a dict of pod_name -> pod_data, filter for names
    starting with `prefix` and return a list of
    (start_datetime, end_datetime, cpu_usage, cpu_request).
    """
    intervals = []
    for pod_name, pod in data.items():
        if not pod_name.startswith(prefix):
            continue
        start = datetime.fromisoformat(pod['start'].replace('Z', '+00:00'))
        end   = datetime.fromisoformat(pod['end'].replace('Z', '+00:00'))
        usage   = pod.get('cpuCoreUsageAverage', 0.0)
        request = pod.get('cpuCoreRequestAverage', 0.0)
        intervals.append((start, end, usage, request))
    return intervals

def compute_time_series(intervals):
    """
    Given a list of (start, end, usage, request) intervals,
    build two lists x (times) and y (% usage) suitable for a step-plot.
    """
    time_points = sorted({t for iv in intervals for t in (iv[0], iv[1])})
    
    x_vals, y_vals = [], []
    for i in range(len(time_points) - 1):
        t0 = time_points[i]
        active = [iv for iv in intervals if iv[0] <= t0 < iv[1]]
        if active:
            total_usage   = sum(iv[2] for iv in active)
            total_request = sum(iv[3] for iv in active)
            pct = (total_usage / total_request) * 100 if total_request > 0 else 0.0
        else:
            pct = 0.0
        x_vals.append(t0)
        y_vals.append(pct)
    
    x_vals.append(time_points[-1])
    y_vals.append(y_vals[-1] if y_vals else 0.0)
    
    return x_vals, y_vals

def plot_cpu_percentage(x, y, out_path):
    """Generate and save a step-plot of CPU usage % over time."""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.step(x, y, where='post', color='tab:blue', linewidth=1.5)

    ax.set_xlabel('Time')
    ax.set_ylabel('CPU Usage Percentage (%)')
    ax.set_title('CPU Usage Percentage Over Time for knative-fn4 Pods')

    # Major ticks: every 30 minutes
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # Minor ticks: every 15 minutes
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15, 45]))

    # Set X limits
    if x:
        start_time = x[0] - timedelta(minutes=30)
        end_time = x[-1] + timedelta(minutes=30)
        ax.set_xlim(start_time, end_time)

    # Y-axis: percentage (we leave automatic scaling)
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())

    # Grid styling
    ax.grid(which='major', linestyle='--', alpha=0.5)
    ax.grid(which='minor', linestyle=':', alpha=0.3)

    # Rotate labels
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def main():
    parser = argparse.ArgumentParser(
        description="Plot CPU usage % over time for knative-fn4 pods from a JSON file"
    )
    parser.add_argument(
        "json_file",
        help="Path to the JSON file containing pod allocation data"
    )
    parser.add_argument(
        "--output",
        default="images/cpu_usage.png",
        help="Path to save the resulting plot (default: images/cpu_usage.png)"
    )
    args = parser.parse_args()

    raw_data = load_data_from_file(args.json_file)
    pod_intervals = extract_pod_intervals(raw_data)
    x_vals, y_vals = compute_time_series(pod_intervals)
    plot_cpu_percentage(x_vals, y_vals, args.output)
    print(f"Plot saved to {args.output}")

if __name__ == "__main__":
    main()
