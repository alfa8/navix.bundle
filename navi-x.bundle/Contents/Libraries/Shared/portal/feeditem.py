import re

class FeedItem:

  regt = "type=(.*)"
  regn = "(?!#)name=(.*)"
  regu = "(?!#)URL=(.*)"
  regd = "(?!#)description=(.*)"
  regi = "(?!#)icon=(.*)"
  regth = "(?!#)thumb=(.*)"
  regdt = "(?!#)date=(.*)"
  regp = "(?!#)processor=(.*)"
  regplayer = "(?!#)player=(.*)"
  regrating = "(?!#)rating=(.*)"

  description = ""
  icon = None
  thumb = None
  name = ""
  type = None
  date = ""
  path = ""
  swfplayer = ""
  playpath = ""
  error = ""
  pageurl = ""
  v1 = ''
  v2 = ''
  live = ''
  player = ''
  processor = ''

  def __init__(self, content):

    #todo: add parsing code for swf urls
    #example: rtmp://204.45.66.186/ctv playpath=tom swfUrl=http://www.canaistv.net/swf/player.swf pageUrl=http://www.canaistv.net/tvamigos/tom&jerry.html live=1
    #needs to be split in properties
    self.live = ''
    self.content = content

    if self.content != '':

      type = re.search(self.regt, content, re.M)
      if type is not None:
        self.type = type.group(1)

      name = re.search(self.regn, content, re.M)
      if name is not None:
        self.name = name.group(1)

      path = re.search(self.regu, content, re.M)
      if path is not None:
        self.path = path.group(1)

      processor = re.search(self.regp, content, re.M)
      if processor is not None:
        self.processor = processor.group(1)

      description = re.search(self.regd, content, re.M)
      if description is not None:
        self.description = description.group(1)

      icon = re.search(self.regi, content, re.M)
      if icon is not None:
        self.icon = icon.group(1)

      thumb = re.search(self.regth, content, re.M)
      if thumb is not None:
        self.thumb = thumb.group(1)

      date = re.search(self.regdt, content, re.M)
      if date is not None:
        self.date = date.group(1)

      player = re.search(self.regplayer, content, re.M)
      if player is not None:
        self.player = player.group(1)

      rating = re.search(self.regrating, content, re.M)
      if rating is not None:
        self.rating = rating.group(1)

  def setVar(self, var, value):
    vars(self)[var] = value
