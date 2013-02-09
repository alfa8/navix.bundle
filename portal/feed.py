import re
from feeditem import *

class Feed:

  regv = "(?!#)version=(.*)"
  regt = "(?!#)title=(.*)"
  regl = "(?!#)logo=(.*)"
  regb = "(?!#)background=(.*)"

  version = 0
  logo = None
  background = None
  title = None
  items = None

  def __init__(self,content):

    self.items = []
    self.version = re.search(self.regv, content,re.M).group(1)
    self.title = re.search(self.regt, content,re.M).group(1)
    self.logo = re.search(self.regl, content,re.M).group(1)
    self.background = re.search(self.regb, content,re.M).group(1)

    reg = "^type="

    matches = re.finditer(reg, content, re.M)
    if matches == None:
      print "none found"
    else:
      lastpos = 0
      for match in matches:
        if lastpos > 0:
          item = FeedItem(content[lastpos:match.start()])
          self.items.append(item)
        lastpos = match.start()

      item = FeedItem(content[lastpos:len(content)])
      self.items.append(item)
