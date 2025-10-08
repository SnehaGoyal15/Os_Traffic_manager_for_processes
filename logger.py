# logger.py - SIMPLE VERSION (No Emojis)
import os

DB_FILE = "system_metrics.csv"

def log_alert(alert_text):
    """Append alert to a log file"""
    try:
        with open("alerts.log", "a", encoding="utf-8") as f:
            f.write(f"{alert_text}\n")
    except Exception as e:
        # If UTF-8 fails, try without encoding
        try:
            with open("alerts.log", "a") as f:
                f.write(f"{alert_text}\n")
        except Exception as e2:
            print(f"Error logging alert: {e2}")