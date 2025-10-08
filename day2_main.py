import time
import psutil
from datetime import datetime

# Import from your modules
from collectors import get_system_usage, get_high_resource_processes
from analyzer import check_system_metrics, correlation_checks
from logger import log_alert
from automation import auto_kill_processes   # optional

# ----------------- MAIN LOOP -----------------
def main():
    while True:
        # --- Collect system metrics ---
        cpu, mem_percent, disk_percent = get_system_usage()

        # --- Analyze metrics ---
        alerts = check_system_metrics(cpu, mem_percent, disk_percent)
        correlations = correlation_checks(cpu, mem_percent, disk_percent)

        # --- Log + print alerts ---
        if alerts or correlations:
            print("=== ALERTS ===")
            for a in alerts + correlations:
                print(" -", a)
                log_alert(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {a}")

        # --- Print system usage ---
        print("=== SYSTEM RESOURCE USAGE ===")
        print(f"CPU Usage   : {cpu:.1f}%")
        print(f"Memory Usage: {mem_percent:.1f}%")
        print(f"Disk Usage  : {disk_percent:.1f}%\n")

        # --- Show high resource usage processes ---
        print("=== HIGH RESOURCE USAGE PROCESSES ===")
        processes = get_high_resource_processes()
        for p in processes:
            print(p)
            log_alert(p)

        # --- (Optional) Automation ---
        auto_kill_processes()

        time.sleep(2)

if __name__ == "__main__":
    main()
