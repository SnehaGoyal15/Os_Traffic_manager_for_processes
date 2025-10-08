import psutil
import time
import os
from datetime import datetime

# ----------------- THRESHOLDS -----------------
CPU_THRESHOLD = 80           # % CPU usage
MEM_THRESHOLD = 200          # MB memory usage
PROC_CPU_THRESHOLD = 20      # % per-process CPU usage
PROC_MEM_THRESHOLD = 100     # MB per-process memory usage
PROC_NET_THRESHOLD = 1       # MB per-process network activity

# ----------------- COLORS -----------------
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
BLINK = '\033[5m'
RESET = '\033[0m'

# ----------------- LOG FILE (local folder, not OneDrive) -----------------
LOG_FILE = os.path.join(os.path.dirname(__file__), "high_resource_log.txt")

# ----------------- HELPERS -----------------
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_bar(percentage, length=30):
    filled_length = int(length * percentage // 100)
    return '█' * filled_length + '-' * (length - filled_length)

def log_message(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# For tracking per-process "network" approximation
prev_proc_net = {}

# ----------------- MAIN LOOP -----------------
while True:
    clear_screen()

    # --- SYSTEM USAGE ---
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    print("=== SYSTEM RESOURCE USAGE ===")
    print(f"CPU Usage   : |{get_bar(cpu)}| {cpu:.1f}%")
    print(f"Memory Usage: |{get_bar(memory.percent)}| {memory.percent:.1f}%")
    print(f"Disk Usage  : |{get_bar(disk.percent)}| {disk.percent:.1f}%\n")

    # --- HIGH RESOURCE USAGE PROCESSES ---
    print("=== ALERT: High Resource Usage Processes ===")
    print(f"{'PID':<8}{'Name':<25}{'CPU%':<10}{'Memory(MB)':<12}{'DiskIO(MB)':<12}{'Net(MB)':<10}")

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'io_counters']):
        try:
            cpu_proc = proc.cpu_percent(interval=None)
            mem_proc = proc.info['memory_info'].rss / (1024 * 1024)

            # Disk I/O
            disk_io = 0
            if proc.info['io_counters']:
                disk_io = (proc.info['io_counters'].read_bytes + proc.info['io_counters'].write_bytes) / (1024 * 1024)

            # "Network usage" approximation → just counts active connections
            net_bytes = 0
            try:
                connections = proc.connections(kind='inet')
                for conn in connections:
                    if conn.raddr:
                        net_bytes += 1  # counts active remote connections
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass

            net_mb = (net_bytes - prev_proc_net.get(proc.info['pid'], 0)) / 1024 / 1024
            prev_proc_net[proc.info['pid']] = net_bytes

            # Color coding
            color = GREEN
            if cpu_proc > PROC_CPU_THRESHOLD or mem_proc > PROC_MEM_THRESHOLD or net_mb > PROC_NET_THRESHOLD:
                color = RED
            elif disk_io > 50:
                color = YELLOW

            if cpu_proc > PROC_CPU_THRESHOLD or mem_proc > PROC_MEM_THRESHOLD or disk_io > 50 or net_mb > PROC_NET_THRESHOLD:
                msg = f"{proc.info['pid']:<8}{proc.info['name']:<25}{cpu_proc:<10.1f}{mem_proc:<12.2f}{disk_io:<12.2f}{net_mb:<10.2f}"
                print(f"{color}{msg}{RESET}")
                log_message(msg)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    time.sleep(2)
