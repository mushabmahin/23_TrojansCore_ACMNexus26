import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import subprocess
import ast

st.set_page_config(layout="wide", page_title="Insidra Dashboard", page_icon="🛡️", initial_sidebar_state="expanded")

# Custom CSS for premium feel
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-card.high-alert {
        border-left: 5px solid #ff4b4b;
    }
    .metric-card.medium-alert {
        border-left: 5px solid #faca2b;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Insidra/data/scored_logs.csv")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Handle parsed lists from CSV safely
        df['reasons'] = df['reasons'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

st.sidebar.title("🛡️ Insidra Controls")

if df.empty:
    st.warning("No data found. Please run the pipeline first.")
    if st.sidebar.button("Run Full Pipeline"):
        with st.spinner("Generating Data & Scoring..."):
            subprocess.run(["python", "data_gen.py"], cwd="Insidra")
            subprocess.run(["python", "app.py"], cwd="Insidra")
            st.rerun()
    st.stop()

# Auto-identify the riskiest users
user_risk = df.groupby('emp_id')['risk_score'].max().sort_values(ascending=False)
highest_risk_users = user_risk[user_risk >= 70].index.tolist()

st.sidebar.markdown("### Select User for Analysis")

# Format dropdown to flag high risk users
user_list = df['emp_id'].unique()
# Sort so high risk are at the top
user_list = sorted(user_list, key=lambda x: 0 if x in highest_risk_users else 1)

selected_user = st.sidebar.selectbox(
    "Employee ID", 
    user_list,
    format_func=lambda x: f"🔴 {x} (HIGH RISK)" if x in highest_risk_users else f"🟢 {x}"
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Rerun Data Pipeline"):
    with st.spinner("Regenerating & Re-scoring..."):
        subprocess.run(["python", "data_gen.py"], cwd="Insidra")
        subprocess.run(["python", "app.py"], cwd="Insidra")
        st.cache_data.clear()
        st.rerun()

user_data = df[df['emp_id'] == selected_user].sort_values('timestamp')

max_risk = user_data['risk_score'].max()
final_alert = user_data.iloc[-1]['alert'] if not user_data.empty else 'LOW'

st.title(f"User Analysis: `{selected_user}`")

# Metrics
col1, col2, col3 = st.columns(3)
alert_color_class = "high-alert" if max_risk >= 70 else ("medium-alert" if max_risk >= 40 else "")
with col1:
    st.markdown(f'<div class="metric-card {alert_color_class}"><h4>Max Risk Score</h4><h2>{max_risk}</h2></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card {alert_color_class}"><h4>Current Status</h4><h2>{final_alert}</h2></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><h4>Events Tracked</h4><h2>{len(user_data)}</h2></div>', unsafe_allow_html=True)

st.markdown("---")
st.subheader("📈 Behavioral Drift & Risk History")

# Plotly Line Chart
fig = px.line(user_data, x='timestamp', y='risk_score', 
              markers=True, line_shape='spline',
              color_discrete_sequence=['#00f2fe'])

fig.add_hrect(y0=70, y1=100, line_width=0, fillcolor="red", opacity=0.1, annotation_text="HIGH RISK ZONE", annotation_position="top left")
fig.add_hrect(y0=40, y1=70, line_width=0, fillcolor="yellow", opacity=0.1, annotation_text="MEDIUM RISK ZONE", annotation_position="top left")

fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e0e0e0'),
    yaxis_title="Risk Score",
    xaxis_title="Time",
    yaxis_range=[-5, 105],
    height=400,
    margin=dict(l=0, r=0, t=30, b=0)
)
fig.update_traces(line=dict(width=3), marker=dict(size=8, color='#ff4b4b', line=dict(width=2, color='white')))

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("🚨 Anomalous Behavior Logs")

suspicious_events = user_data[user_data['risk_score'] >= 40][['timestamp', 'risk_score', 'alert', 'reasons']].sort_values('timestamp', ascending=False)
# format reasons list nicely as string mapping
suspicious_events['reasons'] = suspicious_events['reasons'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

if suspicious_events.empty:
    st.success("No suspicious behavior detected for this user.")
else:
    # Basic color mapping using Streamlit dataframe features 
    st.dataframe(
        suspicious_events,
        use_container_width=True,
        hide_index=True
    )
