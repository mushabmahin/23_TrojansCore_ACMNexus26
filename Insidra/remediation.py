import json
import os
import time
from datetime import datetime
import pandas as pd

HISTORY_FILE = "remediation_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def record_action(user_id, action, platform):
    history = load_history()
    
    # Check if this exact action/platform was already applied to prevent duplicates
    for record in history:
        if record["user_id"] == user_id and record["action"] == action:
            return False # Action already applied

    history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "action": action,
        "platform": platform,
        "status": "Success"
    })
    
    save_history(history)
    return True

def suspend_account(user_id):
    """
    Simulates making an API call to Active Directory to suspend an account.
    """
    time.sleep(0.5) # Simulate API latency
    return record_action(user_id, "Suspend Account", "Active Directory")

def unsuspend_account(user_id):
    """
    Reverses an account suspension by removing the corresponding active directory block from history.
    """
    history = load_history()
    
    # Filter out the suspension records for this specific user
    new_history = [r for r in history if not (r["user_id"] == user_id and r["action"] == "Suspend Account")]
    
    # If the length changed, it means we actually unsuspended someone
    if len(new_history) < len(history):
        save_history(new_history)
        return True
    return False

def force_mfa(user_id):
    """
    Simulates making an API call to Okta to force re-authentication.
    """
    time.sleep(0.5)
    return record_action(user_id, "Force MFA", "Okta")

def isolate_device(user_id):
    """
    Simulates making an API call to CrowdStrike to isolate the endpoint.
    """
    time.sleep(0.8)
    return record_action(user_id, "Isolate Device", "CrowdStrike")

def get_remediation_summary_df():
    """
    Returns the remediation history as a pandas DataFrame for the UI.
    """
    history = load_history()
    if not history:
        return pd.DataFrame(columns=["timestamp", "user_id", "action", "platform", "status"])
    
    # Sort backwards so newest events are at top
    return pd.DataFrame(history).iloc[::-1]

def get_applied_actions(user_id):
    """
    Returns a set of actions that have already been applied to a user.
    """
    history = load_history()
    return {record["action"] for record in history if record["user_id"] == user_id}

