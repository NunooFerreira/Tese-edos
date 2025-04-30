import subprocess
import time
import random
import yaml

# Configuration
SERVICE_NAME = "knative-fn4"
NAMESPACE = "default"
YAML_FILE = "knative-service4.yaml"
CHECK_INTERVAL = 50   # Seconds between checks
CHANGE_THRESHOLD = 4  # Trigger if pod count increases by more than 2 ou seja de 1+3 para 4 Ou seja 300% increase
HISTORY_WINDOW = 6    # Track last 10 pod counts
SLEEP_AFTER_UPDATE = 3600  # Seconds to sleep after changing the autoscaling target
#Mudas o randomizer para 75-85 para ter a certeza que nos primeiros testes daava bem.

def get_pod_count():
    # Get the current number of pods
    cmd = f"kubectl get pods -n {NAMESPACE} -l serving.knative.dev/service={SERVICE_NAME} --no-headers | wc -l"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return int(result.stdout.strip())

def update_autoscaling_target(new_target):
    # Update the autoscaling target in the YAML file and apply it
    with open(YAML_FILE, 'r') as file:
        config = yaml.safe_load(file)
    
    # Update the target annotation to the new value between 55 and 85
    config['spec']['template']['metadata']['annotations']['autoscaling.knative.dev/target'] = str(new_target)
    
    # Save the updated YAML
    with open(YAML_FILE, 'w') as file:
        yaml.dump(config, file)
    
    # Run the kubectl apply command
    subprocess.run(f"kubectl apply -f {YAML_FILE}", shell=True, check=True)
    print(f"Updated autoscaling target to {new_target}")

def detect_attack(pod_history):
    if len(pod_history) < 2:  # Needs at least 2 data points
        return False
    min_pods = min(pod_history)  # Smallest value in history pod, so it triggers based on the smallest value
    current_pods = pod_history[-1]  # Latest pod count
    return (current_pods - min_pods) >= CHANGE_THRESHOLD

def main():
    pod_history = []
    current_target = 50  # Starting target (not used beyond comparison)

    print("Starting Yo-Yo attack mitigation...")
    while True:
        current_pod_count = get_pod_count()
        print(f"Current pod count: {current_pod_count}")
        
        # Track pod count history
        pod_history.append(current_pod_count)
        if len(pod_history) > HISTORY_WINDOW:
            pod_history.pop(0)
        
        # Check for attack conditions: significant increase in pod count
        if detect_attack(pod_history):
            print("Detected Yo-Yo attack! Adjusting autoscaling target...")
            # Choose a new target between 75 and 85
            new_target = random.randint(75, 85)
            while new_target == current_target:  # Ensure the new target is different
                new_target = random.randint(75, 85)
            update_autoscaling_target(new_target)
            current_target = new_target
            # Reset history after adjustment
            pod_history = [current_pod_count]
            # Sleep for 60 seconds before resuming monitoring
            time.sleep(SLEEP_AFTER_UPDATE)
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()