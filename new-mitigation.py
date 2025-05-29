import subprocess
import time
import random
import yaml

# Configuration
SERVICE_NAME = "knative-fn4"
NAMESPACE = "default"
YAML_FILE = "knative-service4.yaml"
CHECK_INTERVAL = 30  # Seconds
CHANGE_THRESHOLD = 3  # Trigger if pod count increases by more than this
HISTORY_WINDOW = 6    # Track last N pod counts
SLEEP_AFTER_UPDATE = 5 # Seconds to sleep after changing the autoscaling target

# New global variables for YoYo attack response
INCREMENT_MIN = 10
INCREMENT_MAX = 15
COOLDOWN_PERIOD = 2 * 60 * 60  # 2 hours in seconds

# Default autoscaling configuration values
DEFAULT_KPA_SETTINGS = {
    'autoscaling.knative.dev/max-scale': '10',
    'autoscaling.knative.dev/min-scale': '0',
    'autoscaling.knative.dev/target': '50',
    'autoscaling.knative.dev/target-utilization-percentage': '100'
    # If you want specific scale-to-zero or other settings for the default state, add them here.
    # e.g., 'autoscaling.knative.dev/scale-to-zero-grace-period': "60s"
}

# Autoscaling settings specifically for mitigation (e.g., aggressive scale-to-zero)
MITIGATION_SPECIFIC_SETTINGS = {
    'autoscaling.knative.dev/scale-to-zero-grace-period': "10s",
    'autoscaling.knative.dev/scale-to-zero-pod-retention-period': "0s"
}


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
        print("[WARN] Could not parse pod count, returning 0.")
        return 0


def modify_and_apply_yaml(new_autoscaling_annotations):
    """
    Update the autoscaling annotations in the YAML file and apply the changes.
    Removes all existing autoscaling.knative.dev/ annotations and applies the new set.
    """
    print(f"[INFO] Updating autoscaling annotations to: {new_autoscaling_annotations}")
    try:
        with open(YAML_FILE, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"[ERROR] YAML file {YAML_FILE} not found. Cannot apply configuration.")
        # Create a basic structure if file not found, so it can be written to.
        # This might be too presumptive; depends on desired behavior for a missing file.
        # For now, let's assume it should exist or the user handles its creation.
        # If we want to create it:
        # config = {'apiVersion': 'serving.knative.dev/v1', 'kind': 'Service', 'metadata': {'name': SERVICE_NAME}, 'spec': {'template': {'metadata': {'annotations': {}}}}}
        # However, the original script assumes the YAML exists. We'll stick to that.
        return
    except yaml.YAMLError as e:
        print(f"[ERROR] Error parsing YAML file {YAML_FILE}: {e}")
        return


    # Ensure path to annotations exists
    spec = config.setdefault('spec', {})
    template = spec.setdefault('template', {})
    metadata = template.setdefault('metadata', {})
    annotations = metadata.setdefault('annotations', {})

    # Remove existing autoscaling.knative.dev annotations
    for key in list(annotations.keys()):
        if key.startswith('autoscaling.knative.dev/'):
            del annotations[key]

    # Add the new ones
    for key, value in new_autoscaling_annotations.items():
        annotations[key] = str(value) # Ensure all values are strings for YAML

    try:
        with open(YAML_FILE, 'w') as file:
            yaml.dump(config, file)
        print(f"[INFO] YAML file {YAML_FILE} updated.")
    except IOError as e:
        print(f"[ERROR] Could not write to YAML file {YAML_FILE}: {e}")
        return

    try:
        subprocess.run(f"kubectl apply -f {YAML_FILE} -n {NAMESPACE}", shell=True, check=True)
        print("[INFO] kubectl apply successful.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] kubectl apply failed: {e}")


def get_current_autoscaling_target_from_yaml(yaml_file_path):
    """Reads the 'autoscaling.knative.dev/target' from the YAML file."""
    try:
        with open(yaml_file_path, 'r') as file:
            config = yaml.safe_load(file)
        return config['spec']['template']['metadata']['annotations']['autoscaling.knative.dev/target']
    except (FileNotFoundError, KeyError, TypeError, yaml.YAMLError):
        print(f"[WARN] Could not read current target from {yaml_file_path}. File might be missing, malformed, or annotation not set.")
        return None


def detect_attack(pod_history):
    """Detect if current pod count jump exceeds the threshold."""
    if len(pod_history) < 2:
        return False
    # Consider the pod history relevant for an attack detection window
    # Using min over the whole window might be too sensitive if normal scale-downs occur.
    # For this implementation, we stick to the original logic: min over the history window.
    min_pods_in_window = min(pod_history)
    current_pods = pod_history[-1]
    change = current_pods - min_pods_in_window
    detected = change >= CHANGE_THRESHOLD
    if detected:
        print(f"[DEBUG] Attack detection: current_pods={current_pods}, min_pods_in_window={min_pods_in_window}, change={change}, threshold={CHANGE_THRESHOLD}")
    return detected


