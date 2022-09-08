import os
import json
import smtplib
from email.message import EmailMessage

# Find all feeds in the ./Feeds directory except for the example feed
feedDir = os.path.join(os.path.dirname(__file__), "Feeds")
for filename in os.listdir(feedDir):
  if filename.endswith(".json") and not filename == "exampleFeed.json":
    
    # Open and read feed file
    file = open(os.path.join(feedDir, filename), "r")
    feed = json.load(file)
    file.close()

    # Create Email
    msg = EmailMessage()
    msg['Subject'] = "PyPaper - " + os.path.splitext(filename)[0]
    msg['From'] = msg['To'] = feed["login"]["email address"]

    msg.set_content("Hello World!")

    # Create SMTP connection
    s = smtplib.SMTP(feed["login"]["smtp server"], feed["login"]["smtp port"])
    s.starttls()
    s.login(feed["login"]["email address"], feed["login"]["email password"])

    # Send Email
    s.send_message(msg)
    s.quit()
