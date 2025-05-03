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
    with open(filepath, 'r') as f:
        return json.load(f)

def extract_pod_intervals(data, prefix="knative-fn4-"):
    intervals = []
    for pod_name, pod in data.items():
        if not pod_name.startswith(prefix):
            continue
        start = datetime.fromisoformat(pod['start'].replace('Z', '+00:00'))
        end   = datetime.fromisoformat(pod['end'].replace('Z', '+00:00'))
        intervals.append((start, end))
    return intervals

def compute_pod_counts(intervals):
    time_points = sorted({t for iv in intervals for t in iv})
    counts = []
    for t in time_points:
        cnt = sum(1 for iv in intervals if iv[0] <= t < iv[1])
        counts.append(cnt)
    return time_points, counts

def plot_pod_counts(x, y, output_path):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.step(x, y, where='post', color='tab:blue', linewidth=1.5)


    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))


    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15, 45]))

    # So os numeros uinteiros neste caso..
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # Se quisres mudar os Y limites.
    min_y = 0
    max_y = max(y) + 1 if y else 1
    ax.set_ylim(min_y, max_y)

    # -30 +30 minutos antes e depois.
    start_time = x[0] - timedelta(minutes=30)
    end_time = x[-1] + timedelta(minutes=30)
    ax.set_xlim(start_time, end_time)

    # Grid style como default.
    ax.grid(which='major', linestyle='--', alpha=0.5)
    ax.grid(which='minor', linestyle=':', alpha=0.3)


    ax.set_xlabel('Time')
    ax.set_ylabel('Running Pods')
    ax.set_title('Number of Running Pods Over Time')

    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
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
        help="Path to save the resulting plot (default: images/pod_count.png)"
    )
    args = parser.parse_args()

    raw = load_data_from_file(args.json_file)
    intervals = extract_pod_intervals(raw)
    x_vals, counts = compute_pod_counts(intervals)
    plot_pod_counts(x_vals, counts, args.output)
    print(f"Plot saved to {args.output}")

if __name__ == '__main__':
    main()
