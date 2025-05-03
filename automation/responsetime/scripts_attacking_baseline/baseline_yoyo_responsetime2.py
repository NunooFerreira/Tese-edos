import sys
import os
from datetime import datetime, timedelta # Import timedelta
import numpy as np
import matplotlib
matplotlib.rcParams.update({'font.size': 14})
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from scipy.interpolate import interp1d
import math # Import math for isnan check
from matplotlib.ticker import MultipleLocator # Importe MultipleLocator aqui

def process_file(filepath):
    """
    Reads, parses, sorts, and interpolates response time data from a file.
    Aligns timestamps to a common arbitrary date for plotting time-of-day comparison.

    Args:
        filepath (str): The path to the input data file.

    Returns:
        tuple: Contains:
            - times (list): List of ALIGNED datetime objects.
            - resp_times (np.array): Array of response times.
            - times_fine (list/np.array): List of ALIGNED datetime objects for interpolated curve.
            - rt_fine (np.array): Array of interpolated response times.
            - is_yoyo (bool): True if 'yoyo' is in the filepath.
            - error_message (str or None): Error message if processing failed, else None.
    """
    times, resp_times = [], []
    error_message = None
    is_yoyo = 'yoyo' in os.path.basename(filepath).lower() # Check base filename

    try:
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                if not line.strip(): continue
                try:
                    # Expecting format: timestamp,response_time[,optional_other_data]
                    parts = line.strip().split(',')
                    if len(parts) < 2:
                        raise ValueError("Line does not contain at least timestamp and response time")
                    ts_str, rt_str = parts[0], parts[1]
                    dt = datetime.fromisoformat(ts_str)
                    rt_val = float(rt_str)
                    if math.isnan(rt_val): # Skip NaN values
                        print(f"Warning: Skipping NaN response time in {filepath} at line {i+1}")
                        continue
                    times.append(dt)
                    resp_times.append(rt_val)
                except ValueError as e:
                    print(f"Warning: Skipping malformed line in {filepath} at line {i+1}: {line.strip()} - Error: {e}")
                    continue
                except Exception as e:
                    print(f"Warning: Unexpected error processing line in {filepath} at line {i+1}: {line.strip()} - Error: {e}")
                    continue
    except FileNotFoundError:
        error_message = f"Error: Input file not found at {filepath}"
        return None, None, None, None, is_yoyo, error_message
    except Exception as e:
        error_message = f"Error: Failed to read file {filepath}: {e}"
        return None, None, None, None, is_yoyo, error_message

    if not times:
        error_message = f"Error: No valid data points read from file {filepath}."
        return None, None, None, None, is_yoyo, error_message

    # --- ALIGNMENT LOGIC (Permanece igual) ---
    try:
        # Determine the start time for this specific file's data
        original_start_time = min(times)
        # Define a common arbitrary time to align all data to
        plotting_start_time = datetime(2000, 1, 1, 0, 0, 0) # Jan 1, 2000, Midnight

        aligned_times = []
        for dt in times:
            # Calculate the time difference from the file's start
            time_delta = dt - original_start_time
            # Add this difference to the common plotting start time
            aligned_dt = plotting_start_time + time_delta
            aligned_times.append(aligned_dt)

        times = aligned_times # Replace original times with aligned times

    except Exception as e:
        error_message = f"Error: Failed to align timestamps for {filepath}: {e}"
        return None, np.array(resp_times), None, None, is_yoyo, error_message # Return raw data if alignment fails

    # Ensure ascending order by ALIGNED time
    try:
        # Sort using the now-aligned 'times' list
        sorted_data = sorted(zip(times, resp_times))
        times, resp_times = zip(*sorted_data)
        resp_times = np.array(resp_times)
        # Convert back to list if preferred, or keep as tuple
        times = list(times)

    except Exception as e:
        error_message = f"Error: Failed to sort data for {filepath} after alignment: {e}"
        # If sorting fails after alignment, interpolation/plotting is unlikely to work correctly
        return times, np.array(resp_times), None, None, is_yoyo, error_message


    # Convert datetimes to matplotlib float days for interpolation (uses the aligned times)
    num_times = mdates.date2num(times)

    # Interpolate (cubic) on a fine grid if enough points, otherwise linear/none
    times_fine, rt_fine = None, None
    # Check for enough unique points for interpolation after sorting
    unique_num_times = np.unique(num_times)

    if len(unique_num_times) >= 4:
        try:
            # Use unique points for interpolation to avoid issues with duplicate x values
            # Need to get the y values corresponding to the unique x values *after* sorting by x
            sorted_resp_times = resp_times[np.argsort(num_times)] # Sort y by x order
            # Now select the y values that correspond to the unique x values
            unique_resp_times = sorted_resp_times[np.searchsorted(np.sort(num_times), unique_num_times)]

            f_interp = interp1d(unique_num_times, unique_resp_times, kind='cubic')
            # Ensure linspace range is valid
            if unique_num_times[-1] > unique_num_times[0]:
                num_fine = np.linspace(unique_num_times[0], unique_num_times[-1], 300)
                rt_fine = f_interp(num_fine)
                times_fine = mdates.num2date(num_fine)
            else: # Handle case where all timestamps are identical or range is invalid after filtering uniques
                print(f"Warning: Cannot interpolate for {filepath}, time range is invalid or too small (unique points).")
                times_fine = times # Use original aligned times/values if interpolation fails
                rt_fine = resp_times
        except ValueError as e:
            print(f"Warning: Cubic interpolation failed for {filepath} (possibly duplicate x values even after unique check?): {e}. Falling back.")
            # Fallback attempt with linear
            if len(unique_num_times) >= 2:
                try:
                     # Need corresponding y for unique x for linear fallback too
                     sorted_resp_times = resp_times[np.argsort(num_times)]
                     unique_resp_times = sorted_resp_times[np.searchsorted(np.sort(num_times), unique_num_times)]

                     f_interp = interp1d(unique_num_times, unique_resp_times, kind='linear', fill_value="extrapolate")
                     if unique_num_times[-1] > unique_num_times[0]:
                         num_fine = np.linspace(unique_num_times[0], unique_num_times[-1], 300)
                         rt_fine = f_interp(num_fine)
                         times_fine = mdates.num2date(num_fine)
                     else:
                         times_fine = times
                         rt_fine = resp_times
                except Exception as le:
                     print(f"Warning: Linear interpolation also failed for {filepath}: {le}. Using raw data.")
                     times_fine = times
                     rt_fine = resp_times
            else:
                times_fine = times
                rt_fine = resp_times
        except Exception as e: # Catch any other interpolation errors
            print(f"Warning: Interpolation failed unexpectedly for {filepath}: {e}. Using raw data.")
            times_fine = times
            rt_fine = resp_times

    elif len(unique_num_times) >= 2:
        print(f"Warning: Fewer than 4 unique data points in {filepath}, using linear interpolation.")
        try:
            # Use unique points for linear interpolation
            sorted_resp_times = resp_times[np.argsort(num_times)]
            unique_resp_times = sorted_resp_times[np.searchsorted(np.sort(num_times), unique_num_times)]

            f_interp = interp1d(unique_num_times, unique_resp_times, kind='linear', fill_value="extrapolate")
            if unique_num_times[-1] > unique_num_times[0]:
                num_fine = np.linspace(unique_num_times[0], unique_num_times[-1], 300)
                rt_fine = f_interp(num_fine)
                times_fine = mdates.num2date(num_fine)
            else:
                times_fine = times
                rt_fine = resp_times
        except Exception as e:
            print(f"Warning: Linear interpolation failed for {filepath}: {e}. Using raw data.")
            times_fine = times
            rt_fine = resp_times
    else:
        print(f"Warning: Fewer than 2 unique data points in {filepath}, plotting raw points.")
        times_fine = times
        rt_fine = resp_times # Use original aligned data directly

    # Ensure rt_fine is a numpy array for calculations
    if rt_fine is not None and not isinstance(rt_fine, np.ndarray):
        rt_fine = np.array(rt_fine)
    # Ensure rt_fine does not contain NaNs introduced by interpolation issues
    if rt_fine is not None:
        rt_fine = np.nan_to_num(rt_fine) # Replace NaNs with 0

    # Return the ALIGNED times for plotting, and the original resp_times for stats
    return times, np.array(resp_times), times_fine, rt_fine, is_yoyo, error_message


