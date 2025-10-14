# dashboard_final.py 
import streamlit as st
import pandas as pd
from collections import deque
import time
from datetime import datetime
import threading
import warnings

# Suppress Streamlit thread warnings
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

from collectors import get_system_usage, get_high_resource_processes
from analyzer import get_comprehensive_alerts, check_system_metrics, correlation_checks
from automation import auto_kill_processes, get_processes_for_review
from logger import log_alert, DB_FILE
from network_scanner import scan_ports_range, scan_ports_list
from config import get_config, update_config
from notifier import send_critical_alert, send_info_alert, test_notifications

# -------------------- CONFIG --------------------
st.set_page_config(page_title="System Monitor Dashboard", layout="wide")
st.title("Real-Time System Monitor with Alerts, Trends & History")
st.markdown("Monitor CPU, Memory, Disk usage, high-resource processes, and real-time alerts.")

# Load configuration
config = get_config()
refresh_rate = config["monitoring"]["refresh_rate"]
history_length = config["monitoring"]["history_length"]
COMMON_PORTS = config["network"]["common_ports"]
UNUSUAL_PORT_THRESHOLD = 5

# -------------------- SESSION STATE --------------------
if 'proc_history' not in st.session_state:
    st.session_state['proc_history'] = {}
if 'alert_history' not in st.session_state:
    st.session_state['alert_history'] = deque(maxlen=50)
if 'active_scans' not in st.session_state:
    st.session_state['active_scans'] = []
if 'kill_confirm' not in st.session_state:
    st.session_state['kill_confirm'] = ""
if 'auto_kill_enabled' not in st.session_state:
    st.session_state['auto_kill_enabled'] = False
if 'show_settings' not in st.session_state:
    st.session_state['show_settings'] = False

proc_history = st.session_state['proc_history']
alert_history = st.session_state['alert_history']

# -------------------- SIDEBAR - SAFETY CONTROLS --------------------
st.sidebar.title("Safety Controls")

# Emergency stop
if st.sidebar.button("EMERGENCY STOP AUTO-KILL", type="secondary", use_container_width=True):
    st.session_state['auto_kill_enabled'] = False
    st.session_state['kill_confirm'] = ""
    st.sidebar.success("Auto-kill feature DISABLED for safety!")
    
# Safety status
safety_status = "DANGEROUS" if st.session_state['auto_kill_enabled'] else "SAFE"
st.sidebar.metric("Safety Status", safety_status)

st.sidebar.markdown("---")
st.sidebar.info("Safety Features: Process whitelist, System process protection, Double confirmation required, Dry-run mode by default")

# -------------------- SIDEBAR - CONFIGURATION --------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Configuration")

# Settings toggle
if st.sidebar.button("Open Settings", key="open_settings", use_container_width=True):
    st.session_state['show_settings'] = not st.session_state['show_settings']

