# set_recipient.py
from config import get_config, update_config

config = get_config()
config["notifications"]["email_address"] = "goyalsneha405@gmail.com"
config["notifications"]["enable_email"] = True

if update_config(config):
    print("✅ Recipient email set to: goyalsneha405@gmail.com")
    print("✅ Email notifications enabled")
else:
    print("❌ Failed to save config")
    