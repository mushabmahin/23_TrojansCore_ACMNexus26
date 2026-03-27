import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess
import ast
import time

st.set_page_config(
    layout="wide",
    page_title="Insidra Dashboard",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# -------------------------
# STYLING
# -------------------------
st.markdown("""
<style>
.stApp {
    background-color: #0f1115;
    color: #e0e0e0;
}
.metric-card {
    background-color: #1e2128;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #00f2fe;
}
.metric-card.high-alert {
    border-left: 5px solid #ff4b4b;
}
.metric-card.medium-alert {
    border-left: 5px solid #faca2b;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/scored_logs.csv")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["reasons"] = df["reasons"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith("[") else x
        )
        return df
    except:
        return pd.DataFrame()

df = load_data()

# -------------------------
# SIDEBAR CONTROLS
# -------------------------
st.sidebar.title("🛡️ Insidra Controls")

mode = st.sidebar.selectbox(
    "Scenario Mode",
    ["Normal Monitoring", "Insider Attack Simulation"]
)

if df.empty:
    st.warning("No data found. Run pipeline first.")
    if st.sidebar.button("Run Pipeline"):
        subprocess.run(["python", "data_gen.py"])
        subprocess.run(["python", "app.py"])
        st.rerun()
    st.stop()

# Sort users by risk (SMART)
user_list = df.groupby("emp_id")["risk_score"].max() \
              .sort_values(ascending=False) \
              .index.tolist()

selected_user = st.sidebar.selectbox("Employee ID", user_list)

if st.sidebar.button("🔄 Regenerate Data"):
    subprocess.run(["python", "data_gen.py"])
    subprocess.run(["python", "app.py"])
    st.cache_data.clear()
    st.rerun()

# -------------------------
# USER DATA
# -------------------------
full_user_data = df[df["emp_id"] == selected_user].sort_values("timestamp")

# Simulated real-time behavior
if mode == "Insider Attack Simulation":
    step = st.sidebar.slider("Simulation Step", 5, len(full_user_data), 10)
    user_data = full_user_data.iloc[:step]
else:
    user_data = full_user_data

# -------------------------
# METRICS
# -------------------------
max_risk = user_data["risk_score"].max()
current_alert = user_data.iloc[-1]["alert"]

st.title(f"🛡️ User Analysis: `{selected_user}`")

col1, col2, col3 = st.columns(3)

alert_class = "high-alert" if max_risk >= 70 else ("medium-alert" if max_risk >= 40 else "")

with col1:
    st.markdown(f'<div class="metric-card {alert_class}"><h4>Max Risk</h4><h2>{max_risk}</h2></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="metric-card {alert_class}"><h4>Status</h4><h2>{current_alert}</h2></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="metric-card"><h4>Events</h4><h2>{len(user_data)}</h2></div>', unsafe_allow_html=True)

# -------------------------
# ALERT SYSTEM
# -------------------------
if max_risk >= 70:
    st.error("🚨 HIGH RISK USER DETECTED!")
elif max_risk >= 40:
    st.warning("⚠️ Suspicious behavior detected")

# -------------------------
# RISK GRAPH
# -------------------------
st.markdown("### 📈 Risk Evolution")

fig = px.line(
    user_data,
    x="timestamp",
    y="risk_score",
    markers=True,
    line_shape="spline"
)

fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1)
fig.add_hrect(y0=40, y1=70, fillcolor="yellow", opacity=0.1)

fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e0e0e0')
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# DRIFT GRAPH (YOUR USP)
# -------------------------
if "file_drift" in user_data.columns:
    st.markdown("### 📊 Behavioral Drift")

    drift_fig = px.line(
        user_data,
        x="timestamp",
        y="file_drift",
        markers=True
    )

    drift_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0')
    )

    st.plotly_chart(drift_fig, use_container_width=True)

# -------------------------
# SUSPICIOUS LOGS
# -------------------------
st.markdown("### 🚨 Suspicious Activity Log")

suspicious = user_data[user_data["risk_score"] >= 40][[
    "timestamp", "risk_score", "alert", "reasons"
]].sort_values("timestamp", ascending=False)

suspicious["reasons"] = suspicious["reasons"].apply(
    lambda x: ", ".join(x) if isinstance(x, list) else x
)

if suspicious.empty:
    st.success("No suspicious activity detected.")
else:
    st.dataframe(suspicious, use_container_width=True)