# Settings panel
if st.session_state['show_settings']:
    with st.sidebar.expander("Settings Panel", expanded=True):
        st.subheader("Alert Thresholds")
        
        # Get current config
        current_config = get_config()
        
        # Threshold settings
        cpu_threshold = st.slider(
            "CPU Alert Threshold (%)", 
            50, 100, 
            current_config["thresholds"]["cpu"],
            help="CPU usage above this percentage will trigger alerts"
        )
        
        memory_threshold = st.slider(
            "Memory Alert Threshold (%)", 
            50, 100, 
            current_config["thresholds"]["memory"],
            help="Memory usage above this percentage will trigger alerts"
        )
        
        disk_threshold = st.slider(
            "Disk Alert Threshold (%)", 
            50, 100, 
            current_config["thresholds"]["disk"],
            help="Disk usage above this percentage will trigger alerts"
        )
        
        st.subheader("Monitoring Settings")
        refresh_rate = st.slider(
            "Refresh Rate (seconds)", 
            1, 10, 
            current_config["monitoring"]["refresh_rate"],
            help="How often the dashboard updates"
        )
        
        st.subheader("Notification Settings")
        enable_notifications = st.checkbox(
            "Enable Notifications",
            value=current_config["notifications"]["enable_email"],
            help="Send alerts via notification system"
        )
        
        # Email Address Input Field
        email_address = st.text_input(
            "Recipient Email Address",
            value=current_config["notifications"]["email_address"],
            placeholder="Enter email address for alerts",
            help="Email address where alerts will be sent"
        )
        
        critical_only = st.checkbox(
            "Critical Alerts Only",
            value=current_config["notifications"]["critical_alerts_only"],
            help="Only send notifications for critical system alerts"
        )
        
        # Save settings
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Settings", use_container_width=True):
                new_config = current_config.copy()
                new_config["thresholds"]["cpu"] = cpu_threshold
                new_config["thresholds"]["memory"] = memory_threshold
                new_config["thresholds"]["disk"] = disk_threshold
                new_config["monitoring"]["refresh_rate"] = refresh_rate
                new_config["notifications"]["enable_email"] = enable_notifications
                new_config["notifications"]["email_address"] = email_address
                new_config["notifications"]["critical_alerts_only"] = critical_only
                
                if update_config(new_config):
                    st.success("Settings saved successfully!")
                    # Update current session config
                    config.update(new_config)
                else:
                    st.error("Failed to save settings")
        
        with col2:
            if st.button("Test Notifications", use_container_width=True):
                result = test_notifications()
                if "error" not in result:
                    st.success("Notification test completed!")
                else:
                    st.error("Notification test failed")

# Simulation toggle
simulate_anomaly = st.sidebar.checkbox("Simulate Anomalies", value=False, key="simulate_anomaly")

# -------------------- NETWORK SCANNING SECTION --------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Network Scanning")

scan_enable = st.sidebar.checkbox("Enable Range Scan", value=False, key="range_scan_enable")
quick_scan = st.sidebar.button("Quick Scan Common Ports", key="quick_scan_btn", use_container_width=True)
scan_host = st.sidebar.text_input("Host to scan", value="127.0.0.1", key="host_input")
start_port = st.sidebar.number_input("Start Port", min_value=1, max_value=65535, value=1, key="start_port_input")
end_port = st.sidebar.number_input("End Port", min_value=1, max_value=65535, value=1024, key="end_port_input")
scan_timeout = st.sidebar.number_input("Timeout (s)", min_value=0.05, max_value=2.0, value=0.2, step=0.05, key="timeout_input")
max_workers = st.sidebar.number_input("Threads", min_value=10, max_value=500, value=100, key="threads_input")

placeholder = st.empty()

# -------------------- FUNCTIONS --------------------
def _run_scan_and_store(host, ports_arg, timeout, max_workers, scan_id):
    try:
        if isinstance(ports_arg, list):
            result = scan_ports_list(host=host, ports_list=ports_arg, timeout=timeout, max_workers=max_workers)
        else:
            start, end = ports_arg
            result = scan_ports_range(host=host, start=start, end=end, timeout=timeout, max_workers=max_workers)
        st.session_state[f'port_scan_result_{scan_id}'] = result
        st.session_state[f'port_scan_status_{scan_id}'] = 'done'
    except Exception as e:
        st.session_state[f'port_scan_result_{scan_id}'] = []
        st.session_state[f'port_scan_status_{scan_id}'] = f'error: {e}'

def start_scan_async(host, ports_arg, timeout, max_workers):
    scan_id = int(time.time() * 1000)
    st.session_state[f'port_scan_status_{scan_id}'] = 'running'
    st.session_state[f'port_scan_result_{scan_id}'] = []
    t = threading.Thread(target=_run_scan_and_store, args=(host, ports_arg, timeout, max_workers, scan_id), daemon=True)
    t.start()
    st.session_state['active_scans'].append(scan_id)
    return scan_id

def colored_sparkline(values):
    if not values:
        return ""
    min_val, max_val = min(values), max(values)
    bars = "▁▂▃▄▅▆▇█"
    result = ""
    colors = []
    for v in values:
        idx = 0 if max_val - min_val == 0 else int((v - min_val) / (max_val - min_val) * (len(bars)-1))
        result += bars[idx]
        perc = (v - min_val) / (max_val - min_val + 0.0001)
        colors.append("red" if perc > 0.7 else "orange" if perc > 0.4 else "green")
    html = "".join([f"<span style='color:{c}'>{b}</span>" for b,c in zip(result, colors)])
    return html

