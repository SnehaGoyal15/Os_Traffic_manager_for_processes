# fix_config_completely.py
from config import get_config, update_config

# Reset config with correct settings
config = {
    "thresholds": {
        "cpu": 85,
        "memory": 80,
        "disk": 90
    },
    "monitoring": {
        "refresh_rate": 2,
        "history_length": 100,
        "max_processes_display": 8
    },
    "safety": {
        "dry_run": True,
        "enable_auto_kill": False,
        "require_confirmation": True
    },
    "notifications": {
        "enable_email": True,
        "email_address": "goyalsneha405@gmail.com",  # Correct recipient
        "critical_alerts_only": False  # Allow all alerts
    },
    "network": {
        "common_ports": [22, 80, 443, 53, 3389, 3306, 5432, 8080, 5900],
        "scan_timeout": 0.2,
        "max_workers": 100
    }
}

if update_config(config):
    print("✅ Config completely reset with correct settings!")
    print(f"✅ Recipient: {config['notifications']['email_address']}")
    print(f"✅ Critical Only: {config['notifications']['critical_alerts_only']}")
else:
    print("❌ Failed to update config")