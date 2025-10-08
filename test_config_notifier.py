# test_config_notifier.py
from config import get_config, update_config
from notifier import test_notifications

print("🔧 Testing Config System...")
config = get_config()
print("Current Config:")
print(f"  CPU Threshold: {config['thresholds']['cpu']}%")
print(f"  Memory Threshold: {config['thresholds']['memory']}%") 
print(f"  Refresh Rate: {config['monitoring']['refresh_rate']}s")

print("\n🔔 Testing Notifications...")
test_notifications()

print("\n✅ All tests completed! Check notifications.log file.")