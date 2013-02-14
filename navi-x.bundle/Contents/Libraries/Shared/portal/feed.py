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

    title = re.search(self.regt, content, re.M)
    if title is not None:
      self.title = title.group(1)

    version = re.search(self.regv, content, re.M)
    if version is not None:
      self.version = version.group(1)

    logo = re.search(self.regl, content, re.M)
    if logo is not None:
      self.logo = logo.group(1)

    background = re.search(self.regb, content, re.M)
    if background is not None:
      self.background = background.group(1)

    reg = "^type="

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
