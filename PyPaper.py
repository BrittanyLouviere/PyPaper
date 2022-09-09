import os
import json
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText

# Find all feeds in the ./Feeds directory except for the example feed
feedDir = os.path.join(os.path.dirname(__file__), "Feeds")
for filename in os.listdir(feedDir):
  if filename.endswith(".json") and not filename == "exampleFeed.json":

    # Open and read feed file
    file = open(os.path.join(feedDir, filename), "r")
    feed = json.load(file)
    file.close()

    # Create email
    msg = EmailMessage()
    msg['Subject'] = "PyPaper - " + os.path.splitext(filename)[0]
    msg['From'] = msg['To'] = feed["login"]["email address"]

    # Create message content
    content = ""
    for section in feed["feeds"]:
      # Create header for feed section
      content += "<h1>" + section + "</h1>\n"
      for site in feed["feeds"][section]:
        siteInfo = feed["feeds"][section][site]
        # Create header for site
        siteHeader = "<a href='{0}'><h2>{1}</h2></a>\n"
        content += siteHeader.format(siteInfo["url"].rsplit("/", 1)[0], site)
    msg.set_content(MIMEText(content, "html"))

    # Create SMTP connection
    s = smtplib.SMTP(feed["login"]["smtp server"], feed["login"]["smtp port"])
    s.starttls()
    s.login(feed["login"]["email address"], feed["login"]["email password"])

    # Send email
    s.send_message(msg)
    s.quit()
