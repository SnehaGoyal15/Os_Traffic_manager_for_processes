# collectors.py
import psutil
import pandas as pd
from datetime import datetime
from logger import DB_FILE

def get_system_usage():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    # Log to DB_FILE for historical chart
    try:
        timestamp = datetime.now()
        df = pd.DataFrame([[timestamp, cpu, mem, disk]], columns=["timestamp", "cpu", "mem", "disk"])
        df.to_csv(DB_FILE, mode='a', header=not pd.io.common.file_exists(DB_FILE), index=False)
    except Exception as e:
        print(f"Error logging system usage: {e}")

    return cpu, mem, disk

def get_high_resource_processes(limit=5):
    """
    Returns top processes sorted by CPU + Memory usage
    Format: PID Name CPU% MEM(MB)
    """
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            pid = p.info['pid']
            name = p.info['name']
            cpu_percent = p.info['cpu_percent']
            mem_mb = p.info['memory_info'].rss / (1024*1024)
            procs.append(f"{pid} {name} {cpu_percent:.1f} {mem_mb:.1f}")
        except Exception:
            continue
    procs = sorted(procs, key=lambda x: float(x.split()[-2]) + float(x.split()[-1]), reverse=True)
    return procs[:limit]
