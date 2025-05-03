#!/usr/bin/env python3
import json
import argparse
from datetime import datetime, timedelta
import matplotlib
# Use a non-interactive backend
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import matplotlib.ticker as ticker


def load_data_from_file(filepath):
    """Load and return the JSON data from a local file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def extract_cost_intervals(data, prefix="knative-fn4-"):
    """
    Given a dict of pod_name -> pod_data (or a nested structure),
    filter keys by `prefix` and return a list of
    (start_datetime, end_datetime, total_cost).
    """
    intervals = []
    for pod_name, pod in data.items():
        if not pod_name.startswith(prefix):
            continue
        # Parse timestamps
        start = datetime.fromisoformat(pod['start'].replace('Z', '+00:00'))
        end   = datetime.fromisoformat(pod['end'].replace('Z', '+00:00'))
        cost  = pod.get('totalCost', 0.0)
        intervals.append((start, end, cost))
    return intervals


def compute_cost_rate(intervals):
    """
    From a list of (start, end, cost) intervals,
    return two lists: times and cost-rate ($/min).

    If there's only one interval, compute its average rate
    and return a flat line across start->end.
    """
    # Handle single-interval case: flat average rate
    if len(intervals) == 1:
        start, end, cost = intervals[0]
        duration_min = (end - start).total_seconds() / 60.0
        rate = cost / duration_min if duration_min > 0 else 0.0
        # Build a flat line from start to end
        return [start, end], [rate, rate]

    # Unique, sorted time points
    time_points = sorted({t for iv in intervals for t in (iv[0], iv[1])})

    # Sum cost of active pods at each time point
    sums = []
    for t in time_points:
        total = sum(iv[2] for iv in intervals if iv[0] <= t < iv[1])
        sums.append(total)

    # Compute rate of change between consecutive points
    x_times = []
    rates   = []
    for i in range(len(time_points) - 1):
        t1 = time_points[i]
        t2 = time_points[i+1]
        dt = (t2 - t1).total_seconds() / 60.0  # minutes
        delta = sums[i+1] - sums[i]
        rate = (delta / dt) if dt > 0 else 0.0
        x_times.append(t1)
        rates.append(rate)

    return x_times, rates


def plot_cost_rate(x, y, out_path):
    """
    Generate and save a step-plot of cost rate over time.
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.step(x, y, where='post', color='tab:blue', linewidth=1.5)

    ax.set_xlabel('Time')
    ax.set_ylabel('Cost Rate ($/min)')
    ax.set_title('Variation of totalCost Over Time for knative-fn4 Pods')

    # Major ticks: every 30 minutes
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))

    # Minor ticks: every 15 minutes
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15, 45]))

    # Set X limits
    if x:
        start_time = x[0] - timedelta(minutes=30)
        end_time = x[-1] + timedelta(minutes=30)
        ax.set_xlim(start_time, end_time)

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
        description="Plot cost rate ($/min) over time for knative-fn4 pods from a JSON file"
    )
    parser.add_argument(
        "json_file",
        help="Path to the JSON file containing pod cost data"
    )
    parser.add_argument(
        "--output",
        default="images/cost_rate.png",
        help="Path to save the resulting plot (default: images/cost_rate.png)"
    )
    args = parser.parse_args()

    raw = load_data_from_file(args.json_file)
    intervals = extract_cost_intervals(raw)
    if not intervals:
        print("No knative-fn4 intervals found in JSON.")
        return

    x, y = compute_cost_rate(intervals)
    plot_cost_rate(x, y, args.output)
    print(f"Plot saved to {args.output}")

if __name__ == '__main__':
    main()
