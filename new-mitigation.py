import subprocess
import time
import random
import yaml

# Configuration
SERVICE_NAME = "knative-fn4"
NAMESPACE = "default"
YAML_FILE = "knative-service4.yaml"
CHECK_INTERVAL = 50     # Seconds
CHANGE_THRESHOLD = 3    # Trigger if pod count increases by more than this
HISTORY_WINDOW = 5      # Track last N pod counts
SLEEP_AFTER_UPDATE = 5  # Seconds to sleep after changing the autoscaling target

# Target range, it will incremente random value from 10 to 15
INCREMENT_MIN = 10    
INCREMENT_MAX = 15   

# Default 
DEFAULT_ANNOTATIONS = {
    'autoscaling.knative.dev/max-scale': '10',
    'autoscaling.knative.dev/min-scale': '0',
    'autoscaling.knative.dev/target': '50',
    'autoscaling.knative.dev/target-utilization-percentage': '100'
}
DEFAULT_TARGET_VALUE = 50 

# Vai dar Reset depois de passarem 2 horas sem YoYo attack.
RESET_TIME_NO_ATTACK = 120 * 60  


def get_pod_count():
    """Get the current number of pods for the Knative service."""
    cmd = (
        f"kubectl get pods -n {NAMESPACE} "
        f"-l serving.knative.dev/service={SERVICE_NAME} "
        f"--field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l"
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        return int(result.stdout.strip())
    except ValueError:
        print("Error getting pod count. Assuming 0.")
        return 0


def read_current_target():
    """
    Read the current autoscaling target from the YAML file.
    Returns an integer or None if not found.
    """
    try:
        with open(YAML_FILE, 'r') as file:
            config = yaml.safe_load(file)
        annotations = config.get('spec', {}).get('template', {}).get('metadata', {}).get('annotations', {})
        target = annotations.get('autoscaling.knative.dev/target')
        return int(target)
    except FileNotFoundError:
        print(f"Warning: YAML file {YAML_FILE} not found. Cannot read current target.")
        return None
    except (TypeError, ValueError, AttributeError):
        print("Warning: Could not parse current target from YAML. It might be missing or malformed.")
        return None


def update_autoscaling_target(new_target):
    """
    Update the autoscaling annotations in the YAML file and apply the changes.
    Sets a new target plus scale-to-zero grace.
    """
    try:
        with open(YAML_FILE, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: YAML file {YAML_FILE} not found. Cannot update target.")
        config = {'apiVersion': 'serving.knative.dev/v1', 'kind': 'Service', 'metadata': {'name': SERVICE_NAME}, 'spec': {'template': {'metadata': {'annotations': {}}}}}


    annotations = config.setdefault('spec', {}) \
                      .setdefault('template', {}) \
                      .setdefault('metadata', {}) \
                      .setdefault('annotations', {})

    # Update para os novos autoscaling.
    annotations['autoscaling.knative.dev/target'] = str(new_target)
    annotations['autoscaling.knative.dev/scale-to-zero-grace-period'] = "10s"
    annotations['autoscaling.knative.dev/scale-to-zero-pod-retention-period'] = "0s"

    try:
        with open(YAML_FILE, 'w') as file:
            yaml.dump(config, file)
        subprocess.run(f"kubectl apply -f {YAML_FILE} -n {NAMESPACE}", shell=True, check=True, capture_output=True, text=True)
        print(f"Updated autoscaling target to {new_target} and set scale-to-zero annotations.")
    except FileNotFoundError: # Should not happen if we create basic config above
        print(f"Error: YAML file {YAML_FILE} could not be written to.")
    except subprocess.CalledProcessError as e:
        print(f"Error applying kubectl command: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred during autoscaling target update: {e}")


def reset_to_default_autoscaling_config():
    """
    Resets the Knative service's autoscaling configuration to the defined defaults.
    """
    try:
        with open(YAML_FILE, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Warning: YAML file {YAML_FILE} not found. Creating with default structure for reset.")
        config = {'apiVersion': 'serving.knative.dev/v1', 'kind': 'Service', 'metadata': {'name': SERVICE_NAME}, 'spec': {'template': {'metadata': {'annotations': {}}}}}


    annotations = config.setdefault('spec', {}) \
                      .setdefault('template', {}) \
                      .setdefault('metadata', {}) \
                      .setdefault('annotations', {})

    # Set default annotations
    for key, value in DEFAULT_ANNOTATIONS.items():
        annotations[key] = value

    # Remove other specific autoscaling annotations that might have been added
    # during attack mitigation and are not part of the desired default state.
    annotations_to_remove = [
        'autoscaling.knative.dev/scale-to-zero-grace-period',
        'autoscaling.knative.dev/scale-to-zero-pod-retention-period'
    ]
    for key in annotations_to_remove:
        if key in annotations:
            del annotations[key]
    
    
    keys_to_check = list(annotations.keys()) 
    for key in keys_to_check:
        if key.startswith('autoscaling.knative.dev/') and key not in DEFAULT_ANNOTATIONS:
            print(f"Removing non-default autoscaling annotation: {key}")
            del annotations[key]


    try:
        with open(YAML_FILE, 'w') as file:
            yaml.dump(config, file)
        
        subprocess.run(f"kubectl apply -f {YAML_FILE} -n {NAMESPACE}", shell=True, check=True, capture_output=True, text=True)
        print(f"Knative service {SERVICE_NAME} reset to default autoscaling configuration in {YAML_FILE}.")
        for key, value in DEFAULT_ANNOTATIONS.items():
            print(f"  {key}: '{value}'")

    except FileNotFoundError:
        print(f"Error: YAML file {YAML_FILE} could not be written to during reset.")
    except subprocess.CalledProcessError as e:
        print(f"Error applying kubectl command during reset: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred during configuration reset: {e}")


def detect_attack(pod_history):
    """Detect if current pod count jump from a recent minimum in the history window exceeds the threshold."""
    if len(pod_history) < 2:  # Need at least one value 
        return False

    min_val_in_past_window = min(pod_history[:-1])
    current_pods = pod_history[-1]

    increase = current_pods - min_val_in_past_window

    if increase >= CHANGE_THRESHOLD:
        # If the current pod count has increased by 3(or more) to the minimum, its the YoYo Attack

        print(f"Debug: Attack check: Current: {current_pods}, Min in past window ({len(pod_history)-1} values): {min_val_in_past_window}, Increase: {increase}, Threshold: {CHANGE_THRESHOLD}")
        return True
    return False


def main():
    pod_history = []
    current_target = read_current_target() or DEFAULT_TARGET_VALUE
    last_attack_timestamp = time.time() # Initialize to current time

    print(f"Starting Yo-Yo attack mitigation for {SERVICE_NAME} in namespace {NAMESPACE}.")
    print(f"Initial autoscaling target: {current_target}")
    print(f"Configuration will be reset to defaults after {RESET_TIME_NO_ATTACK / 60} minutes without attacks.")
    print(f"Monitoring YAML file: {YAML_FILE}")


    while True:
        current_pod_count = get_pod_count()
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}, Current pod count: {current_pod_count}, Target: {current_target}")

        pod_history.append(current_pod_count)
        if len(pod_history) > HISTORY_WINDOW:
            pod_history.pop(0)

        if detect_attack(pod_history):
            print(f"Yo-Yo attack detected! Pods increased from {min(pod_history[:-1]) if len(pod_history) >=2 else 'N/A'} to {current_pod_count} (recent min vs current).") # Updated log message
            last_attack_timestamp = time.time() # Update last attack time
            
            increment = random.randint(INCREMENT_MIN, INCREMENT_MAX)
            new_target = current_target + increment
            
            print(f"Increasing autoscaling target from {current_target} to {new_target}...")
            update_autoscaling_target(new_target)
            current_target = new_target
            
            pod_history = [current_pod_count] 
            
            print(f"Sleeping for {SLEEP_AFTER_UPDATE} seconds after update.")
            time.sleep(SLEEP_AFTER_UPDATE)
        else:
            # No attack detected, check if it's time to reset
            if (time.time() - last_attack_timestamp) > RESET_TIME_NO_ATTACK:
                print(f"No Yo-Yo attacks detected for {RESET_TIME_NO_ATTACK / 60:.2f} minutes.") 
                
                print("Attempting to reset to default autoscaling configuration...")
                reset_to_default_autoscaling_config()
                current_target = DEFAULT_TARGET_VALUE # Reset current target tracker
                last_attack_timestamp = time.time() # Reset the timer for the next 120-minute window
                print(f"Autoscaling configuration reset. New target: {current_target}.")
                pod_history = [get_pod_count()] # fresh reading for history
            else:
                # This else block is for when no attack is detected AND it's not time to reset
                pass 

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
    except Exception as e:
        print(f"An unexpected critical error occurred in main: {e}")