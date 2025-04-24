import sys
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.rcParams.update({'font.size': 14})
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from scipy.interpolate import interp1d

def main(filepath):
    # 1) Read & parse
    times, resp_times = [], []
    with open(filepath, 'r') as f:
        for line in f:
            if not line.strip(): continue
            ts_str, rt_str, _ = line.strip().split(',')
            dt = datetime.fromisoformat(ts_str)
            times.append(dt)
            resp_times.append(float(rt_str))
    # Ensure ascending
    times, resp_times = zip(*sorted(zip(times, resp_times)))
    resp_times = np.array(resp_times)

    # 2) Convert datetimes to matplotlib float days
    num_times = mdates.date2num(times)

    # 3) Interpolate (cubic) on a fine grid
    f_interp = interp1d(num_times, resp_times, kind='cubic')
    num_fine = np.linspace(num_times[0], num_times[-1], 300)
    rt_fine = f_interp(num_fine)
    times_fine = mdates.num2date(num_fine)

    # 4) Plot
    fig, ax = plt.subplots(figsize=(12,6))
    
    # Determine if this is a yoyo attack file
    is_yoyo = 'yoyo' in filepath.lower()
    title = "Response Time (Yoyo Attack)" if is_yoyo else "Response Time Baseline"
    ax.set_title(title, fontsize=16, pad=15)

    # Smooth curve only
    ax.plot(times_fine, rt_fine, color='tab:blue', linewidth=2, zorder=2)
    # Fill under
    ax.fill_between(times_fine, rt_fine, 0, color='tab:blue', alpha=0.5)

    # Axes styling
    ax.set_ylabel('Response Time [s]')
    
    # Smart y-axis limit setting with more detail for yoyo attack
    if is_yoyo:
        # Calculate the 85th percentile for upper limit
        y_max = np.percentile(resp_times, 85)
        # Calculate the median for reference
        y_median = np.median(resp_times)
        # Set the limit to either 2x median or 85th percentile, whichever is larger
        y_limit = max(y_median * 2, y_max)
        ax.set_ylim(0.00, y_limit)
    else:
        ax.set_ylim(0.00, resp_times.max() * 1.05)

    ax.yaxis.grid(True)

    # Hourly ticks, HH:MM labels
    locator = mdates.HourLocator()
    formatter = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.set_xlabel('Time')

    # Adjust X-axis limits
    start_hour = times[0]
    end_hour = times[-1]
    ax.set_xlim(start_hour, end_hour)

    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.7)

    fig.autofmt_xdate()
    fig.tight_layout(pad=1.0)
    
    # Dynamic output filename based on input
    outname = 'yoyo_response_time.png' if is_yoyo else 'baseline_response_time.png'
    fig.savefig(outname, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {outname}")

    # Print statistics to help with debugging
    if is_yoyo:
        print(f"\nStatistics for {filepath}:")
        print(f"Median response time: {np.median(resp_times):.3f}s")
        print(f"85th percentile: {np.percentile(resp_times, 85):.3f}s")
        print(f"Maximum value: {np.max(resp_times):.3f}s")
        print(f"Y-axis limit set to: {y_limit:.3f}s")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <response_log.txt>")
        sys.exit(1)
    main(sys.argv[1])