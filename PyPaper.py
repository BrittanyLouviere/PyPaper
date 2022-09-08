import os
import json
import smtplib
from email.message import EmailMessage

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'Feeds', 'testFeed.json')
file = open(filename, "r")
feed = json.load(file)

# Create Email
msg = EmailMessage()
msg.set_content("Hello World!")
msg['Subject'] = "Hello"
msg['From'] = msg['To'] = feed["login"]["email address"]

# Create SMTP connection
s = smtplib.SMTP(feed["login"]["smtp server"], feed["login"]["smtp port"])
s.starttls()
s.login(feed["login"]["email address"], feed["login"]["email password"])

# Send Email
s.send_message(msg)
s.quit()