def calculate_y_limit(resp_times_np, is_yoyo, filepath):
    """Calculates the appropriate Y-axis upper limit for a dataset."""
    if resp_times_np is None or len(resp_times_np) == 0:
        return 0.01 # Default small limit if no data

    try:
        # Filter out any potential NaNs or infinite values before calculating stats
        finite_resp_times = resp_times_np[np.isfinite(resp_times_np)]
        if len(finite_resp_times) == 0:
             return 0.01 # Return default if no finite data points

        if is_yoyo:
            # Yoyo Attack: Use max(median*2, 85th percentile)
            y_max_pctl = np.percentile(finite_resp_times, 85)
            y_median = np.median(finite_resp_times)
            y_limit = max(y_median * 2, y_max_pctl)
            # Ensure limit is slightly above 0
            y_limit = max(y_limit, 0.01)
            print(f"\nStats for Yoyo {os.path.basename(filepath)}: Median={y_median:.3f}s, 85th={y_max_pctl:.3f}s, Max={np.max(finite_resp_times):.3f}s -> Limit={y_limit:.3f}s")
            return y_limit
        else:
            # Baseline: Use 95th percentile * 1.05
            y_limit_baseline = np.percentile(finite_resp_times, 95)
            y_limit_final = y_limit_baseline * 1.05
            # Handle cases with very small values or ensure limit is above median
            y_median = np.median(finite_resp_times)
            y_max_val = np.max(finite_resp_times)
            if y_limit_final < 0.001:
                 y_limit_final = y_max_val * 1.05 if y_max_val > 0 else 0.01
            y_limit_final = max(y_limit_final, y_median * 1.5)
            y_limit_final = max(y_limit_final, 0.01) # Absolute minimum limit
            print(f"\nStats for Baseline {os.path.basename(filepath)}: Median={y_median:.3f}s, 95th={y_limit_baseline:.3f}s, Max={y_max_val:.3f}s -> Limit={y_limit_final:.3f}s")
            return y_limit_final
    except Exception as e:
        print(f"Error calculating Y limit for {filepath}: {e}. Using max value * 1.05 as fallback.")
        # Fallback if percentile calculation fails
        try:
            finite_resp_times = resp_times_np[np.isfinite(resp_times_np)]
            if len(finite_resp_times) > 0:
                return max(np.max(finite_resp_times) * 1.05, 0.01)
            else:
                 return 0.01
        except: # If even max fails (e.g., empty finite array)
            return 0.01


