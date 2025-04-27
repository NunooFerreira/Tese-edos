import re
import argparse

def detect_increases(log_path, threshold=0.2):
    """
    Parse the log file at log_path and print timestamps and concurrency levels
    when a request's duration increases by more than threshold (fractional) compared to the previous request.
    """
    prev_duration = None
    concurrency = None
    # Regex to detect concurrency level
    pattern_start = re.compile(r"--- Starting concurrency (\d+)")
    # Regex to parse log lines: timestamp,duration,HTTP code
    pattern_line = re.compile(
        r"(?P<time>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+),(?P<dur>[\d\.]+),HTTP"
    )

    try:
        with open(log_path, 'r') as f:
            for line in f:
                # Check for concurrency change
                m_start = pattern_start.search(line)
                if m_start:
                    concurrency = int(m_start.group(1))
                    prev_duration = None  # reset when concurrency changes
                    continue

                # Check for log entry line
                m_line = pattern_line.search(line)
                if m_line and concurrency is not None:
                    timestamp = m_line.group('time')
                    duration = float(m_line.group('dur'))

                    if prev_duration is not None:
                        # Check if increase exceeds threshold
                        if duration > prev_duration * (1 + threshold):
                            print(f"{timestamp}  Concurrency={concurrency}  Duration increased: {prev_duration:.3f}s -> {duration:.3f}s")

                    prev_duration = duration
    except FileNotFoundError:
        print(f"Error: Log file not found at '{log_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Detect >20% increases in request durations from a concurrency log file.'
    )
    parser.add_argument(
        'log_path',
        nargs='?',
        default='logs/templogs.txt',
        help='Path to the log file (default: log/templogs.txt)'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.6,
        help='Threshold for increase detection as a fraction (default: 0.2 for 30%)'
    )
    args = parser.parse_args()
    detect_increases(args.log_path, args.threshold)
