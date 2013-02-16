import urllib

import socket
import urllib2

try: import cStringIO as StringIO
except: import StringIO

from portal.feed import *
from processor.nipl import *

####################################################################################################

MAIN_URL = 'http://www.navixtreme.com/playlists/med_port.plx'
TITLE    = L('Title')
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'
DEBUG    = True

####################################################################################################
def Start():

  ObjectContainer.title1 = TITLE
  ObjectContainer.art = R(ART)
  DirectoryObject.thumb = R(ICON)
  NextPageObject.thumb = R(ICON)
  VideoClipObject.thumb = R(ICON)

  HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler('/video/navix', TITLE, art=ART, thumb=ICON)
def MainMenu():

  return Menu(title=None, url=MAIN_URL)

####################################################################################################
@route('/video/navix/menu')
def Menu(title, url):

  oc = ObjectContainer(title2=title)
  feed = GetFeed(url)

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

    if item.type == 'video':
      oc.add(CreateMovieObject(
        url = item.path,
        processor = item.processor,
        title = item.name,
        summary = item.description
      ))
    elif item.type == 'playlist':
      oc.add(DirectoryObject(
        key = Callback(SubMenu, title=item.name, url=item.path),
        title = item.name,
        summary = item.description,
        thumb = thumb,
        art = art
      ))
    else:
      continue

  return oc

####################################################################################################
def CreateMovieObject(url, processor, title, summary, include_container=False):

  movie_obj = MovieObject(
    key = Callback(CreateMovieObject, url=url, processor=processor, title=title, summary=summary, include_container=True),
    rating_key = url,
    title = title,
    summary = summary,
    items = [
      MediaObject(
        parts = [
          PartObject(
            key = Callback(PlayVideo, url=url, processor=processor)
          )
        ],
        container = Container.MP4,
        video_codec = VideoCodec.H264,
        video_resolution = 'sd',
        audio_codec = AudioCodec.AAC,
        audio_channels = 2,
        optimized_for_streaming = True
      )
    ]
  )

  if include_container:
    return ObjectContainer(objects=[movie_obj])
  else:
    return movie_obj

####################################################################################################
def PlayVideo(url, processor):

  #i think callback can only pass on primitives, therefore we reconstruct the object here
  item = FeedItem('')
  item.path = url
  item.processor = processor

  Log('start %s' % url)
  Log('process with %s' % processor)

  app = FakeApp()

  #phase 1 retreive processor data
  url = '%s?url=%s&phase=0' % (processor, String.Quote(url, usePlus=True))
  Log('NAVI-X: Get Processor for: %s' % url)

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

  result = None
  if datalist[0] == 'v2':
    nipl = NIPL(app, item, 0, datalist, Log)
    result = nipl.process()

  if result is not None:
    return Redirect(result.playurl)
  else:
    raise Ex.MediaNotAvailable

####################################################################################################
def GetFeed(url):

  Log("requesting url: %s" % url.strip())
  try:
    playlist = HTTP.Request(url.strip(), timeout=60).content
  except:
    playlist = ""
    Log("error fetching playlist")

  return Feed(playlist)

####################################################################################################
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
