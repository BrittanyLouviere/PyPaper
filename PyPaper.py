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
articleLogDir = os.path.join(os.path.dirname(__file__), "ArticleLogs")
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
      globalMaxPosts = feed["settings"]["max posts"] if "max posts" in feed["settings"] else 10

      # Get global full text option
      # If not set, default to false
      globalFullText = feed["settings"]["full text"] if "full text" in feed["settings"] else False

      # Get log article option
      # If not set, default to true
      logArticles = feed["settings"]["log articles"] if "log articles" in feed["settings"] else True

      # Get block list
      blockList = [x.lower() for x in feed["settings"]["block list"]] if "block list" in feed["settings"] else []

      # Get allow list
      allowList = [x.lower() for x in feed["settings"]["allow list"]] if "allow list" in feed["settings"] else []

      # Retrieve article log if needed (create log if needed)
      if logArticles:
        try:
          with open(os.path.join(articleLogDir, filename), "r") as logFile:
            oldLog = json.load(logFile)
        except Exception as e:
          os.makedirs(articleLogDir, exist_ok=True)
          oldLog = {}
        newLog = {}

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

        # Create dictionary for this section's log
        if logArticles:
          newLog[section] = {}

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

            # Get this site's log and create a dictionary for the new one
            if logArticles:
              try:
                siteLog = oldLog[section][site["url"]]
              except:
                siteLog = []
              newLog[section][site["url"]] = []

            # Parse Feed
            for _ in range(5):
              try:
                parsedFeed = feedparser.parse(site["url"])
                if not parsedFeed["bozo"]: break
              except:
                continue

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

                # Check if any of the phrases in the block or allow list appear in 
                # either the title or summary of the article
                allText = "{0} {1}".format(entry["title"].lower(), entry["summary"].lower())
                inBlock = any([x in allText for x in blockList])
                inAllow = any([x in allText for x in allowList])

                # Parse datetime and check if the entry is within the user's set timeframe
                # If there isn't a published date for the item, assume the item was published now and allow it
                # Also check if the user has enabled logs and if the entry is in the log
                # Also Also check if the article should be blocked
                entryDate = datetime.fromtimestamp(timegm(entry["published_parsed"])) if "published_parsed" in entry else datetime.now()
                if (entryDate > siteTimeFrame and 
                  (not logArticles or not entry["title"] in siteLog) and
                  (not inBlock or inAllow)):

                  hasEntries = True
                  siteContent += "<li>"
                  siteContent += entryHeaderHTML.format(entry["link"], entry["title"])
                  if siteFullText:
                    if "<img" in entry["summary"]:
                      entry["summary"] = '<img style="max-width: 100%"'.join(entry["summary"].split("<img"))
                    siteContent += entryContentHTML.format(entry["summary"])
                  siteContent += "</li>"

                # If logs are enabled, add the current entry to the log
                if logArticles:
                  newLog[section][site["url"]].append(entry["title"])
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

    if len(content) == 0:
      content += "<h1>You're all caught up!</h1>"

    # Add content to email message   
    msg.set_content(MIMEText(content, "html"))

    # Create SMTP connection
    s = smtplib.SMTP(feed["settings"]["smtp server"], feed["settings"]["smtp port"])
    s.starttls()
    s.login(feed["settings"]["email address"], feed["settings"]["email password"])

    # Send email
    s.send_message(msg)
    s.quit()

    # Save the new log to the log directory
    if logArticles:
      os.makedirs(articleLogDir, exist_ok=True)
      with open(os.path.join(articleLogDir, filename), "w") as logFile:
        logFile.truncate(0)
        json.dump(newLog, logFile)
