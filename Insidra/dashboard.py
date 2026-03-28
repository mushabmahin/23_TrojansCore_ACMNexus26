import streamlit as st
import pandas as pd
import plotly.express as px
import time

from stream_generator import generate_log

from model.preprocess import preprocess_data
from model.anomaly_model import train_model, predict
from model.risk_engine import *
from mailer import send_soc_email
from remediation import suspend_account, force_mfa, get_remediation_summary_df, get_applied_actions, load_history, unsuspend_account

st.set_page_config(layout="wide", page_title="Live Threat Monitor")

st.title("🛡️ Real-Time Insider Threat Detection System")

start = st.sidebar.button("▶ Start Monitoring")
fast_forward = st.sidebar.button("⏩ Fast Forward")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Demo Environment"):
    import os
    # Clear the persistent JSON database
    if os.path.exists("remediation_history.json"):
        with open("remediation_history.json", "w") as f:
            f.write("[]")
    
    # Clear active session state
    if "final_df" in st.session_state:
        del st.session_state["final_df"]
    st.session_state.whitelist = []
    st.sidebar.success("✅ Database Wiped. Ready for Judges!")
    time.sleep(1)
    st.rerun()
st.sidebar.markdown("---")

st.sidebar.info("Simulating real-time log ingestion with adaptive behavior")

if "whitelist" not in st.session_state:
    st.session_state.whitelist = []

with st.sidebar.expander("🛡️ Exception Manager", expanded=False):
    st.write("Authorize contextual overrides to prevent anomalies.")
    all_users = [f"U{i}" for i in range(1, 11)]
    st.session_state.whitelist = st.multiselect(
        "Whitelisted Employees", 
        options=all_users, 
        default=st.session_state.whitelist,
        key="whitelist_select"
    )

