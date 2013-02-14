import urllib

import socket
import urllib2

try: import cStringIO as StringIO
except: import StringIO

from portal.feed import *
from processor.nipl import *

####################################################################################################

VIDEO_PREFIX   = "/video/navi-x-plex"
MAIN_URL       = "http://www.navixtreme.com/playlists/med_port.plx"
TITLE          = L('Title')
ART            = 'art-default.jpg'
ICON           = 'icon-default.png'
DEBUG          = True

####################################################################################################

def Start():

  Plugin.AddViewGroup("InfoList", viewMode = "InfoList", mediaType = "items")
  Plugin.AddViewGroup("List", viewMode = "List", mediaType = "items")

  ObjectContainer.title1 = TITLE
  ObjectContainer.art = R(ART)
  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  NextPageObject.thumb = R(ICON)
  NextPageObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)

  #Causes issues with retrieval...must be xml blah blah... suckie suckie...
  #HTTP.CacheTime = CACHE_1HOUR

@handler(VIDEO_PREFIX, TITLE, art = ART, thumb = ICON)
def MainMenu():

  oc = ObjectContainer(view_group = "InfoList")

  content = GetContents(MAIN_URL)
  feed = Feed(content)

  for item in feed.items:

    if item.thumb != None:
      thumb = item.thumb
    else:
      thumb = R(ICON)
    if item.icon != None:
      art = item.icon
    elif feed.background != None:
      art = feed.background
    else:
      art = R(ART)

    oc.add(DirectoryObject(key = Callback(SubMenu, title = item.name, url = item.path), title = item.name, tagline = '', summary = item.description, thumb = item.thumb, art = R(ART)))

  return oc

@route('/video/navi-x-plex/submenu')
def SubMenu(title, url):

  oc = ObjectContainer(title2 = title, view_group = "List")

  content = GetContents(url)
  feed = Feed(content)

  for item in feed.items:

    if item.thumb != None:
      thumb = item.thumb
    else:
      thumb = R(ICON)
    if item.icon != None:
      art = item.icon
    elif feed.background != None:
      art = feed.background
    else:
      art = R(ART)

    if item.type == "video":
      oc.add(MovieObject(key = Callback(PressPlayOnTape, url = item.path, processor = item.processor), rating_key = item.name, title = item.name, tagline = '', summary = item.description, thumb = thumb, art = art))
    elif item.type == 'playlist':
      oc.add(DirectoryObject(key = Callback(SubMenu, title = item.name, url = item.path), title = item.name, tagline = '', summary = item.description, thumb = thumb, art = art))
    else:
      continue

  return oc

@route('/video/navi-x-plex/submenu/press-play-on-tape')
def PressPlayOnTape(url, processor):
  #i think callback can only pass on primitives, therefore we reconstruct the object here
  item = FeedItem('')
  item.path = url
  item.processor = processor

  Log('start %s' % item.path)
  Log('process with %s' % item.processor)

  app = FakeApp()

  #phase 1 retreive processor data
  url = "".join([item.processor, '?url=', urllib.quote_plus(item.path), '&phase=0'])
  Log('NAVI-X: Get Processor for: ' + item.path)
  data = app.storage.get(url)
  if data:
      datalist = data
  else:
      #phase 1 retreive processor data
      rawdata = urlopen(app, str(url), {'cookie':'version=1.'+str(app.navi_sub_version)+'; platform=plexapp', 'action':'read'})
      htmRaw = rawdata['content']
      htmRaw = re.sub('(?m)\r[#].+|\n[#].+|^\s+|\s+$', '\r\n', htmRaw)    #remove comments and tabs
      htmRaw = re.sub('[\r\n]+', '\n', htmRaw)                            #remove empty lines
      datalist = htmRaw.replace('\t','').split('\n')

  if datalist[0] == 'v2':
      nipl = NIPL(app, item, 0, datalist)
      return nipl.process()
  elif 'http' in datalist[0]:
      return self.PROCESS(item, datalist)

  def PROCESS(self, item, datalist):
    url = datalist[0]
    regex = datalist[1]

    rawpage = urlopen(app, url, {'action':'read'})
    try: results = re.compile(regex).findall(rawpage['content'])
    except:
        Log(traceback.format_exc())
        results = []

    if len(results) > 0:
        vars = ["".join(['v', str(i+1),'=', urllib.quote_plus(value), '&']) for i, value in enumerate(results)]
        url = "".join([item.processor, '?', "&".join(vars) ])
        rawdata = urlopen(app, str(url), {'cookie':'version=1.'+str(app.navi_sub_version)+'; platform=plexapp'})
        try: path = rawdata['content'].readline()
        except: path = ''
        rawdata['content'].close()

        Log('NAVI-X PROCESS: Path - ' + path)

        item.setVar('path', path)
        return item
    else: return item


def GetContents(url):
  Log("requesting url: " + url.strip())
  playlist = ""
  try:
    playlist = HTTP.Request(url.strip())
  except:
    Log("error fetching playlist")
  #Log(playlist)
  return str(playlist)

class FakeApp:

  debug = True
  url_useragent = ''
  navi_version = 1
  navi_sub_version = 1
  storage = None
  url_open_timeout = 100000

  def __init__(self):
    self.storage = FakeStorage()

class FakeStorage:

    stuff = None

    def __init__(self):
      self.stuff = dict()

    def get(self, id, **kwargs):
      item = None
      try:
        print '============ getting item %s' % id
        item = self.stuff[id]
      except Exception, e:
        return item

      return item


    def set(self, id, data, **kwargs):
        print '============ setting item %s' % id
        self.stuff[id] = data

def urlopen(app, url, args={}):
  rdefaults={
      'agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4',
      'referer': '',
      'cookie': '',
      'action':'',
      'method': 'get',
      'postdata': '',
      'headers': {},
  }
  Log(url)
  for ke in rdefaults:
      try:
          args[ke]
      except KeyError:
          args[ke]=rdefaults[ke]

  socket.setdefaulttimeout(float(app.url_open_timeout))

  try:
      hdr = {'User-Agent':args['agent'], 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Referer':args['referer'], 'Cookie':args['cookie']}
  except:
      print "Unexpected error:", sys.exc_info()[0]

  for ke in args['headers']:
      try:
          hdr[ke] = args['headers'][ke]
      except:
          print "Unexpected error:", sys.exc_info()[0]

  result ={
      'headers':'',
      'geturl':url,
      'cookies':'',
      'content':''
      }

  try:
      cookieprocessor = urllib2.HTTPCookieProcessor()
      opener = urllib2.build_opener(cookieprocessor)
      urllib2.install_opener(opener)

      if args['method'] == 'get':
          req = urllib2.Request(url=url, headers = hdr)
      else:
          req = urllib2.Request(url, args['postdata'], hdr)

      response = urllib2.urlopen(req)

      cookies={}
      for c in cookieprocessor.cookiejar:
          cookies[c.name]=c.value

      result['headers'] = response.info()
      result['geturl'] = response.geturl()
      result['cookies'] = cookies
  except urllib2.URLError, e:
      print e.reason
      #app.gui.ShowDialogNotification('Error: %s' % e.reason)
      response = StringIO.StringIO('')
  except:
      Log(app, traceback.format_exc() )
      response = StringIO.StringIO('')

  if args['action'] == 'read':
      result['content'] = response.read()
      response.close()
  else:
      result['content'] = response
  return result
