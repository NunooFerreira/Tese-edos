import subprocess
import time
import random
import yaml

# Configuration
SERVICE_NAME = "knative-fn4"
NAMESPACE = "default"
YAML_FILE = "knative-service4.yaml"
CHECK_INTERVAL = 35   # Seconds between checks
CHANGE_THRESHOLD = 3  # Trigger if pod count increases by more than this
HISTORY_WINDOW = 6    # Track last N pod counts
SLEEP_AFTER_UPDATE = 400  # Seconds to sleep after changing the autoscaling target

# Range for random target values
TARGET_MIN = 82
TARGET_MAX = 82


def get_pod_count():
    """Get the current number of pods for the Knative service."""
    cmd = (
        f"kubectl get pods -n {NAMESPACE} \
"
        f"-l serving.knative.dev/service={SERVICE_NAME} \
"
        f"--field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l"
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0


def update_autoscaling_target(new_target):
    """
    Update the autoscaling annotations in the YAML file and apply the changes.
    Sets a new target plus scale-to-zero grace and retention annotations.
    """
    with open(YAML_FILE, 'r') as file:
        config = yaml.safe_load(file)

    annotations = config.setdefault('spec', {}) \
                      .setdefault('template', {}) \
                      .setdefault('metadata', {}) \
                      .setdefault('annotations', {})

    # Update the main target
    annotations['autoscaling.knative.dev/target'] = str(new_target)
    # Ensure pods scale down quickly to zero when idle
    annotations['autoscaling.knative.dev/scale-to-zero-grace-period'] = "15s"
    annotations['autoscaling.knative.dev/scale-to-zero-pod-retention-period'] = "0s"

    # Save the updated YAML
    with open(YAML_FILE, 'w') as file:
        yaml.dump(config, file)

    # Apply via kubectl
    subprocess.run(f"kubectl apply -f {YAML_FILE}", shell=True, check=True)
    print(f"Updated autoscaling target to {new_target} and set scale-to-zero annotations.")


def detect_attack(pod_history):
    """Detect if current pod count jump exceeds the threshold."""
    if len(pod_history) < 2:
        return False
    min_pods = min(pod_history)
    current_pods = pod_history[-1]
    return (current_pods - min_pods) >= CHANGE_THRESHOLD


def main():
    pod_history = []
    current_target = None

    print("Starting Yo-Yo attack mitigation...")
    while True:
        current_pod_count = get_pod_count()
        print(f"Current pod count: {current_pod_count}")

        # Track pod count history
        pod_history.append(current_pod_count)
        if len(pod_history) > HISTORY_WINDOW:
            pod_history.pop(0)

        # If we detect a pod spike, adjust autoscaling
        if detect_attack(pod_history):
            print("Detected Yo-Yo attack! Adjusting autoscaling annotations...")
            # Choose a new target in [TARGET_MIN, TARGET_MAX]
            new_target = random.randint(TARGET_MIN, TARGET_MAX)
            while new_target == current_target:
                new_target = random.randint(TARGET_MIN, TARGET_MAX)

            update_autoscaling_target(new_target)
            current_target = new_target
            # Reset history to avoid repeated triggers
            pod_history = [current_pod_count]
            # Sleep to allow new settings to take effect
            time.sleep(SLEEP_AFTER_UPDATE)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
