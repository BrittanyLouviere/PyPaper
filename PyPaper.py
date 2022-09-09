import os
import json
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
import feedparser
import ssl

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
    sectionHeaderHTML = "<h1>{0}</h1>\n"
    siteHeaderHTML = "<a href='{0}'><h2>{1}</h2></a>\n"
    entryHeaderHTML = "<a href='{0}'><h3>{1}</h3></a>\n"
    entryContentHTML = "<p>{0}</p>\n"
    for section in feed["feeds"]:
      # Create header for feed section
      content += sectionHeaderHTML.format(section)

      for site in feed["feeds"][section]:
        # Parse Feed
        if hasattr(ssl, '_create_unverified_context'):
          ssl._create_default_https_context = ssl._create_unverified_context
        parsedFeed = feedparser.parse(site["url"])

        # Create header for site and start unordered list
        # if an alternative title is specified in the json, use that instead of the feed title
        title = site["title"] if "title" in site else parsedFeed["feed"]["title"]
        content += siteHeaderHTML.format(parsedFeed["feed"]["link"], title)
        content += "<ul>"

        # Iterarte through entries and add each as a list item
        for i in range(min(site["max posts"], len(parsedFeed["entries"]))):
          entry = parsedFeed["entries"][i]
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
    s = smtplib.SMTP(feed["login"]["smtp server"], feed["login"]["smtp port"])
    s.starttls()
    s.login(feed["login"]["email address"], feed["login"]["email password"])

    # Send email
    s.send_message(msg)
    s.quit()
