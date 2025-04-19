#!/usr/bin/env python3
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
    rt_fine   = f_interp(num_fine)
    times_fine = mdates.num2date(num_fine)

    # 4) Plot
    fig, ax = plt.subplots(figsize=(10,5))
    ax.set_title("Response Time Baseline Script", fontsize=16, pad=15)

    # Smooth curve only
    ax.plot(times_fine, rt_fine, color='tab:purple', linewidth=2, zorder=2)
    # Fill under
    ax.fill_between(times_fine, rt_fine, 0, color='tab:purple', alpha=0.5)

    # Legend with max RT
    max_rt = resp_times.max()
    ax.plot([], [], ' ', label=f"Max Response Time = {max_rt:.3f} s")
    ax.legend(loc='upper right', handlelength=0)

    # Axes styling
    ax.set_ylabel('Response Time [s]')
    ax.set_ylim(0.00, max_rt * 1.05)
    ax.yaxis.grid(True)

    # Hourly ticks, HH:MM labels
    locator = mdates.HourLocator()
    formatter = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.set_xlabel('Time')

    # Align X-axis to start exactly at 14:00
    start_hour = datetime(times[0].year, times[0].month, times[0].day, 14, 0)
    # Handle possible date roll-over at midnight
    if start_hour < times[0]:
        start_hour = start_hour.replace(day=start_hour.day + 1)
    end_hour = datetime(times[-1].year, times[-1].month, times[-1].day, times[-1].hour, 0)
    ax.set_xlim(start_hour, end_hour)



    
    fig.autofmt_xdate()
    fig.tight_layout(pad=1.0)
    outname = 'baseline_response_time.png'
    fig.savefig(outname, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {outname}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <response_log.txt>")
        sys.exit(1)
    main(sys.argv[1])
