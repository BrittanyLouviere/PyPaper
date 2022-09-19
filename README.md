# PyPaper
 
A self hosted python script to compile and send RSS and ATOM feeds to your email inbox.

## Dependencies:
- Python 3
- [feedparser](https://pypi.org/project/feedparser/)
  - run `pip install feedparser`
- Something like cronjob to run the script at set times

## Feed JSON Notes
The JSON should be set up like the following:
```json
{
  "settings" : {
    "required settings keys" : "see table below"
  },
  "feeds" : {
    "Feed Group Heading" : [
      {
        "required site keys" : "see table below"
      }
    ]
  }
}
```

See the provided `exampleFeed.json` in the `Feeds` folder for a working example.

Settings Keys  | Value type | Required? | Description
---------------|------------|-----------|----------------------------------------------------
smtp server    | string     | yes       | This is specific to the email service you are using.
smtp port      | int        | yes       | This is specific to the email service you are using.
email address  | string     | yes       | The email address that will both send and recieve the feed email.
email password | string     | yes       | IT IS NOT RECOMENDED TO USE YOUR NORMAL PASSWORD. Most email services ofer an "app password" that apps can use to interact with and access you email.
max posts      | int        | no        | Specifies the maximum amount of posts that should be shown from each feed. Defaults to 5 if not specified.
full text      | boolean    | no        | Defaults to false. If set to false, only each posts' title will be shown. If set to true, the summary content will also be shown. Some feeds may only provide a snippet of the content instead of the full text (especially news sites that require a subscription).
time frame     | string     | no        | In the format of "hh:mm". If a post from any rss feed is older than the secified time, it will be skipped. For example: if the value is "3:15" then any posts that were published more than 3 hours and 15 minutes ago are skipped.

Site Keys      | Value type | Required? | Description
---------------|------------|-----------|----------------------------------------------------
title          | string     | no        | If a title is specified, it is used as the name of the site in the feed email rather than the title specified in the feed's header.
url            | string     | yes       | The url that is used to grab the rss feed. This url MUST be an RSS or ATOM formated webpage.
alternate url  | string     | no        | If this is specified, this url is used to form the hyperlink to the site in the email instead of the one specified in the feed's header.
max posts      | int        | no        | See "max posts" in the settings key table. This will override the global max posts for this site.
full text      | boolean    | no        | See "full text" in the settings key table. This will override the global "full text" for this site.
time frame     | string     | no        | See "time frame" in the settings key table. This will override the global time frame for this site.
