# debug_notifier.py
from notifier import notifier
from config import get_config

print("Debugging Notifier Configuration...")
print("=" * 50)

# Check config
config = get_config()
print("1. Config Email Settings:")
print(f"   Enable Email: {config['notifications']['enable_email']}")
print(f"   Email Address: '{config['notifications']['email_address']}'")
print(f"   Critical Only: {config['notifications']['critical_alerts_only']}")

print("\n2. Notifier SMTP Settings:")
print(f"   SMTP Server: {notifier.SMTP_SERVER}")
print(f"   Username: {notifier.SMTP_USERNAME}")
print(f"   Password Length: {len(notifier.SMTP_PASSWORD)}")

print("\n3. Testing send_email_alert directly...")
try:
    result = notifier.send_email_alert("Direct Test", "Testing notifier directly")
    print(f"   Result: {'SUCCESS' if result else 'FAILED'}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n4. Checking config file...")
import os
if os.path.exists("monitor_config.json"):
    with open("monitor_config.json", "r") as f:
        print("   Config file content:")
        print(f"   {f.read()}")
else:
    print("   Config file not found")