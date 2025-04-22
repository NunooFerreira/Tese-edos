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


def extract_pod_intervals(data, prefix="knative-fn4-"):
    """
    From a dict of pod_name -> pod_data, filter for names
    starting with `prefix` and return a list of
    (start_datetime, end_datetime).
    """
    # If your JSON wraps pods under data[0], uncomment:
    # data = data.get("data", [])[0]

    intervals = []
    for pod_name, pod in data.items():
        if not pod_name.startswith(prefix):
            continue
        start = datetime.fromisoformat(pod['start'].replace('Z', '+00:00'))
        end   = datetime.fromisoformat(pod['end'].replace('Z', '+00:00'))
        intervals.append((start, end))
    return intervals


def compute_pod_counts(intervals):
    """
    Given a list of (start, end) intervals, return two lists:
    sorted unique time points, and count of active pods at each time.
    """
    # Unique, sorted time points
    time_points = sorted({t for iv in intervals for t in iv})

    counts = []
    for t in time_points:
        cnt = sum(1 for iv in intervals if iv[0] <= t < iv[1])
        counts.append(cnt)

    return time_points, counts


def plot_pod_counts(x, y, output_path):
    """
    Generate and save a step-plot of active pod counts over time.
    """
    plt.figure(figsize=(12, 6))
    plt.step(x, y, where='post', color='tab:blue')
    plt.xlabel('Time')
    plt.ylabel('Number of Active Pods')
    plt.title('Autoscaler Behavior: Active knative-fn4 Pod Count Over Time')
    ax = plt.gca()
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
    plt.gcf().autofmt_xdate()
    plt.grid(True)
    # discrete y-axis ticks
    plt.yticks(range(0, max(y) + 1 if y else 1))
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Plot active knative-fn4 pod counts from a JSON file"
    )
    parser.add_argument(
        "json_file",
        help="Path to the JSON file containing pod allocation data"
    )
    parser.add_argument(
        "--output",
        default="images/pod_count.png",
        help="Path to save the resulting plot (default: pod_count.png)"
    )
    args = parser.parse_args()

    raw = load_data_from_file(args.json_file)
    intervals = extract_pod_intervals(raw)
    x_vals, counts = compute_pod_counts(intervals)
    plot_pod_counts(x_vals, counts, args.output)
    print(f"Plot saved to {args.output}")

if __name__ == '__main__':
    main()
