#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta, timezone
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

# -----------------------
# Configuration
# -----------------------
OPENCOST_HOST    = "10.255.32.113:32079"
POD_PREFIX       = "knative-fn4-"
START_TIME_STR   = "2025-04-23T00:00:00Z"
END_TIME_STR     = "2025-04-23T12:51:10Z"
OUTPUT_PNG       = "cost_rate.png"
DATA_TXT_PATH    = "data/deltacostdata.txt"

# Ensure data directory exists
os.makedirs(os.path.dirname(DATA_TXT_PATH), exist_ok=True)

# -----------------------
# Helper Functions
# -----------------------

def fetch_allocation_data(start: str, end: str):
    url = f"http://{OPENCOST_HOST}/model/allocation"
    params = {"window": f"{start},{end}", "aggregate": "pod"}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json().get("data", [])

def extract_cost_intervals(data, prefix=POD_PREFIX):
    intervals = []
    for bucket in data:
        for pod_name, pod in bucket.items():
            if not pod_name.startswith(prefix):
                continue
            start = datetime.fromisoformat(pod["start"].replace("Z", "+00:00"))
            end   = datetime.fromisoformat(pod["end"].replace("Z", "+00:00"))
            cost  = float(pod.get("totalCost", 0.0))
            intervals.append((pod_name, start, end, cost))
    return intervals

def compute_cost_rate(intervals):
    if not intervals:
        return [], []
    # Single-interval flat rate
    if len(intervals) == 1:
        _, s, e, c = intervals[0]
        mins = (e - s).total_seconds() / 60
        rate = c / mins if mins > 0 else 0.0
        return [s, e], [rate, rate]

    # Multi-interval differential
    pts = sorted({t for (_, s, e, _) in intervals for t in (s, e)})
    sums = [sum(c for (_, s, e, c) in intervals if s <= t < e) for t in pts]
    times, rates = [], []
    for i in range(len(pts)-1):
        t0, t1 = pts[i], pts[i+1]
        dt_min = (t1 - t0).total_seconds() / 60
        drate  = (sums[i+1] - sums[i]) / dt_min if dt_min > 0 else 0.0
        times.append(t0)
        rates.append(drate)
    return times, rates

def plot_cost_rate(x, y, out_path):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.step(x, y, where='post', color='tab:blue', linewidth=1.5)
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0,30]))
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15,45]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    if x:
        ax.set_xlim(x[0] - timedelta(minutes=30), x[-1] + timedelta(minutes=30))
    ax.grid(which='major', linestyle='--', alpha=0.5)
    ax.grid(which='minor', linestyle=':', alpha=0.3)
    ax.set_xlabel('Time')
    ax.set_ylabel('Cost Rate ($/min)')
    ax.set_title(f"Cost Rate for {POD_PREFIX} Functions\n{START_TIME_STR} to {END_TIME_STR}")
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

# -----------------------
# Main
# -----------------------

def main():
    # 1) Fetch & extract
    data = fetch_allocation_data(START_TIME_STR, END_TIME_STR)
    intervals = extract_cost_intervals(data)
    if not intervals:
        print("No matching intervals found.")
        return

    # 2) Compute cost rate
    times, rates = compute_cost_rate(intervals)

    # 3) Dump raw and computed data to text file
    with open(DATA_TXT_PATH, 'w') as f:
        f.write("# Pod intervals and costs:\n")
        for pod_name, s, e, c in intervals:
            f.write(f"{pod_name}\t{s.isoformat()}\t{e.isoformat()}\t${c:.5f}\n")
        f.write("\n# Computed cost rate ($/min) over time:\n")
        for t, r in zip(times, rates):
            f.write(f"{t.isoformat()}\t{r:.5f}\n")
    print(f"Raw and computed data saved to {DATA_TXT_PATH}")

    # 4) Plot
    plot_cost_rate(times, rates, OUTPUT_PNG)
    print(f"Plot saved as {OUTPUT_PNG}")

if __name__ == "__main__":
    main()
