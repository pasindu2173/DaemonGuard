import streamlit as st
import pandas as pd
from collector import get_system_telemetry
from engine import calculate_waste_score
from actions import kill_process

st.set_page_config(page_title="DaemonGuard", layout="wide")

st.title("🛡️ DaemonGuard - Linux Resource Optimization Dashboard")
st.caption("Advanced Linux Process Telemetry, Waste Scoring & Safe Optimization")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Control Panel")

# Auto-Refresh Toggle
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh (5s)", value=False)
if auto_refresh:
    st.empty()
    st.text("Auto-refresh active...")

if st.sidebar.button("🔄 Refresh Data Now"):
    st.rerun()

# Process Termination Tool
st.sidebar.markdown("---")
st.sidebar.subheader("🚫 Terminate Process")
target_pid = st.sidebar.number_input("Enter PID to Kill", min_value=1, step=1, value=1000)

if st.sidebar.button("⚠️ Terminate Selected PID"):
    if target_pid:
        success, msg = kill_process(int(target_pid))
        if success:
            st.sidebar.success(msg)
            st.rerun()
        else:
            st.sidebar.error(msg)

# --- DATA FETCH & ENGINE ---
df_raw = get_system_telemetry()
df = calculate_waste_score(df_raw)

# Search & Filter Controls
st.markdown("---")
col_search, col_filter = st.columns([3, 1])
with col_search:
    search_query = st.text_input("🔍 Search Process Name or PID", "")
with col_filter:
    show_safe = st.checkbox("Show Safe System Processes", value=True)

# Apply Filters
df_filtered = df.copy()
if not show_safe:
    df_filtered = df_filtered[df_filtered['is_safe'] == False]

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
m4.metric("High Waste Candidates", len(df[df['waste_score'] > 200]))

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
st.dataframe(df_filtered.sort_values(by='waste_score', ascending=False), use_container_width=True)

# Export Data Button
csv_data = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Export Filtered Report as CSV",
    data=csv_data,
    file_name="daemonguard_telemetry.csv",
    mime="text/csv"
)