#!/usr/bin/env python3
import json
import argparse
from datetime import datetime
import matplotlib
# Use a non-interactive backend
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

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
    # If the JSON wraps pods under data[0], uncomment below:
    # data = data.get("data", [])[0]

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

    # Otherwise compute deltas as before
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


def plot_cost_rate(x, y, output_path):
    """
    Generate and save a step-plot of cost rate over time.
    """
    plt.figure(figsize=(12, 6))
    plt.step(x, y, where='post', color='red')
    plt.xlabel('Time')
    plt.ylabel('Cost Rate ($/min)')
    plt.title('Variation of totalCost Over Time for knative-fn4 Pods')
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
    plt.gcf().autofmt_xdate()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
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
        default="cost_rate.png",
        help="Path to save the resulting plot (default: cost_rate.png)"
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
