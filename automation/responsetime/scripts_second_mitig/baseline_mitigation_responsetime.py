import sys
import os # Import os module for checking directory existence
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
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    ts_str, rt_str, _ = line.strip().split(',')
                    dt = datetime.fromisoformat(ts_str)
                    times.append(dt)
                    resp_times.append(float(rt_str))
                except ValueError as e:
                    print(f"Skipping malformed line: {line.strip()} - Error: {e}")
                    continue
    except FileNotFoundError:
        print(f"Error: Input file not found at {filepath}")
        sys.exit(1)

    if not times:
        print("Error: No valid data points read from file.")
        sys.exit(1)

    # Ensure ascending
    times, resp_times = zip(*sorted(zip(times, resp_times)))
    resp_times = np.array(resp_times)

    # 2) Convert datetimes to matplotlib float days
    num_times = mdates.date2num(times)

    # 3) Interpolate (cubic) on a fine grid
    # Need at least 4 points for cubic interpolation
    if len(num_times) >= 4:
        f_interp = interp1d(num_times, resp_times, kind='quadratic')
        num_fine = np.linspace(num_times[0], num_times[-1], 300)
        rt_fine = f_interp(num_fine)
        rt_fine = np.clip(rt_fine, 0, None)
        times_fine = mdates.num2date(num_fine)
    else:
        # Fallback to linear interpolation or just plot points if too few data points
        print("Warning: Fewer than 4 data points, using linear interpolation or direct plotting.")
        # Simple linear interpolation for visualization if 2 or 3 points
        if len(num_times) >= 2:
             f_interp = interp1d(num_times, resp_times, kind='linear')
             num_fine = np.linspace(num_times[0], num_times[-1], 300)
             rt_fine = f_interp(num_fine)
             times_fine = mdates.num2date(num_fine)
        else: # Just use the original points if 0 or 1 point (though 0 is handled above)
             times_fine = times
             rt_fine = resp_times


    # 4) Plot
    fig, ax = plt.subplots(figsize=(12,6))

    # Determine if this is a yoyo attack file
    is_yoyo = 'yoyo' in filepath.lower()
    title = "Response Time (Yoyo Attack)" if is_yoyo else "Response Time Baseline"
    ax.set_title(title, fontsize=16, pad=15)

    # Smooth curve (or original points/linear if few data points)
    ax.plot(times_fine, rt_fine, color='tab:blue', linewidth=2, zorder=2)
    # Fill under
    ax.fill_between(times_fine, rt_fine, 0, color='tab:blue', alpha=0.5)

    # Axes styling
    ax.set_ylabel('Response Time [s]')

    # --- MODIFIED Y-AXIS LOGIC ---
    if is_yoyo:
        # Yoyo Attack: Use max(median*2, 85th percentile) to show spikes but avoid extreme outliers
        y_max_pctl = np.percentile(resp_times, 85)
        y_median = np.median(resp_times)
        y_limit = max(y_median * 2, y_max_pctl)
        # Ensure limit is slightly above 0 if data is all near zero
        y_limit = max(y_limit, 0.01)
        ax.set_ylim(0.00, y_limit)
        print(f"\nStatistics for Yoyo Attack {filepath}:")
        print(f"Median response time: {np.median(resp_times):.3f}s")
        print(f"85th percentile: {np.percentile(resp_times, 85):.3f}s")
        print(f"Maximum value: {np.max(resp_times):.3f}s")
        print(f"Y-axis limit set to: {y_limit:.3f}s (max(median*2, 85th percentile))")
    else:
        # Baseline: Use 95th percentile * 1.05 to focus on typical values, ignoring extreme spikes
        y_limit_baseline = np.percentile(resp_times, 95)
        # Add a small buffer (5%)
        y_limit_final = y_limit_baseline * 1.05
        # Handle case where all data is very small or zero, fallback to previous method or a small default
        if y_limit_final < 0.001: # Check if percentile calculation resulted in very small value
             y_limit_final = np.max(resp_times) * 1.05 if np.max(resp_times) > 0 else 0.01
        # Ensure the calculated limit is at least slightly larger than the median if median is significant
        y_limit_final = max(y_limit_final, np.median(resp_times) * 1.5)
        # Set a minimum limit if all else fails
        y_limit_final = max(y_limit_final, 0.01)

        ax.set_ylim(0.00, y_limit_final + 0.01)
        print(f"\nStatistics for Baseline {filepath}:")
        print(f"Median response time: {np.median(resp_times):.3f}s")
        print(f"95th percentile: {np.percentile(resp_times, 95):.3f}s")
        print(f"Maximum value: {np.max(resp_times):.3f}s")
        print(f"Y-axis limit set to: {y_limit_final:.3f}s (based on 95th percentile * 1.05, with min checks)")
    # --- END OF MODIFIED Y-AXIS LOGIC ---

    ax.yaxis.grid(True)

    # Half-hourly ticks: 00 and 30 minutes past each hour
    locator = mdates.MinuteLocator(byminute=[0, 30])
    formatter = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    

    # Adjust X-axis limits
    start_hour = times[0]
    end_hour = times[-1]
    ax.set_xlim(start_hour, end_hour)

    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.7)

    fig.autofmt_xdate()
    fig.tight_layout(pad=1.0)

    # Dynamic output filename based on input, ensure directory exists
    output_dir = 'images'
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        except OSError as e:
            print(f"Error creating output directory {output_dir}: {e}")
            # Fallback to current directory if unable to create
            output_dir = '.'

    outname_base = 'yoyo_response_time.png' if is_yoyo else 'baseline_response_time.png'
    outname = os.path.join(output_dir, outname_base)

    try:
        fig.savefig(outname, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {outname}")
    except Exception as e:
        print(f"Error saving plot to {outname}: {e}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python3 {os.path.basename(sys.argv[0])} <response_log.txt>")
        sys.exit(1)
    main(sys.argv[1])