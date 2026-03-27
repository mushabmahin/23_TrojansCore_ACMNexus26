import pandas as pd
import numpy as np

from sklearn.ensemble import IsolationForest


# -----------------------------
# 1. LOAD DATA
# -----------------------------
def load_data(path="data/logs.csv"):
    df = pd.read_csv(path)
    df = df.dropna()
    return df


# -----------------------------
# 2. PREPROCESSING
# -----------------------------
def preprocess(df):
    # Convert categorical features
    df["location"] = df["location"].astype("category").cat.codes
    df["device"] = df["device"].astype("category").cat.codes
    df["file_sensitivity"] = df["file_sensitivity"].map({
        "low": 1,
        "medium": 2,
        "high": 3
    })

    return df


# -----------------------------
# 3. ANOMALY DETECTION
# -----------------------------
def run_model(df):
    features = [
        "login_hour",
        "files_accessed",
        "file_sensitivity",
        "location",
        "device",
        "failed_logins",
        "session_duration"
    ]

    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(df[features])

    df["anomaly_score"] = model.decision_function(df[features])
    df["anomaly"] = model.predict(df[features])  # -1 = anomaly

    return df


# -----------------------------
# 4. FEATURE FLAGS
# -----------------------------
def add_feature_flags(df):
    # Per-user baseline
    df["avg_files"] = df.groupby("user_id")["files_accessed"].transform("mean")

    df["file_spike"] = df["files_accessed"] > df["avg_files"] * 3

    df["odd_login"] = (df["login_hour"] < 6) | (df["login_hour"] > 22)

    df["location_change"] = df["location"] != df.groupby("user_id")["location"].transform("first")

    df["high_failed_logins"] = df["failed_logins"] > 3

    return df


# -----------------------------
# 5. RISK SCORING
# -----------------------------
def compute_risk_score(row):
    score = 0

    if row["anomaly"] == -1:
        score += 40

    if row["file_spike"]:
        score += 20

    if row["location_change"]:
        score += 20

    if row["high_failed_logins"]:
        score += 10

    if row["odd_login"]:
        score += 10

    return min(score, 100)


def apply_risk(df):
    df["risk_score"] = df.apply(compute_risk_score, axis=1)
    return df


# -----------------------------
# 6. ALERT LEVEL
# -----------------------------
def get_alert(score):
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    return "LOW"


def apply_alerts(df):
    df["alert"] = df["risk_score"].apply(get_alert)
    return df


# -----------------------------
# 7. EXPLANATIONS
# -----------------------------
def generate_explanations(row):
    reasons = []

    if row["anomaly"] == -1:
        reasons.append("Unusual overall behavior")

    if row["file_spike"]:
        reasons.append("Spike in file access")

    if row["location_change"]:
        reasons.append("Access from new location")

    if row["high_failed_logins"]:
        reasons.append("Multiple failed logins")

    if row["odd_login"]:
        reasons.append("Unusual login time")

    return reasons


def apply_explanations(df):
    df["reasons"] = df.apply(generate_explanations, axis=1)
    return df


# -----------------------------
# 8. FINAL PIPELINE
# -----------------------------
def run_pipeline():
    df = load_data()
    df = preprocess(df)
    df = run_model(df)
    df = add_feature_flags(df)
    df = apply_risk(df)
    df = apply_alerts(df)
    df = apply_explanations(df)

    return df


# -----------------------------
# 9. EXPORT FOR UI
# -----------------------------
def get_output():
    df = run_pipeline()

    output = df[[
        "user_id",
        "timestamp",
        "risk_score",
        "alert",
        "reasons"
    ]].to_dict(orient="records")

    return output