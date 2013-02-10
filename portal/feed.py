import re
from feeditem import *

class Feed:

  regv = "(?!#)version=(.*)"
  regt = "(?!#)title=(.*)"
  regl = "(?!#)logo=(.*)"
  regb = "(?!#)background=(.*)"

  unwanted_playlists = ('Utilities', 'Search', 'Site Scrapers')

  version = 0
  logo = None
  background = None
  title = None
  items = None

  def __init__(self, content):

    self.items = []
    self.version = re.search(self.regv, content, re.M).group(1)
    self.title = re.search(self.regt, content, re.M).group(1)
    self.background = re.search(self.regb, content, re.M).group(1)

    logo = re.search(self.regl, content, re.M)
    if logo is not None:
      self.logo = logo.group(1)

    reg = "^type=playlist"

    matches = re.finditer(reg, content, re.M)
    if matches == None:
      print "none found"
    else:
      lastpos = 0
      for match in matches:
        if lastpos > 0:
          text = content[lastpos:match.start()];
          if not any (unwanted in text for unwanted in self.unwanted_playlists):
            item = FeedItem(text)
            self.items.append(item)
        lastpos = match.start()

      text = content[lastpos:len(content)]
      if not any (unwanted in text for unwanted in self.unwanted_playlists):
        item = FeedItem(text)
        self.items.append(item)
