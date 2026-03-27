import pandas as pd
import random
from datetime import datetime, timedelta

users = [
    {"id": "U1", "type": "normal"},
    {"id": "U2", "type": "normal"},
    {"id": "U3", "type": "normal"},
    {"id": "U4", "type": "night"},
    {"id": "U5", "type": "insider"},
]

start_date = datetime(2024, 1, 1)
days = 20


def normal_behavior(user, date):
    base_login = 8 + int(user["id"][-1]) % 3  # slight variation per user

    return {
        "user_id": user["id"],
        "timestamp": date,
        "login_hour": random.randint(base_login, base_login + 2),
        "files_accessed": random.randint(10, 20),
        "file_sensitivity": "low",
        "location": "Kerala",
        "device": "laptop",
        "failed_logins": random.randint(0, 1),
        "session_duration": random.randint(30, 60)
    }


def night_behavior(user, date):
    return {
        "user_id": user["id"],
        "timestamp": date,
        "login_hour": random.randint(1, 3),
        "files_accessed": random.randint(10, 20),
        "file_sensitivity": "low",
        "location": "Kerala",
        "device": "laptop",
        "failed_logins": random.randint(0, 1),
        "session_duration": random.randint(30, 60)
    }


def insider_behavior(user, day, date):

    if day <= 5:
        login_hour = random.randint(8, 10)
        files = random.randint(10, 20)
        sensitivity = "low"
        location = "Kerala"
        failed = 0

    elif day <= 10:
        login_hour = random.randint(8, 11)
        files = random.randint(30, 50)
        sensitivity = random.choice(["low", "medium"])
        location = "Kerala"
        failed = random.randint(1, 2)

    elif day <= 15:
        login_hour = random.choice([2, 3, 4])
        files = random.randint(80, 120)
        sensitivity = random.choice(["medium", "high"])
        location = random.choice(["Kerala", "Unknown"])
        failed = random.randint(2, 4)

    else:
        login_hour = random.choice([1, 2, 3])
        files = random.randint(200, 400)
        sensitivity = "high"
        location = "Unknown"
        failed = random.randint(5, 8)

    return {
        "user_id": user["id"],
        "timestamp": date,
        "login_hour": login_hour,
        "files_accessed": files,
        "file_sensitivity": sensitivity,
        "location": location,
        "device": random.choice(["laptop", "desktop"]),
        "failed_logins": failed,
        "session_duration": random.randint(40, 150)
    }


def generate_user_activity(user, day, date):
    if user["type"] == "normal":
        return normal_behavior(user, date)
    elif user["type"] == "night":
        return night_behavior(user, date)
    else:
        return insider_behavior(user, day, date)


def generate_dataset():
    data = []

    for day in range(days):
        current_date = start_date + timedelta(days=day)

        for user in users:
            sessions = random.randint(2, 5)  # multiple sessions per day

            for _ in range(sessions):
                record = generate_user_activity(user, day, current_date)
                data.append(record)

    return pd.DataFrame(data)



if __name__ == "__main__":
    df = generate_dataset()
    df.to_csv("data/logs.csv", index=False)

    print("Dataset generated successfully!")
    print("Total records:", len(df))