# -------------------- MAIN LOOP --------------------
while True:
    with placeholder.container():
        
        # Network Scanning Section
        st.subheader("Network & Port Scan (Non-blocking)")
        
        # Start scans
        if quick_scan:
            sid = start_scan_async(scan_host, COMMON_PORTS, timeout=scan_timeout, max_workers=max_workers)
            st.success("Started quick-scan of common ports (background)")
        if scan_enable:
            sid = start_scan_async(scan_host, (int(start_port), int(end_port)), timeout=scan_timeout, max_workers=max_workers)
            st.info(f"Started scanning {scan_host}:{start_port}-{end_port} (background)")

        # Display scan results
        if st.session_state.get('active_scans'):
            st.subheader("Port Scan Results (recent)")
            to_remove = []
            for sid in list(st.session_state['active_scans']):
                status = st.session_state.get(f'port_scan_status_{sid}', 'unknown')
                res = st.session_state.get(f'port_scan_result_{sid}', None)
                st.write(f"Scan ID: {sid} — Status: {status}")
                if status == 'running':
                    st.write("Scanning... (results will appear when finished)")
                elif status.startswith('error'):
                    st.error(status)
                    to_remove.append(sid)
                else:
                    if res is None or len(res) == 0:
                        st.success("No open ports found")
                        to_remove.append(sid)
                    else:
                        st.markdown(f"**Open ports on {scan_host}:** {', '.join(map(str,res))}")
                        unusual_ports = [p for p in res if p not in COMMON_PORTS]
                        if len(res) > UNUSUAL_PORT_THRESHOLD or unusual_ports:
                            alert_text = f"Open ports detected on {scan_host}: {', '.join(map(str,res[:20]))}{'...' if len(res)>20 else ''}"
                            st.warning(alert_text)
                            log_alert(alert_text)
                            alert_history.appendleft(f"{datetime.now().strftime('%H:%M:%S')} - {alert_text}")
                        else:
                            st.info("Open ports found but within expected/common set")
                        to_remove.append(sid)
            for sid in to_remove:
                try:
                    st.session_state['active_scans'].remove(sid)
                except Exception:
                    pass

        st.caption("Non-blocking scans run in background threads. Do not scan external networks without permission.")

        # System metrics
        if simulate_anomaly:
            cpu, mem_percent, disk_percent = 95.0, 90.0, 85.0
        else:
            cpu, mem_percent, disk_percent = get_system_usage()

        st.subheader("System Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("CPU Usage (%)", f"{cpu:.1f}")
        col2.metric("Memory Usage (%)", f"{mem_percent:.1f}")
        col3.metric("Disk Usage (%)", f"{disk_percent:.1f}")

        # Comprehensive Alerts with Notifications
        processes_data = get_high_resource_processes()
        all_alerts = get_comprehensive_alerts(cpu, mem_percent, disk_percent, processes_data)
        
        if all_alerts:
            st.subheader("System Alerts")
            for a in all_alerts:
                timestamped_alert = f"{datetime.now().strftime('%H:%M:%S')} - {a}"
                if timestamped_alert not in alert_history:
                    alert_history.appendleft(timestamped_alert)
                    log_alert(timestamped_alert)
                    
                    # Send notifications for alerts
                    if "CRITICAL" in a or "overload" in a.lower() or "crash" in a.lower():
                        send_critical_alert("System Emergency", a)
                    else:
                        send_info_alert("System Alert", a)
            
            # Show recent alerts
            st.write("\n".join(list(alert_history)[:10]))  # Show only 10 most recent
        else:
            st.subheader("System Status")
            st.success("All systems normal. No critical alerts detected.")

        # High resource processes
        st.subheader("High Resource Processes")
        processes = get_high_resource_processes(limit=8)
        parsed = []
        for p in processes:
            parts = p.split()
            if len(parts) >= 4:
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
            st.write("**Processes with Resource Trends**")
            for idx, row in df.iterrows():
                pid = row['PID']
                cpu_history = list(proc_history.get(pid, {}).get("cpu", []))
                mem_history = list(proc_history.get(pid, {}).get("mem", []))
                
                cpu_html = colored_sparkline(cpu_history)
                mem_html = colored_sparkline(mem_history)
                
                st.markdown(
                    f"**{row['Name']}** (PID:{pid}) | CPU: {row['CPU%']:.1f}% {cpu_html} | MEM: {row['Memory(MB)']:.1f}MB {mem_html}",
                    unsafe_allow_html=True
                )
        else:
            st.info("No high resource processes detected.")

        # -------------------- SAFE PROCESS MANAGEMENT --------------------
        st.markdown("---")
        st.subheader("Process Management (Safe Mode)")
        
        # Get processes that need review
        review_processes = get_processes_for_review()
        
        if review_processes:
            st.warning(f"Found {len(review_processes)} processes that may need attention:")
            
            # Display processes in a table
            review_data = []
            for proc in review_processes:
                review_data.append({
                    "Process": proc['name'],
                    "PID": proc['pid'],
                    "CPU%": f"{proc['cpu']:.1f}",
                    "Memory": f"{proc['memory_mb']:.1f}MB",
                    "Reason": proc['reason']
                })
            
            st.table(pd.DataFrame(review_data))
            
            # Safety confirmation for process termination
            st.markdown("---")
            st.subheader("Process Termination (Requires Confirmation)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Refresh Process List", use_container_width=True):
                    st.rerun()
            
            with col2:
                # Double confirmation system
                confirm1 = st.checkbox("I understand this may cause system instability", key="confirm1")
                if confirm1:
                    confirm2 = st.checkbox("I have saved all my work", key="confirm2")
                    if confirm2:
                        kill_text = st.text_input("Type 'KILL' to confirm:", key="kill_confirm")
                        if kill_text.strip().upper() == "KILL":
                            st.session_state['auto_kill_enabled'] = True
                            st.error("AUTO-KILL ENABLED - Processes will be terminated!")
                        else:
                            st.session_state['auto_kill_enabled'] = False
                    else:
                        st.session_state['auto_kill_enabled'] = False
                else:
                    st.session_state['auto_kill_enabled'] = False
            
            # Execute auto-kill if enabled
            if st.session_state['auto_kill_enabled']:
                st.warning("EXECUTING PROCESS TERMINATION...")
                killed_count, killed_list = auto_kill_processes(dry_run=False)
                
                if killed_count > 0:
                    st.error(f"Terminated {killed_count} processes")
                    for killed in killed_list:
                        st.write(f"- {killed}")
                    # Reset after killing
                    st.session_state['auto_kill_enabled'] = False
                    st.rerun()
                else:
                    st.info("No processes were terminated")
            else:
                # Dry run mode (default)
                st.info("Safe Mode: Showing what WOULD be terminated (dry-run)")
                killed_count, killed_list = auto_kill_processes(dry_run=True)
                if killed_list:
                    st.write("**Processes that would be terminated:**")
                    for killed in killed_list:
                        st.write(f"- {killed}")
        else:
            st.success("No problematic processes detected. System is running normally.")

        # Historical metrics
        st.markdown("---")
        st.subheader("Historical System Metrics")
        try:
            if pd.io.common.file_exists(DB_FILE):
                hist_df = pd.read_csv(DB_FILE, parse_dates=["timestamp"])
                st.line_chart(hist_df.set_index("timestamp")[["cpu","mem","disk"]])
            else:
                st.info("No historical data yet. Data will appear after a few refresh cycles.")
        except Exception as e:
            st.error(f"Error loading historical data: {e}")

        st.caption(f"Dashboard updates every {refresh_rate} seconds. Safety features: Process whitelist, system protection, confirmation required.")
        st.caption("Developed using Streamlit. Use with caution on production systems.")

    time.sleep(refresh_rate)
