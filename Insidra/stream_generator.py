import random
from datetime import datetime

USERS = ["U1", "U2", "U3", "U4", "U5"]

def generate_log(step=0):
    now = datetime.now()

    # Default normal behavior
    user = random.choice(USERS)

    # Gradual insider evolution (U5 becomes malicious over time)
    if step > 20:
        user = "U5"

        if step < 50:
            files = random.randint(30, 60)
            sensitivity = random.choice(["low", "medium"])
            failed = random.randint(1, 2)
            location = "Kerala"

        elif step < 100:
            files = random.randint(80, 150)
            sensitivity = random.choice(["medium", "high"])
            failed = random.randint(2, 4)
            location = random.choice(["Kerala", "Unknown"])

        else:
            files = random.randint(200, 400)
            sensitivity = "high"
            failed = random.randint(4, 8)
            location = "Unknown"

    else:
        files = random.randint(10, 25)
        sensitivity = "low"
        failed = random.randint(0, 1)
        location = "Kerala"

    return {
        "emp_id": user,
        "timestamp": now,
        "files_accessed": files,
        "file_sensitivity": sensitivity,
        "location": location,
        "device": random.choice(["laptop", "desktop"]),
        "failed_logins": failed,
        "session_duration": random.randint(30, 120)
    }