import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from collector import get_system_telemetry
from engine import calculate_waste_score
from actions import kill_process, automated_cleanup

st.set_page_config(
    page_title="DaemonGuard",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ DaemonGuard - Linux Resource Optimization Dashboard")
st.caption("Advanced Linux Process Telemetry, Waste Scoring & Safe Optimization")

# --- DATA FETCH & ENGINE (FIRST) ---
df_raw = get_system_telemetry()
df = calculate_waste_score(df_raw)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Control Panel")

# Auto-Refresh Logic
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh (5s)", value=True)
if auto_refresh:
    st_autorefresh(interval=5000, key="daemonguard_refresher")

if st.sidebar.button("🔄 Refresh Data Now"):
    st.rerun()

# Process Termination Tool
st.sidebar.markdown("---")
st.sidebar.subheader("🚫 Terminate Process")
target_pid = st.sidebar.number_input("Enter PID to Kill", min_value=1, step=1, value=1000)

confirm_kill = st.sidebar.checkbox("I confirm I want to terminate this PID")

if st.sidebar.button("⚠️ Terminate Selected PID"):
    if not confirm_kill:
        st.sidebar.warning("Please check the confirmation box before terminating!")
    else:
        success, msg = kill_process(int(target_pid))
        if success:
            st.sidebar.success(msg)
            st.rerun()
        else:
            st.sidebar.error(msg)

# --- AUTOMATED CLEANUP POLICY ---
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Automated Cleanup Policy")
auto_threshold = st.sidebar.slider("Waste Score Threshold", min_value=200, max_value=800, value=400, step=50)

auto_confirm = st.sidebar.checkbox("Confirm Auto-Cleanup Execution")

if st.sidebar.button("⚡ Run Automated Cleanup"):
    if not auto_confirm:
        st.sidebar.warning("Please check the auto-cleanup confirmation box!")
    else:
        cleanup_logs = automated_cleanup(df, threshold=auto_threshold)
        st.sidebar.success(f"Cleanup executed! Processed {len(cleanup_logs)} target(s).")
        for log in cleanup_logs:
            st.sidebar.info(log)
        st.rerun()

# --- HIGH WASTE ALERT BANNER ---
high_waste_df = df[df['waste_score'] > 200]
if not high_waste_df.empty:
    st.error(f"⚠️ **Resource Alert:** Detected {len(high_waste_df)} process(es) with critical waste score (> 200)!")

# Search & Filter Controls
st.markdown("---")
col_search, col_filter, col_risk = st.columns([2, 1, 1])
with col_search:
    search_query = st.text_input("🔍 Search Process Name or PID", "")
with col_filter:
    show_safe = st.checkbox("Show Safe System Processes", value=True)
with col_risk:
    risk_filter = st.selectbox("Filter Risk Level", ["All", "🔥 Critical", "⚠️ High", "⚡ Medium", "✅ Low"])

# Apply Filters
df_filtered = df.copy()
if not show_safe:
    df_filtered = df_filtered[df_filtered['is_safe'] == False]

if risk_filter != "All":
    df_filtered = df_filtered[df_filtered['risk_level'] == risk_filter]

if search_query:
    df_filtered = df_filtered[
        df_filtered['name'].str.contains(search_query, case=False, na=False) |
        df_filtered['pid'].astype(str).contains(search_query)
    ]

# --- METRICS SECTION ---
st.subheader("📊 System Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Active Processes", len(df))
m2.metric("Total RAM Usage", f"{df['ram_mb'].sum():.1f} MB")
m3.metric("Avg CPU Usage", f"{df['cpu_percent'].mean():.1f} %")
m4.metric("High Waste Candidates", len(high_waste_df))

# --- VISUAL ANALYTICS ---
st.markdown("---")
st.subheader("📈 Visual Resource Distribution")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write("**Top 5 RAM Consuming Processes**")
    top_ram = df_filtered.sort_values(by='ram_mb', ascending=False).head(5)
    st.bar_chart(top_ram.set_index('name')['ram_mb'])

with chart_col2:
    st.write("**Top 5 Waste Score Candidates**")
    top_waste = df_filtered.sort_values(by='waste_score', ascending=False).head(5)
    st.bar_chart(top_waste.set_index('name')['waste_score'])

# --- TELEMETRY DATA TABLE ---
st.markdown("---")
st.subheader("📋 Live Process Telemetry Data")

display_cols = ['pid', 'name', 'cpu_percent', 'ram_mb', 'waste_score', 'risk_level', 'is_safe']
existing_cols = [c for c in display_cols if c in df_filtered.columns]

st.dataframe(
    df_filtered[existing_cols].sort_values(by='waste_score', ascending=False),
    use_container_width=True
)

# Export Data Button
csv_data = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Export Filtered Report as CSV",
    data=csv_data,
    file_name="daemonguard_telemetry.csv",
    mime="text/csv"
)