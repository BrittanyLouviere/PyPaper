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
    # Error handling for entire content section
    try:
      # Open and read feed file
      file = open(os.path.join(feedDir, filename), "r")
      feed = json.load(file)
      file.close()

      # Get global time frame for feed items
      # If not set, allow everything
      if "time frame" in feed["settings"]:
        hours, minutes = [int(x) for x in feed["settings"]["time frame"].split(":")]
        globalTimeFrame = datetime.now() - timedelta(hours=hours, minutes=minutes)
      else:
        globalTimeFrame = datetime.min

      # Get global max posts
      # If not set, default to 5
      globalMaxPosts = feed["settings"]["max posts"] if "max posts" in feed["settings"] else 5

      # Get global full text option
      # If not set, default to false
      globalFullText = feed["settings"]["full text"] if "full text" in feed["settings"] else False

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
        # Hold the section content in a temp variable in case there are no entries
        sectionContent = ""
        sectionHasContent = False
        # Create header for feed section
        sectionContent += sectionHeaderHTML.format(section)

        for site in feed["feeds"][section]:
          try:
            # Get site time frame if there is one, else just use global
            siteTimeFrame = globalTimeFrame
            if "time frame" in site:
              hours, minutes = [int(x) for x in site["time frame"].split(":")]
              siteTimeFrame = datetime.now() - timedelta(hours=hours, minutes=minutes)

            # Get site max posts if there is one, else use global
            siteMaxPosts = site["max posts"] if "max posts" in site else globalMaxPosts

            # Get site "full text" if there is one, else use global
            siteFullText = site["full text"] if "full text" in site else globalFullText

            # Parse Feed
            parsedFeed = feedparser.parse(site["url"])

            # Create header for site and start unordered list
            # if an alternative title is specified in the json, use that instead of the feed title
            # if an alternative url is specified in the json, use that instead of the feed url
            title = site["title"] if "title" in site else parsedFeed["feed"]["title"]
            link = site["alternate url"] if "alternate url" in site else parsedFeed["feed"]["link"]

            # Hold site content in a temp variable incase there are no entries
            siteContent = ""
            siteContent += siteHeaderHTML.format(link, title)
            siteContent += "<ul>"

            # Iterate through entries and add each as a list item
            hasEntries = False
            for i in range(min(siteMaxPosts, len(parsedFeed["entries"]))):
              try:
                entry = parsedFeed["entries"][i]

                # Parse datetime and check if the entry is within the user's set timeframe
                # If there isn't a published date for the item, assume the item was published now and allow it
                entryDate = datetime.fromtimestamp(timegm(entry["published_parsed"])) if "published_parsed" in entry else datetime.now()
                if entryDate > siteTimeFrame:
                  hasEntries = True
                  siteContent += "<li>"
                  siteContent += entryHeaderHTML.format(entry["link"], entry["title"])
                  if siteFullText:
                    if "<img" in entry["summary"]:
                      entry["summary"] = '<img style="max-width: 100%"'.join(entry["summary"].split("<img"))
                    siteContent += entryContentHTML.format(entry["summary"])
                  siteContent += "</li>"
              except Exception as e:
                siteContent += "<li>Error with entry: {} {}</li>".format(str(type(e)).replace("<", "").replace(">", ""), e)
                hasEntries = True
            
            # Add the site's content to the section content only if there are entries to display
            if hasEntries:
              sectionHasContent = True
              sectionContent += siteContent

            # End unordered list
            sectionContent += "</ul>"
          except Exception as e:
            sectionHasContent = True
            sectionContent += "<h2>Error with site: {}</h2>".format(site["url"])
            if parsedFeed["bozo"]:
              sectionContent += "<ul><li>{}</li></ul>".format(str(parsedFeed["bozo_exception"]).replace("<", "").replace(">", ""))
            else:
              sectionContent += "<ul><li>{}</li><li>{}</li></ul>".format(str(type(e)).replace("<", "").replace(">", ""), e)
        # Add the section content to the email content only if there are entries to display
        if sectionHasContent:
          content += sectionContent      
    except Exception as e:
      content = "<h1>Error while creating feed:</h1>"
      content += "<p>{}</p>".format(str(type(e)).replace("<", "").replace(">", ""))
      content += "<p>{}</p>".format(e)

    # Add content to email message   
    msg.set_content(MIMEText(content, "html"))

    # Create SMTP connection
    s = smtplib.SMTP(feed["settings"]["smtp server"], feed["settings"]["smtp port"])
    s.starttls()
    s.login(feed["settings"]["email address"], feed["settings"]["email password"])

    # Send email
    s.send_message(msg)
    s.quit()
