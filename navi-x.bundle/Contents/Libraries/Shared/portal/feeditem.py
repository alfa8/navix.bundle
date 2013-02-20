import re

class FeedItem:

  regex = {
    'type' : 'type=(.*)',
    'name' : '(?!#)name=(.*)',
    'url' : '(?!#)URL=(.*)',
    'description' : '(?!#)description=(.*)',
    'icon' : '(?!#)icon=(.*)',
    'thumb' : '(?!#)thumb=(.*)',
    'background' : '(?!#)background=(.*)',
    'date' : '(?!#)date=(.*)',
    'processor' : '(?!#)processor=(.*)',
    'rating' : '(?!#)rating=(.*)',
    'stream' : '(?!#)URL=(?P<stream>(rtmp|http|https)://[^\s]*)',
    'swfplayer' : 'swfUrl=(?P<swf_url>[^\s]*)',
    'playpath' : 'playpath=(?P<playpath>[^\s]*)',
    'swfVfy' : '[Vfy|swfVfy]=(?P<swfVfy>[^\s]*)',
    'pageurl' : 'pageUrl=(?P<pageurl>[^\s]*)',
    'live' : 'live=(?P<live>[^\s]*)',
    'timeout' : 'timeout=(?P<timeout>[^\s\w]*)'
   }

  ####################################################################################################
  def __init__(self, content):

    # begin warning: needed by niple parser, refactor out
    self.agent = ''
    self.app = None
    self.referer = ''
    self.player = 'default'
    # end warning: needed by niple parser, refactor out

    self.content = content
    self.error = None
    self.playurl = '' # the result from scraping

    self.type = ''
    self.name = ''
    self.url = '' # the url to scrape
    self.processor = '' # the processor to scrape with
    self.description = ''
    self.icon = ''
    self.thumb = ''
    self.background = ''
    self.date = ''
    self.rating = 0
    self.stream = ''
    self.swfplayer = ''
    self.playpath = ''
    self.swfVfy = False
    self.pageurl = ''
    self.live = False
    self.timeout = 0

    for var in vars(self):
      if var in self.regex:
        result = re.search(self.regex[var], content, re.M)
        if result is not None:
          self.setVar(var, result.group(1))

    if self.name != '':
      name = re.sub('\[COLOR=[^\]]+\]|\[/COLOR\]', '', self.name)
      self.name = unicode(re.sub('\s\s+', ' ', name)).strip()

    if self.description != '':
      description = re.sub('\[COLOR=[^\]]+\]|\[/COLOR\]', '', self.description)
      self.description = unicode(re.sub('\s\s+', ' ', description)).strip()

    if self.swfVfy != '':
      if self.swfVfy == '1' or self.swfVfy == 'true' or self.swfVfy == True:
        self.swfVfy = True
      else:
        self.swfVfy = False

    if self.live != '':
      if self.live == '1' or self.live == 'true' or self.live == True:
        self.live = True
      else:
        self.live = False

  ####################################################################################################
  def setVar(self, var, value):
    vars(self)[var] = value
