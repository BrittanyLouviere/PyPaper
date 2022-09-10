import os
import json
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
import feedparser
import ssl
from datetime import datetime, timedelta
from calendar import timegm

# Find all feeds in the ./Feeds directory except for the example feed
feedDir = os.path.join(os.path.dirname(__file__), "Feeds")
for filename in os.listdir(feedDir):
  if filename.endswith(".json") and not filename == "exampleFeed.json":

    # Open and read feed file
    file = open(os.path.join(feedDir, filename), "r")
    feed = json.load(file)
    file.close()

    # Get time frame for feed items
    if "time frame" in feed["settings"]:
      hours, minutes = [int(x) for x in feed["settings"]["time frame"].split(":")]
      timeFrame = datetime.now() - timedelta(hours=hours, minutes=minutes)
    else:
      timeFrame = datetime.min

    # Create email
    msg = EmailMessage()
    msg['Subject'] = "PyPaper - " + os.path.splitext(filename)[0]
    msg['From'] = msg['To'] = feed["settings"]["email address"]

    # Fix common ssl issue
    if hasattr(ssl, '_create_unverified_context'):
      ssl._create_default_https_context = ssl._create_unverified_context

    # Create message content
    content = ""

    # HTML templates
    sectionHeaderHTML = "<h1>{0}</h1>"
    siteHeaderHTML = "<a href='{0}'><h2>{1}</h2></a>"
    entryHeaderHTML = "<a href='{0}'><h3>{1}</h3></a>"
    entryContentHTML = "<p>{0}</p>"

    for section in feed["feeds"]:
      # Create header for feed section
      content += sectionHeaderHTML.format(section)

      for site in feed["feeds"][section]:
        # Parse Feed
        parsedFeed = feedparser.parse(site["url"])

        # Create header for site and start unordered list
        # if an alternative title is specified in the json, use that instead of the feed title
        title = site["title"] if "title" in site else parsedFeed["feed"]["title"]
        content += siteHeaderHTML.format(parsedFeed["feed"]["link"], title)
        content += "<ul>"

        # Iterarte through entries and add each as a list item
        for i in range(min(site["max posts"], len(parsedFeed["entries"]))):
          entry = parsedFeed["entries"][i]

          # Parse datetime and check if the entry is within the user's set timeframe
          entryDate = datetime.fromtimestamp(timegm(entry.published_parsed))
          if entryDate > timeFrame:
            content += "<li>"
            content += entryHeaderHTML.format(entry["link"], entry["title"])
            if site["full text"]:
              content += entryContentHTML.format(entry["summary"])
            content += "</li>"

        # End unordered list
        content += "</ul>"

    # Add content to email message   
    msg.set_content(MIMEText(content, "html"))

    # Create SMTP connection
    s = smtplib.SMTP(feed["settings"]["smtp server"], feed["settings"]["smtp port"])
    s.starttls()
    s.login(feed["settings"]["email address"], feed["settings"]["email password"])

    # Send email
    s.send_message(msg)
    s.quit()