if start or fast_forward:

    # Load persistent dataset instead of generating logs
    df_raw = pd.read_csv("data/logs.csv")
    # In case data doesn't have lat/lon, attempt to add dummy ones to satisfy map (optional)
    if "lat" not in df_raw.columns:
        import numpy as np
        df_raw["lat"] = np.where(df_raw["location"].str.contains("Kerala", na=False), 10.8505, 45.0)
        df_raw["lon"] = np.where(df_raw["location"].str.contains("Kerala", na=False), 76.2711, 10.0)
        
    raw_dicts = df_raw.to_dict('records')
    
    logs = []
    placeholder = st.empty()

    if fast_forward:
        st.success("⏩ Fast Forwarding Data Processing...")
    else:
        st.success("🟢 Monitoring Active")

    # -------------------------
    # INITIAL TRAINING BUFFER
    # -------------------------
    # Preload Remediation states (Mock Database)
    history_records = load_history()
    suspended_users = {r["user_id"] for r in history_records if r["action"] == "Suspend Account"}
    mfa_forced_users = {r["user_id"] for r in history_records if r["action"] == "Force MFA"}

    for i in range(20):
        if i < len(raw_dicts):
            # Do not inject suspended users even during init
            if raw_dicts[i]["emp_id"] not in suspended_users:
                logs.append(raw_dicts[i])

    df_init = pd.DataFrame(logs)
    X_scaled, df_init = preprocess_data(df_init)
    model = train_model(X_scaled)

    # -------------------------
    # STREAM LOOP (5 EVENTS)
    # -------------------------
    batch_size = 5
    max_iters = min(200, (len(raw_dicts) - 20) // batch_size)
    
    for i in range(max_iters):
        new_batch = []
        for j in range(batch_size):
            idx = 20 + i*batch_size + j
            if idx < len(raw_dicts):
                log = raw_dicts[idx]
                
                # ENFORCE DATABASE MOCKING
                if log["emp_id"] in suspended_users:
                    # Physically simulate Network Block - skip entirely
                    continue
                if log["emp_id"] in mfa_forced_users:
                    # Physically simulate MFA challenge success reducing their suspicion
                    log["failed_logins"] = 0
                    if log["session_duration"] > 60:
                        log["session_duration"] = 15
                
                new_batch.append(log)

        # Skip batch extension & processing if all logs were blocked
        if not new_batch:
            continue
            
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
        # APPLY AUTHORIZED EXCEPTION
        # -------------------------
        if len(st.session_state.whitelist) > 0:
            mask = df["emp_id"].isin(st.session_state.whitelist)
            df.loc[mask, "risk_score"] = 0
            df.loc[mask, "alert"] = "LOW"
            # Setting reasons directly to authorized override flag
            for idx in df[mask].index:
                df.at[idx, "reasons"] = ["✅ Authorized Exception (Manager)"]

        # -------------------------
        # SUSPICIOUS LOGS
        # -------------------------
        suspicious_df = df[df["risk_score"] >= 40]

        if fast_forward and i < max_iters - 1:
            continue

        # -------------------------
        # LIVE UI
        # -------------------------
        with placeholder.container():

            st.subheader("System Metrics")

            col1, col2, col3 = st.columns(3)

            latest = df.iloc[-1]

            col1.metric("Events Processed", len(df))
            col2.metric("Latest Risk Score", latest["risk_score"])
            col3.metric("Current User", latest["emp_id"])

            # ALERT SYSTEM
            if latest["risk_score"] >= 80:
                st.error("LIVE THREAT DETECTED")
            elif latest["risk_score"] >= 40:
                st.warning("Suspicious Behavior")

            # -------------------------
            # RISK GRAPH
            # -------------------------
            st.markdown("### Risk Evolution")

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
                st.markdown("### Behavioral Drift")

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
            st.markdown("### Suspicious Activity Logs")

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

        if not fast_forward:
            time.sleep(0.8)

    # Store Final DataFrame in Session State to prevent reset on button UI interactions
    st.session_state.final_df = df

if "final_df" in st.session_state:
    df = st.session_state.final_df

    # -------------------------
    # FINAL REPORT
    # -------------------------
    st.markdown("## Simulation Summary Report")

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
    # REMEDIATION ACTIONS
    # -------------------------
    st.markdown("## Automated Remediation Actions")
    st.write("Take immediate action on users exhibiting highly critical behavior.")
    
    critical_users = df[df["risk_score"] >= 70]["emp_id"].unique()
    
    if len(critical_users) > 0:
        for u in critical_users:
            with st.expander(f"Action Panel: {u} (CRITICAL RISK)", expanded=True):
                st.warning(f"User {u} has exceeded risk thresholds. Select an automated response:")
                
                # Fetch dynamically what actions were already applied
                applied = get_applied_actions(u)
                
                col1, col2, col3 = st.columns(3)
                
                if col1.button(f"Suspend Account", key=f"susp_{u}", disabled="Suspend Account" in applied):
                    if suspend_account(u):
                        st.success(f"✅ Active Directory: User '{u}' has been suspended. Future logs will be network blocked.")
                        time.sleep(0.5)
                        st.rerun()
                if col2.button(f"Force MFA", key=f"mfa_{u}", disabled="Force MFA" in applied):
                    if force_mfa(u):
                        st.success(f"📱 Okta: Forced Re-Authentication for '{u}'.")
                        time.sleep(0.5)
                        st.rerun()
                if col3.button(f"Notify SOC", key=f"soc_{u}"):
                    # Get the most recent logs for this user to extract the reasons and specific risk score
                    user_history = df[df["emp_id"] == u]
                    latest_state = user_history.iloc[-1]
                    
                    success, msg_response = send_soc_email(
                        user_id=u,
                        risk_score=latest_state["risk_score"],
                        reasons=latest_state["reasons"]
                    )
                    
                    if success:
                        st.success(f" {msg_response}")
                    else:
                        st.error(f" {msg_response}")
    else:
        st.success("No critical users require immediate remediation.")

    # -------------------------
    # RESTORE USERS
    # -------------------------
    ui_history = load_history()
    currently_suspended = sorted({r["user_id"] for r in ui_history if r["action"] == "Suspend Account"})
    
    if currently_suspended:
        st.markdown("### 🔓 Restore Network Access")
        st.write("Click below to unsuspend employees and allow their future logs back into the pipeline.")
        cols = st.columns(max(len(currently_suspended), 1))
        for idx, s_u in enumerate(currently_suspended):
            if cols[idx].button(f"Unsuspend {s_u}", key=f"unsusp_btn_{s_u}"):
                if unsuspend_account(s_u):
                    st.success(f"Restored network access for {s_u}")
                    time.sleep(0.5)
                    st.rerun()

    # -------------------------
    # AUDIT LOG
    # -------------------------
    st.markdown("### Live Remediation Audit Log")
    audit_df = get_remediation_summary_df()
    if not audit_df.empty:
        st.dataframe(audit_df, use_container_width=True)
    else:
        st.info("No automations have been triggered yet.")

    # -------------------------
    # ATTACK STORY
    # -------------------------
    st.markdown("###Attack Analysis")

    st.write("""
    Phase 1: Normal behavior  
    Phase 2: Gradual increase in file access  
    Phase 3: Abnormal login patterns  
    Phase 4: Insider threat escalation detected  
    """)