def main():
    pod_history = []
    
    # Initialize current_target_value
    initial_target_str = get_current_autoscaling_target_from_yaml(YAML_FILE)
    if initial_target_str is not None:
        try:
            current_target_value = int(initial_target_str)
            print(f"[INFO] Initial target read from YAML: {current_target_value}")
            # Check if current YAML settings match default, otherwise, we might be in a manually set state.
            # For simplicity, we'll use this target as the base if an attack occurs.
        except ValueError:
            print(f"[WARN] Invalid target value '{initial_target_str}' in YAML. Applying and using default target from DEFAULT_KPA_SETTINGS.")
            current_target_value = int(DEFAULT_KPA_SETTINGS['autoscaling.knative.dev/target'])
            print(f"[INFO] Applying default KPA settings due to invalid initial target.")
            modify_and_apply_yaml(DEFAULT_KPA_SETTINGS)
            time.sleep(SLEEP_AFTER_UPDATE)
    else:
        print("[INFO] No initial target found in YAML or YAML not readable. Applying and using default target from DEFAULT_KPA_SETTINGS.")
        current_target_value = int(DEFAULT_KPA_SETTINGS['autoscaling.knative.dev/target'])
        modify_and_apply_yaml(DEFAULT_KPA_SETTINGS) # Ensure a known state
        time.sleep(SLEEP_AFTER_UPDATE)

    in_defense_mode = False
    defense_activation_time = 0

    while True:
        print(f"--- Checking @ {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        current_pod_count = get_pod_count()
        print(f"Current pod count: {current_pod_count}, Current KPA target: {current_target_value}, Defense mode: {in_defense_mode}")

        pod_history.append(current_pod_count)
        if len(pod_history) > HISTORY_WINDOW:
            pod_history.pop(0)
        print(f"Pod history (last {HISTORY_WINDOW}): {pod_history}")

        # 1. Check for cooldown expiry if in defense mode
        if in_defense_mode:
            if (time.time() - defense_activation_time) >= COOLDOWN_PERIOD:
                print(f"[INFO] Cooldown period of {COOLDOWN_PERIOD // 3600} hours ended ({COOLDOWN_PERIOD}s). No new attacks detected during this time.")
                print("[INFO] Reverting to default autoscaling configuration.")
                modify_and_apply_yaml(DEFAULT_KPA_SETTINGS)
                current_target_value = int(DEFAULT_KPA_SETTINGS['autoscaling.knative.dev/target'])
                in_defense_mode = False
                defense_activation_time = 0
                pod_history = [] # Reset history as config changed significantly
                print(f"[INFO] System reverted to default. New KPA target: {current_target_value}. Defense mode deactivated.")
                time.sleep(SLEEP_AFTER_UPDATE)
                time.sleep(CHECK_INTERVAL) # Wait for the next full interval
                continue 
            else:
                remaining_cooldown = COOLDOWN_PERIOD - (time.time() - defense_activation_time)
                print(f"[INFO] In defense mode. Cooldown remaining: {remaining_cooldown:.0f} seconds.")

        # 2. Detect attack
        if detect_attack(pod_history):
            print(f"ALERT! Detected potential Yo-Yo attack. Pod history leading to detection: {pod_history}.")
            
            increment = random.randint(INCREMENT_MIN, INCREMENT_MAX)
            new_target = current_target_value + increment
            
            print(f"[MITIGATION] Previous KPA target: {current_target_value}. Increment: {increment}. New proposed KPA target: {new_target}")

            # Prepare the full set of annotations for mitigation
            # Start with default KPA settings, then override for mitigation
            mitigation_annotations_to_apply = DEFAULT_KPA_SETTINGS.copy()
            mitigation_annotations_to_apply['autoscaling.knative.dev/target'] = str(new_target)
            mitigation_annotations_to_apply.update(MITIGATION_SPECIFIC_SETTINGS) # Add/override with specific mitigation settings

            print(f"[MITIGATION] Applying comprehensive mitigation KPA settings: {mitigation_annotations_to_apply}")
            modify_and_apply_yaml(mitigation_annotations_to_apply)
            
            current_target_value = new_target # Update the tracked target value
            
            if not in_defense_mode:
                print("[INFO] Defense mode ACTIVATED.")
                in_defense_mode = True
            else:
                print("[INFO] Defense mode RE-ACTIVATED (attack detected while already in defense mode).")

            defense_activation_time = time.time() # Start/reset cooldown timer
            pod_history = [current_pod_count] # Reset history after action to observe effect of new settings
            
            print(f"[INFO] Mitigation applied. New KPA target: {current_target_value}. Cooldown timer (re)started for {COOLDOWN_PERIOD // 3600} hours.")
            time.sleep(SLEEP_AFTER_UPDATE)
        else:
            print("No Yo-Yo attack pattern detected in current window.")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()