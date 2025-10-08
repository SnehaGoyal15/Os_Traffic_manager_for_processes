import streamlit as st
import pandas as pd
from collectors import get_system_usage, get_high_resource_processes

st.set_page_config(page_title="System Monitor Dashboard", layout="wide")

st.title("🖥 System Resource Dashboard")

# ---------------- System Metrics ----------------
cpu, mem_percent, disk_percent = get_system_usage()

st.subheader("System Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("CPU Usage (%)", f"{cpu:.1f}")
col2.metric("Memory Usage (%)", f"{mem_percent:.1f}")
col3.metric("Disk Usage (%)", f"{disk_percent:.1f}")

# ---------------- Resource Bars ----------------
st.subheader("Resource Usage Bars")
st.progress(int(cpu))
st.progress(int(mem_percent))
st.progress(int(disk_percent))

# ---------------- High Resource Processes ----------------
st.subheader("High Resource Processes")
processes = get_high_resource_processes()

if processes:
    parsed = []
    for p in processes:
        parts = p.split()
        pid = parts[0]
        cpu_proc = parts[-2]
        mem_proc = parts[-1]
        name = " ".join(parts[1:-2])
        parsed.append([pid, name, cpu_proc, mem_proc])
    
    proc_df = pd.DataFrame(parsed, columns=["PID", "Name", "CPU%", "Memory(MB)"])
    st.dataframe(proc_df)
else:
    st.text("No high resource processes detected.")

# ---------------- Footer ----------------
st.write("Dashboard updates every time you refresh the page.")
