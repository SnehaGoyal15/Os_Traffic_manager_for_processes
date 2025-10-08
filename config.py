# config.py
import json
import os

class Config:
    def __init__(self):
        self.config_file = "monitor_config.json"
        self.default_config = {
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
                "enable_email": False,
                "email_address": "",
                "critical_alerts_only": True
            },
            "network": {
                "common_ports": [22, 80, 443, 53, 3389, 3306, 5432, 8080, 5900],
                "scan_timeout": 0.2,
                "max_workers": 100
            }
        }
    
    def load_config(self):
        """Load configuration from file or return defaults"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    # Merge with defaults (in case new settings were added)
                    return self._merge_configs(self.default_config, saved_config)
        except Exception as e:
            print(f"Config load error: {e}. Using defaults.")
        
        return self.default_config.copy()
    
    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Config save error: {e}")
            return False
    
    def _merge_configs(self, default, user):
        """Merge default config with user config"""
        merged = default.copy()
        for key, value in user.items():
            if isinstance(value, dict) and key in merged:
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged
    
    def get_threshold(self, metric):
        """Get threshold for specific metric"""
        config = self.load_config()
        return config["thresholds"].get(metric, 80)
    
    def get_refresh_rate(self):
        """Get dashboard refresh rate"""
        config = self.load_config()
        return config["monitoring"].get("refresh_rate", 2)

# Global config instance
app_config = Config()

# Helper functions
def get_config():
    return app_config.load_config()

def update_config(new_settings):
    return app_config.save_config(new_settings)