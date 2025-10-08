import streamlit as st
import pandas as pd
from collectors import get_system_usage, get_high_resource_processes
import time
from collections import deque

st.set_page_config(page_title="System Monitor Dashboard", layout="wide", page_icon="💻")
st.title("🖥 Real-Time System Monitor with Colored Inline Trends")
st.markdown("Monitor CPU, Memory, Disk usage and top resource-consuming processes with color-coded inline trends.")

refresh_rate = 2
history_length = 10
placeholder = st.empty()
proc_history = {}

# Sparkline function with colored bars
def colored_sparkline(values):
    if not values:
        return ""
    min_val, max_val = min(values), max(values)
    bars = "▁▂▃▄▅▆▇█"
    colors = []
    result = ""
    for v in values:
        if max_val - min_val == 0:
            idx = 0
        else:
            idx = int((v - min_val) / (max_val - min_val) * (len(bars)-1))
        result += bars[idx]
        perc = (v - min_val) / (max_val - min_val + 0.0001)
        if perc > 0.7:
            colors.append("red")
        elif perc > 0.4:
            colors.append("orange")
        else:
            colors.append("green")
    html = "".join([f"<span style='color:{c}'>{b}</span>" for b, c in zip(result, colors)])
    return html

while True:
    with placeholder.container():
        cpu, mem_percent, disk_percent = get_system_usage()

        # ------------------ Metric Cards ------------------
        st.subheader("System Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("CPU Usage (%)", f"{cpu:.1f}", delta_color="inverse")
        col2.metric("Memory Usage (%)", f"{mem_percent:.1f}", delta_color="inverse")
        col3.metric("Disk Usage (%)", f"{disk_percent:.1f}", delta_color="inverse")

        # ------------------ High Resource Processes ------------------
        st.subheader("High Resource Processes")
        processes = get_high_resource_processes()
        parsed = []

        for p in processes:
            parts = p.split()
            pid = parts[0]
            cpu_proc = float(parts[-2])
            mem_proc = float(parts[-1])
            name = " ".join(parts[1:-2])
            parsed.append([pid, name, cpu_proc, mem_proc])

            if pid not in proc_history:
                proc_history[pid] = {"cpu": deque(maxlen=history_length), "mem": deque(maxlen=history_length)}
            proc_history[pid]["cpu"].append(cpu_proc)
            proc_history[pid]["mem"].append(mem_proc)

        if parsed:
            df = pd.DataFrame(parsed, columns=["PID", "Name", "CPU%", "Memory(MB)"])

            # Highlight high CPU/Memory automatically
            def color_row(row):
                if row['CPU%'] > 70 or row['Memory(MB)'] > 150:
                    return ['background-color: #FFCCCC']*4
                elif row['CPU%'] > 40 or row['Memory(MB)'] > 80:
                    return ['background-color: #FFE5CC']*4
                else:
                    return ['']*4

            st.dataframe(df.style.apply(color_row, axis=1))

            st.markdown("**Processes Inline CPU & Memory Trends**")
            for idx, row in df.iterrows():
                cpu_html = colored_sparkline(proc_history[row['PID']]["cpu"])
                mem_html = colored_sparkline(proc_history[row['PID']]["mem"])
                st.markdown(
                    f"**{row['Name']} (PID: {row['PID']})** | CPU: {cpu_html} | MEM: {mem_html}",
                    unsafe_allow_html=True
                )
        else:
            st.text("No high resource processes detected.")

        st.markdown("---")
        st.caption("Dashboard updates every 2 seconds. Developed with ❤️ using Streamlit.")

    time.sleep(refresh_rate)
