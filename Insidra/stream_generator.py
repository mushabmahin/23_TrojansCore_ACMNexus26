import random
from datetime import datetime

USERS = ["U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8", "U9", "U10"]

def generate_log(step=0):
    now = datetime.now()

    # Default normal behavior
    user = random.choice(USERS)

    # Gradual insider evolution for suspicious users
    if user in ["U5", "U9", "U10"] and step > 20:
        if step < 50:
            files = random.randint(30, 60)
            sensitivity = random.choice(["low", "medium"])
            failed = random.randint(1, 2)
            location = "Kerala"
            lat, lon = random.uniform(8.0, 12.0), random.uniform(75.0, 77.0)

        elif step < 100:
            files = random.randint(80, 150)
            sensitivity = random.choice(["medium", "high"])
            failed = random.randint(2, 4)
            location = random.choice(["Kerala", "Unknown"])
            if location == "Kerala":
                lat, lon = random.uniform(8.0, 12.0), random.uniform(75.0, 77.0)
            else:
                lat, lon = random.uniform(35.0, 60.0), random.uniform(-10.0, 40.0) # Europe/Unknown

        else:
            files = random.randint(200, 400)
            sensitivity = "high"
            failed = random.randint(4, 8)
            location = "Unknown"
            lat, lon = random.uniform(35.0, 60.0), random.uniform(-10.0, 40.0) # Europe/Unknown

    else:
            files = random.randint(10, 25)
            sensitivity = "low"
            failed = random.randint(0, 1)
            location = "Kerala"
            lat, lon = random.uniform(8.0, 12.0), random.uniform(75.0, 77.0) # Normal Kerala range

    return {
        "emp_id": user,
        "timestamp": now,
        "files_accessed": files,
        "file_sensitivity": sensitivity,
        "location": location,
        "lat": lat,
        "lon": lon,
        "device": random.choice(["laptop", "desktop"]),
        "failed_logins": failed,
        "session_duration": random.randint(30, 120)
    }