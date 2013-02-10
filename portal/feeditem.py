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

  description = ""
  icon = None
  thumb = None
  name = ""
  url = ""
  type = None
  date = ""

  def __init__(self, content):

    self.content = content

    self.type = re.search(self.regt, content, re.M).group(1)
    self.name = re.search(self.regn, content, re.M).group(1)
    self.url = re.search(self.regu, content, re.M).group(1)

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

    date = re.search(self.regd, content, re.M)
    if date is not None:
      self.date = date.group(1)
