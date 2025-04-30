import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# === Configuration ===
LOG_FILE = "logs20/51requests.log"  # Update this path as needed
OUTPUT_PATH = 'images/killchain_graph51.png'

# === Load & Parse the log ===
# Expect lines like: timestamp,req-<id>,duration,HTTP <status> or ERROR,<error>
df = pd.read_csv(
    LOG_FILE,
    header=None,
    usecols=[0, 2],
    names=["timestamp", "duration"],
    parse_dates=["timestamp"],
)

# === Plotting ===
plt.figure(figsize=(10, 6))
plt.plot(df["timestamp"], df["duration"], color='tab:blue', marker='.', linestyle='None', alpha=0.6)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.gcf().autofmt_xdate()
plt.xlabel("Time")
plt.ylabel("Response Time (seconds)")
plt.title("Response Time over Time")
plt.grid(True)
plt.show()

plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight')
plt.close()

