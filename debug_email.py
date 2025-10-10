# debug_email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def debug_gmail_connection():
    print("🔍 Debugging Gmail Connection...")
    print("=" * 50)
    
    # Your credentials - UPDATE THESE
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    USERNAME = "lakshaygoyal2509@gmail.com"
    PASSWORD = "aafqezcwrivumhlb"  # Replace with your actual password
    
    try:
        print("1. Testing SMTP connection...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        print("   ✅ SMTP connection successful")
        
        print("2. Testing STARTTLS...")
        server.starttls()
        print("   ✅ STARTTLS successful")
        
        print("3. Testing login...")
        server.login(USERNAME, PASSWORD)
        print("   ✅ Login successful")
        
        print("4. Testing email send...")
        msg = MIMEMultipart()
        msg['From'] = USERNAME
        msg['To'] = "test@example.com"
        msg['Subject'] = "Test Email from Debug"
        
        body = "This is a test email from the debug script."
        msg.attach(MIMEText(body, 'plain'))
        
        server.send_message(msg)
        print("   ✅ Email send successful")
        
        server.quit()
        print("🎉 ALL TESTS PASSED! Email system is working.")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ AUTHENTICATION FAILED: {e}")
        print("   Check: 2-step verification enabled? App password correct?")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    debug_gmail_connection()