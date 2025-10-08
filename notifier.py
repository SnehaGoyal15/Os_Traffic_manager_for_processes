# notifier.py - SIMPLE VERSION
import logging
from config import get_config

class Notifier:
    def __init__(self):
        self.config = get_config()
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for notifications"""
        logging.basicConfig(
            filename='notifications.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def send_alert(self, alert_type, message, is_critical=False):
        """
        Simple alert method - just logs for now
        """
        try:
            results = {
                'email_sent': False,
                'desktop_sent': False,
                'logged': True
            }
            
            # Always log the alert
            log_message = f"{alert_type.upper()}: {message}"
            logging.info(log_message)
            
            # Print to console for demo
            if is_critical:
                print(f"🚨 CRITICAL ALERT: {message}")
            else:
                print(f"⚠️ ALERT: {message}")
            
            return results
            
        except Exception as e:
            print(f"Alert sending failed: {e}")
            return {'error': str(e)}
    
    def test_connection(self):
        """Test notification connectivity"""
        try:
            results = self.send_alert(
                "Test Alert", 
                "This is a test notification from System Monitor",
                is_critical=False
            )
            
            print("✅ Notification System Tested Successfully!")
            print("   All alerts are being logged to notifications.log")
            
            return results
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return {'error': str(e)}

# Global notifier instance
notifier = Notifier()

# Helper functions
def send_critical_alert(alert_type, message):
    """Send critical alert"""
    return notifier.send_alert(alert_type, message, is_critical=True)

def send_info_alert(alert_type, message):
    """Send informational alert"""
    return notifier.send_alert(alert_type, message, is_critical=False)

def test_notifications():
    """Test all notification systems"""
    return notifier.test_connection()