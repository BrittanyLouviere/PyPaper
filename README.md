# PyPaper
 
A self hosted python script to compile and send RSS and ATOM feeds to your email inbox.

## Dependencies:
- Python 3
- [feedparser](https://pypi.org/project/feedparser/)
  - run `pip install feedparser`
- Something like cronjob to run the script at set times

## Feed JSON Notes
- For simplicity, this script sends the email from and to the same email address
- Most email clients will require you to use an "app passowrd" instead of you're actual password
- The "time frame" value is optional. If set, it will limit shown entries to those within that time frame.
  - EX: If "time frame" is set to "12:30" then only entries that were published in the last 12 hours and 30 minutes will be shown
- The "title" key is optional if you wish to customize the name of an RSS/ATOM feed
- Set the "full text" value to true if you want the content of the feed item in the email instead of just the title
  - Some feeds may only provide a snippet of the content instead of the full text
