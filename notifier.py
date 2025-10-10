# notifier.py - COMPLETE WORKING VERSION
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime
from config import get_config

class Notifier:
    def __init__(self):
        self.config = get_config()
        self.setup_logging()
        
        # Gmail SMTP Configuration with App Password
        self.SMTP_SERVER = "smtp.gmail.com"
        self.SMTP_PORT = 587
        self.SMTP_USERNAME = "lakshaygoyal2509@gmail.com"
        self.SMTP_PASSWORD = "aafqezcwrivumhlb"
    
    def setup_logging(self):
        """Setup logging for notifications"""
        logging.basicConfig(
            filename='notifications.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def send_email_alert(self, subject, message, is_critical=False):
        """
        Send REAL email using Gmail SMTP
        """
        try:
            # RELOAD CONFIG EVERY TIME to get latest settings
            current_config = get_config()
            notification_config = current_config["notifications"]
            
            # Check if email is enabled
            if not notification_config.get("enable_email", False):
                return False
            
            # Check if only critical alerts are enabled
            if notification_config.get("critical_alerts_only", False) and not is_critical:
                return False
            
            # Get recipient email from config
            recipient_email = notification_config.get("email_address", "")
            if not recipient_email:
                print("No recipient email address configured")
                return False
            
            print(f"Attempting to send email FROM: {self.SMTP_USERNAME}")
            print(f"Attempting to send email TO: {recipient_email}")
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.SMTP_USERNAME
            msg['To'] = recipient_email
            msg['Subject'] = f"System Alert: {subject}"
            
            # Email body with clean formatting
            hostname = socket.gethostname()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            email_body = f"""
SYSTEM MONITOR ALERT

System: {hostname}
Time: {current_time}
Alert Type: {subject}
Priority: {'CRITICAL' if is_critical else 'INFO'}

ALERT DETAILS:
{message}

SYSTEM INFORMATION:
- Hostname: {hostname}
- Time Detected: {current_time}
- Alert Level: {'CRITICAL - Immediate Action Required' if is_critical else 'Information'}

RECOMMENDED ACTIONS:
- Check the System Monitor Dashboard
- Review running processes
- Take appropriate action if needed

---
This is an automated alert from your System Monitoring Tool.
            """
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            # Send email using Gmail SMTP
            print("Connecting to Gmail SMTP server...")
            server = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
            server.starttls()
            
            print("Authenticating with Gmail...")
            server.login(self.SMTP_USERNAME, self.SMTP_PASSWORD)
            
            print("Sending email...")
            server.send_message(msg)
            server.quit()
            
            print(f"REAL EMAIL SENT SUCCESSFULLY!")
            print(f"FROM: {self.SMTP_USERNAME}")
            print(f"TO: {recipient_email}")
            print(f"SUBJECT: {subject}")
            logging.info(f"Email alert sent to {recipient_email}: {subject}")
            
            return True
            
        except Exception as e:
            print(f"EMAIL FAILED: {e}")
            logging.error(f"Email send error: {e}")
            return False
    
    def send_desktop_notification(self, title, message):
        """
        Send desktop notification
        """
        try:
            # For Windows
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=5)
                return True
            except ImportError:
                pass
            
            # For Linux
            try:
                import subprocess
                subprocess.Popen(['notify-send', title, message])
                return True
            except:
                pass
            
            # For Mac
            try:
                import subprocess
                script = f'display notification "{message}" with title "{title}"'
                subprocess.run(['osascript', '-e', script])
                return True
            except:
                pass
            
            # Fallback - just print
            print(f"DESKTOP NOTIFICATION: {title} - {message}")
            return True
            
        except Exception as e:
            print(f"Desktop notification failed: {e}")
            return False
    
    def send_alert(self, alert_type, message, is_critical=False):
        """
        Main alert method - sends all types of notifications
        """
        try:
            results = {
                'email_sent': False,
                'desktop_sent': False,
                'logged': True
            }
            
            # Send email alert
            results['email_sent'] = self.send_email_alert(alert_type, message, is_critical)
            
            # Send desktop notification for critical alerts
            if is_critical:
                results['desktop_sent'] = self.send_desktop_notification(
                    f"ALERT: {alert_type}", 
                    message
                )
            
            # Always log the alert
            logging.info(f"ALERT - {alert_type}: {message}")
            
            return results
            
        except Exception as e:
            logging.error(f"Alert sending failed: {e}")
            return {'error': str(e)}
    
    def test_connection(self):
        """Test email connectivity"""
        try:
            print("Testing Email System...")
            print(f"SMTP Server: {self.SMTP_SERVER}")
            print(f"Username: {self.SMTP_USERNAME}")
            
            # Test email with simple message
            test_message = "This is a test email from your System Monitor. If you receive this, email notifications are working correctly!"
            
            results = self.send_alert(
                "Email Test", 
                test_message,
                is_critical=False
            )
            
            print("\nTest Results:")
            print(f"   Email: {'SUCCESS' if results.get('email_sent') else 'FAILED'}")
            print(f"   Logged: OK")
            
            if results.get('email_sent'):
                print(f"\nCheck your test email in the recipient's Gmail inbox")
            
            return results
            
        except Exception as e:
            print(f"Test failed: {e}")
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