def main(filepath1, filepath2):
    """
    Main function to process two files and plot a comparison graph,
    aligned by time of day.
    """
    # Process both files
    # Note: times1, times2, times_fine1, times_fine2 will contain ALIGNED datetimes
    # resp1, resp2 will contain the ORIGINAL response times for stats calculations
    times1, resp1, times_fine1, rt_fine1, is_yoyo1, err1 = process_file(filepath1)
    times2, resp2, times_fine2, rt_fine2, is_yoyo2, err2 = process_file(filepath2)

    # Check for processing errors
    if err1:
        print(err1)
    if err2:
        print(err2)

    # Exit if neither file could be processed successfully enough for plotting
    # Check if we have aligned times and rt_fine for plotting
    can_plot1 = times_fine1 is not None and rt_fine1 is not None and len(times_fine1) > 0
    can_plot2 = times_fine2 is not None and rt_fine2 is not None and len(times_fine2) > 0

    if not can_plot1 and not can_plot2:
        print("Error: Neither file could be processed or interpolated for plotting.")
        sys.exit(1)


    # --- Plotting Setup ---
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title("Response Time Comparison (Aligned by Start Time)", fontsize=16, pad=15)
    ax.set_ylabel('Response Time [s]')
    ax.set_xlabel('Time Since Start (HH:MM)') # Updated label


    # --- Plot Data ---
    label1 = os.path.basename(filepath1)
    label2 = os.path.basename(filepath2)

    plot1_successful = False
    if can_plot1:
        try:
            ax.plot(times_fine1, rt_fine1, color='tab:blue', linewidth=2, zorder=2, label=label1)
            # Interpolate original data points for scatter plot if desired (optional)
            # ax.scatter(times1, resp1, color='tab:blue', alpha=0.5, s=10, zorder=4) # Add original points
            ax.fill_between(times_fine1, rt_fine1, 0, color='tab:blue', alpha=0.4)
            plot1_successful = True
        except Exception as e:
            print(f"Error plotting data for {filepath1}: {e}")

    plot2_successful = False
    if can_plot2:
        try:
            ax.plot(times_fine2, rt_fine2, color='tab:red', linewidth=2, zorder=3, label=label2) # zorder=3 to be on top
             # Interpolate original data points for scatter plot if desired (optional)
            # ax.scatter(times2, resp2, color='tab:red', alpha=0.5, s=10, zorder=4) # Add original points
            ax.fill_between(times_fine2, rt_fine2, 0, color='tab:red', alpha=0.3) # Slightly less alpha
            plot2_successful = True
        except Exception as e:
            print(f"Error plotting data for {filepath2}: {e}")

    if not plot1_successful and not plot2_successful:
        print("Error: No data could be plotted.")
        plt.close(fig) # Close the empty figure
        sys.exit(1)

    # --- Axis Limits ---
    # Y-axis: Calculate limits for each dataset (using original response times for stats) and take the max
    y_limit1 = calculate_y_limit(resp1, is_yoyo1, filepath1) if resp1 is not None else 0.01
    y_limit2 = calculate_y_limit(resp2, is_yoyo2, filepath2) if resp2 is not None else 0.01
    final_y_limit = max(y_limit1, y_limit2)

    # Add a buffer to "zoom out" the Y-axis (Mantido)
    y_buffer_factor = 1.2 +0.01# Increase the limit by 20%
    final_y_limit_buffered = final_y_limit * y_buffer_factor

    # Ensure the buffered limit is not excessively small (Mantido)
    final_y_limit_buffered = max(final_y_limit_buffered, 0.01)

    ax.set_ylim(0.00, final_y_limit_buffered) # Use the buffered limit
    print(f"\nOriginal calculated Y-axis limit: {final_y_limit:.3f}s") # Optional: show original limit
    print(f"Final Y-axis limit set to: {final_y_limit_buffered:.3f}s (with {y_buffer_factor*100 - 100:.0f}% buffer)") # Updated print


    # --- NOVO: Definir limites FIXOS para o eixo X (de 00:00 a 12:00) ---
    # Usamos a mesma data base arbitrária que em process_file
    x_start_time = datetime(2000, 1, 1, 0, 0, 0)    # 1 de Janeiro de 2000, 00:00:00 (Início da janela de plotagem)
    x_end_time = datetime(2000, 1, 1, 12, 0, 0)      # 1 de Janeiro de 2000, 12:00:00 (Fim da janela de plotagem)

    # Definir os limites do eixo X explicitamente
    ax.set_xlim(x_start_time, x_end_time)

    # Opcional: Verificar se os dados estão dentro dos limites definidos
    # Note: Esta verificação usa os 'times' ALINHADOS
    all_aligned_times = []
    if times1: all_aligned_times.extend(times1)
    if times2: all_aligned_times.extend(times2)
    if all_aligned_times:
        min_data_time = min(all_aligned_times)
        max_data_time = max(all_aligned_times)
        if min_data_time < x_start_time:
             print(f"Warning: Data starts before 00:00 relative time (at {min_data_time.strftime('%H:%M')}) and will be clipped.")
        if max_data_time > x_end_time:
             print(f"Warning: Data ends after 12:00 relative time (at {max_data_time.strftime('%H:%M')}) and will be clipped.")
    # --- Fim do NOVO ---


    # --- Formatting & Legend ---
    # --- Definir o espaçamento dos ticks do eixo Y (Mantido) ---
    y_tick_interval = 0.003 # O espaçamento desejado
    y_locator = MultipleLocator(y_tick_interval)
    ax.yaxis.set_major_locator(y_locator)
    # --- Fim da definição do espaçamento do Y ---

    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.xaxis.grid(True, linestyle='--', alpha=0.7) # Also add x-grid

    # Format X-axis to show time of day based on the aligned datetimes (Mantido)
    # Usamos AutoDateLocator, mas poderíamos usar HourLocator se quiséssemos ticks a cada hora
    locator = mdates.AutoDateLocator(maxticks=15) # Automatically choose sensible intervals
    # locator = mdates.HourLocator(interval=1) # Alternativa: ticks a cada hora
    formatter = mdates.DateFormatter('%H:%M') # Show Hour and Minute
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    if plot1_successful or plot2_successful: # Add legend only if something was plotted
        ax.legend()

    fig.autofmt_xdate() # Rotate date labels
    fig.tight_layout(pad=1.0)

    # --- Save Figure ---
    output_dir = 'images'
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        except OSError as e:
            print(f"Warning: Could not create output directory {output_dir}. Saving to current directory. Error: {e}")
            output_dir = '.' # Fallback to current directory

    outname = os.path.join(output_dir, 'response_time_comparison_aligned_fixed_x.png') # Nome do ficheiro atualizado
    try:
        fig.savefig(outname, dpi=300, bbox_inches='tight')
        print(f"Saved comparison plot to {outname}")
    except Exception as e:
        print(f"Error saving plot to {outname}: {e}")

    plt.show() # Optionally display the plot interactively


if __name__ == '__main__':
    if len(sys.argv) != 3:
        # Use os.path.basename to get just the script name for usage message
        script_name = os.path.basename(sys.argv[0])
        print(f"Usage: python3 {script_name} <baseline_log.txt> <comparison_log.txt>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])