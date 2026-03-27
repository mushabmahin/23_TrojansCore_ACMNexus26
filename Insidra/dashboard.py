import streamlit as st
import pandas as pd
import plotly.express as px
import time

from stream_generator import generate_log

from model.preprocess import preprocess_data
from model.anomaly_model import train_model, predict
from model.risk_engine import *

st.set_page_config(layout="wide", page_title="Live Threat Monitor")

st.title("🛡️ Real-Time Insider Threat Detection System")

start = st.sidebar.button("▶ Start Monitoring")

st.sidebar.info("Simulating real-time log ingestion with adaptive behavior")

if start:

    logs = []
    placeholder = st.empty()

    st.success("🟢 Monitoring Active")

    # -------------------------
    # INITIAL TRAINING BUFFER
    # -------------------------
    for i in range(20):
        logs.append(generate_log(step=i))

    df_init = pd.DataFrame(logs)
    X_scaled, df_init = preprocess_data(df_init)
    model = train_model(X_scaled)

    # -------------------------
    # STREAM LOOP (5 EVENTS)
    # -------------------------
    for i in range(200):

        batch_size = 5

        new_batch = []
        for _ in range(batch_size):
            new_batch.append(generate_log(step=i))

        logs.extend(new_batch)

        df = pd.DataFrame(logs)

        # -------------------------
        # PIPELINE
        # -------------------------
        X_scaled, df = preprocess_data(df)

        scores, labels = predict(model, X_scaled)

        df["anomaly_score"] = scores
        df["anomaly"] = labels

        baseline = compute_baseline(df)
        df = merge_baseline(df, baseline)

        df = compute_drift(df)
        df = add_flags(df)

        df = compute_risk(df)
        df = assign_alert(df)

        df["reasons"] = df.apply(generate_reason, axis=1)

        # -------------------------
        # SUSPICIOUS LOGS
        # -------------------------
        suspicious_df = df[df["risk_score"] >= 40]

        # -------------------------
        # LIVE UI
        # -------------------------
        with placeholder.container():

            st.subheader("📊 System Metrics")

            col1, col2, col3 = st.columns(3)

            latest = df.iloc[-1]

            col1.metric("Events Processed", len(df))
            col2.metric("Latest Risk Score", latest["risk_score"])
            col3.metric("Current User", latest["emp_id"])

            # ALERT SYSTEM
            if latest["risk_score"] >= 80:
                st.error("🚨 LIVE THREAT DETECTED")
            elif latest["risk_score"] >= 40:
                st.warning("⚠️ Suspicious Behavior")

            # -------------------------
            # RISK GRAPH
            # -------------------------
            st.markdown("### 📈 Risk Evolution")

            fig = px.line(
                df,
                x="timestamp",
                y="risk_score",
                color="emp_id",
                markers=True
            )

            st.plotly_chart(fig, use_container_width=True)

            # -------------------------
            # DRIFT GRAPH
            # -------------------------
            if "file_drift" in df.columns:
                st.markdown("### 📊 Behavioral Drift")

                drift_fig = px.line(
                    df,
                    x="timestamp",
                    y="file_drift",
                    color="emp_id"
                )

                st.plotly_chart(drift_fig, use_container_width=True)

            # -------------------------
            # SUSPICIOUS LOG TABLE
            # -------------------------
            st.markdown("### 🚨 Suspicious Activity Logs")

            if not suspicious_df.empty:
                display_df = suspicious_df.tail(10)[
                    ["timestamp", "emp_id", "risk_score", "alert", "reasons"]
                ]

                display_df["reasons"] = display_df["reasons"].apply(
                    lambda x: ", ".join(x) if isinstance(x, list) else x
                )

                st.dataframe(display_df, use_container_width=True)
            else:
                st.success("No suspicious activity detected")

        time.sleep(0.8)

    # -------------------------
    # FINAL REPORT
    # -------------------------
    st.markdown("## 📄 Simulation Summary Report")

    total_events = len(df)
    high_risk = len(df[df["risk_score"] >= 70])
    medium_risk = len(df[(df["risk_score"] >= 40) & (df["risk_score"] < 70)])
    low_risk = len(df[df["risk_score"] < 40])

    top_user = df.groupby("emp_id")["risk_score"].max().idxmax()
    max_risk = df["risk_score"].max()

    st.write(f"Total Events Processed: {total_events}")
    st.write(f"High Risk Events: {high_risk}")
    st.write(f"Medium Risk Events: {medium_risk}")
    st.write(f"Low Risk Events: {low_risk}")
    st.write(f"Most Suspicious User: {top_user}")
    st.write(f"Maximum Risk Score Observed: {max_risk}")

    # -------------------------
    # ATTACK STORY
    # -------------------------
    st.markdown("### 🧠 Attack Analysis")

    st.write("""
    Phase 1: Normal behavior  
    Phase 2: Gradual increase in file access  
    Phase 3: Abnormal login patterns  
    Phase 4: Insider threat escalation detected  
    """)