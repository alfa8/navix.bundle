import urllib
import socket
import urllib2

try: import cStringIO as StringIO
except: import StringIO

from portal.feed import *
from processor.nipl import *

####################################################################################################

MAIN_URL        = 'http://www.navixtreme.com/playlists/med_port.plx'
TITLE           = L('Title')
ART             = 'art-default.jpg'
ICON            = 'icon-default.png'
DEBUG           = True
CACHE_NAME      = 'NAVIX_CACHE'
CACHE_MAX_ITEMS = 100
CACHE_MAX_BYTES = 1 * 1024 * 1024

####################################################################################################

feed_regex = {
  'version' : '(?!#)version=(.*)',
  'title' : '(?!#)title=(.*)',
  'logo' : '(?!#)logo=(.*)',
  'background' : '(?!#)background=(.*)'
 }

feeditem_regex = {
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
def Start():

  ObjectContainer.title1 = TITLE
  ObjectContainer.art = R(ART)
  DirectoryObject.thumb = R(ICON)
  NextPageObject.thumb = R(ICON)
  VideoClipObject.thumb = R(ICON)

  HTTP.CacheTime = CACHE_1HOUR

  PruneCache(CACHE_MAX_BYTES, CACHE_MAX_ITEMS)

####################################################################################################
@handler('/video/navix', TITLE, art=ART, thumb=ICON)
def MainMenu():

  return Menu(title=None, url=MAIN_URL)

####################################################################################################
@route('/video/navix/menu')
def Menu(title, url):

  oc = ObjectContainer(title2=unicode(title))
  feed = CreatePlaylist(url)

  for item in feed['items']:

    if 'thumb' in item and item['thumb'].startswith('http://'):
      thumb = item['thumb']
    else:
      thumb = R(ICON)

    if 'background' in item and item['background'].startswith('http://'):
      art = item['background']
    elif 'background' in feed and feed['background'].startswith('http://'):
      art = feed['background']
    else:
      art = R(ART)

    if item['type'] == 'video':
      if item['processor'] == '':
        oc.add(CreateVideoClipObject(
          url = item['stream'],
          clip = item['playpath'],
          swf_url = item['swfplayer'],
          pageurl = item['pageurl'],
          timeout = item['timeout'],
          live = item['live'],
          title = item['name'],
          summary = item['description'],
          thumb = thumb,
          art = art
          ))
      else:
        oc.add(CreateMovieObject(
          item = item,
          thumb = thumb,
          art = art
        ))
    elif item['type'] == 'playlist':
      oc.add(DirectoryObject(
        key = Callback(Menu, title=item['name'], url=item['url']),
        title = item['name'],
        summary = item['description'],
        thumb = thumb,
        art = art
      ))
    else:
      continue

  return oc

####################################################################################################
@route('/video/navix/createmovieobject', item=dict)
def CreateMovieObject(item, thumb, art, include_container=False):

  movie_obj = MovieObject(
    key = Callback(CreateMovieObject, item=item, thumb=thumb, art=art, include_container=True),
    rating_key = item['url'],
    title = item['name'],
    summary = item['description'],
    thumb = thumb,
    art = art,
    items = [
      MediaObject(
        parts = [
          PartObject(
            key = Callback(PlayVideo, item=item)
          )
        ],
        container = Container.MP4,
        video_codec = VideoCodec.H264,
        audio_codec = AudioCodec.AAC,
        audio_channels = 2
      )
    ]
  )

  if include_container:
    return ObjectContainer(objects=[movie_obj])
  else:
    return movie_obj

####################################################################################################
@indirect
@route('video/navix/playvideo', item=dict)
def PlayVideo(item):

  result = Processor(item)

  if result is not None:
    LogDebug('redirecting to: %s' % result['playurl'])
    return IndirectResponse(MovieObject, key=result['playurl'])
  else:
    raise Ex.MediaNotAvailable

####################################################################################################
def Processor(item):

  cache_key = Hash.MD5(item['url'])
  result = GetCacheItem(cache_key)

  if result is not None:
    LogDebug('the cache returned a result, skipping processor...')
    return result

  LogDebug('url to process %s' % item['url'])
  LogDebug('will be processed with %s' % item['processor'])

  app = FakeApp()

  #phase 1 retreive processor data
  url = '%s?url=%s&phase=0' % (item['processor'], String.Quote(item['url'], usePlus=True))
  htmRaw = GetProcessor(url)
  htmRaw = re.sub('(?m)\r[#].+|\n[#].+|^\s+|\s+$', '\r\n', htmRaw)    #remove comments and tabs
  htmRaw = re.sub('[\r\n]+', '\n', htmRaw)                            #remove empty lines
  datalist = htmRaw.replace('\t','').split('\n')

  result = None
  if datalist[0] == 'v2':
    nipl = NIPL(app, item, 0, datalist, LogDebug)
    result = nipl.process()

    if result is not None:
      SetCacheItem(cache_key, result)

  return result

####################################################################################################
@route('/video/navix/createvideoclipobject')
def CreateVideoClipObject(url, clip, swf_url, pageurl, timeout, live, title, summary, thumb, art, include_container=False):

  clip_obj = VideoClipObject(
    key = Callback(CreateVideoClipObject, url=url, clip=clip, swf_url=swf_url, pageurl=pageurl, timeout=timeout, live=live, title=title, summary=summary, thumb=thumb, art=art, include_container=True),
    rating_key = title,
    title = title,
    summary = summary,
    thumb = thumb,
    art = art,
    items = [
      MediaObject(
        parts = [
          PartObject(
            key = Callback(PlayStream, url=url, clip=clip, swf_url=swf_url, pageurl=pageurl, timeout=timeout, live=live)
          )
        ],
        optimized_for_streaming = True
      )
    ]
  )

  if include_container:
    return ObjectContainer(objects=[clip_obj])
  else:
    return clip_obj

####################################################################################################
@indirect
@route('video/navix/playstream')
def PlayStream(url, clip, swf_url, pageurl, timeout, live):

  LogDebug('Starting stream...')
  LogDebug('*' * 100)
  LogDebug('url: %s' % url)
  LogDebug('clip: %s' % clip)
  LogDebug('swf_url: %s' % swf_url)
  LogDebug('pageurl: %s' % pageurl)
  LogDebug('timeout: %s' % timeout)
  LogDebug('live: %s' % live)
  LogDebug('*' * 100)

  if (url.startswith('http') or url.startswith('https')):
    return IndirectResponse(VideoClipObject, key=HTTPLiveStreamURL(url=url))

  if clip is not None:
    if clip[-4:] == '.mp4':
      clip = 'MP4:' + clip[:-4]
    else:
      clip = clip.replace('.flv', '')

  return IndirectResponse(VideoClipObject, key=RTMPVideoURL(url=url, clip=clip, swf_url=swf_url, live=live, pageurl=pageurl))

####################################################################################################
def GetFeed(url):

  LogDebug("requesting url: %s" % url.strip())
  try:
    playlist = HTTP.Request(url.strip(), encoding='utf-8', timeout=60).content
  except:
    playlist = ""
    LogDebug("error fetching playlist")

  return Feed(playlist)

####################################################################################################
def GetProcessor(url):

  LogDebug("requesting url: %s" % url.strip())
  try:
    processor = HTTP.Request(url.strip(), encoding='utf-8', timeout=60).content
  except:
    processor = ""
    LogDebug("error fetching processor")

  return processor

####################################################################################################
def SetCacheItem(key, item, duration_seconds = 7200):

  LogDebug('caching item with key %s ' % key)

  cache = Cache[CACHE_NAME]
  cache_item = cache[key]

  cache_item.data = item

  LogDebug('cache count: %s' % cache.item_count)

####################################################################################################
def GetCacheItem(key):

  LogDebug('getting cache item with key: %s' % key)

  cache = Cache[CACHE_NAME]
  cache_item = cache[key]

  LogDebug('cache_item expired: %s' % cache_item.expired)
  LogDebug('cache_item modified_at %s' % cache_item.modified_at)

  #todo; get the expired flag working...this is buggy...
  if cache_item.expired:
    LogDebug('not found...')
    return cache_item.data
  else:
    LogDebug('cache hit...')
    return cache_item.data

####################################################################################################
def PruneCache(max_bytes, max_items):

  LogDebug('pruning cache')

  cache = Cache[CACHE_NAME]
  cache.trim(max_bytes, max_items)

####################################################################################################
def LogDebug(message):
  Log.Debug('*[navix]* %s' % message)

####################################################################################################
def CreatePlaylist(url):

  LogDebug('creating playlist from url: %s' % url.strip())

  playlist = {}

  try:
    content = HTTP.Request(url.strip(), encoding='utf-8', timeout=60).content
  except:
    LogDebug("error fetching playlist")
    return playlist

  for key, regex in feed_regex.items():
    match = re.search(regex, content, re.M)
    if match is not None:
      playlist[key] = match.group(1)
    else:
      playlist[key] = ''

  #todo: filter out color tags
  #todo: fix encoding issue

  playlist['items'] = CreatePlaylistItems(content)

  return playlist

####################################################################################################
def CreatePlaylistItems(content):

  LogDebug('creating playlist items')

  playlist_items = []

  type_regex = "^type="
  unwanted_playlists = ('Utilities', 'Search')

  matches = re.finditer(type_regex, content, re.M)
  if matches == None:
    LogDebug('no playlist items found')
  else:
    lastpos = 0
    for match in matches:
      if lastpos > 0:
        text = content[lastpos:match.start()];
        if not any(unwanted in text for unwanted in unwanted_playlists):
          item = CreatePlaylistItem(text)
          playlist_items.append(item)
      lastpos = match.start()

    text = content[lastpos:len(content)]
    if not any(unwanted in text for unwanted in unwanted_playlists):
      item = CreatePlaylistItem(text)
      playlist_items.append(item)

  return playlist_items

####################################################################################################
def CreatePlaylistItem(content):

  playlist_item = {}

  for key, regex in feeditem_regex.items():
    match = re.search(regex, content, re.M)
    if match is not None:
      playlist_item[key] = match.group(1)
    else:
      playlist_item[key] = ''

  playlist_item['player'] = 'default'
  playlist_item['error'] = ''

  #todo: filter out color tags
  #todo: fix encoding issue
  #todo: fix booleans

  return playlist_item

####################################################################################################
def any(iterable):
    for element in iterable:
        if element:
            return True
    return False

####################################################################################################
# @route('/video/navix/createscraper')
# def CreateScraper(url, processor, title, summary, thumb, art, include_container=False):

#   clip_obj = VideoClipObject(
#     key = Callback(CreateScraper, url=url, processor=processor, title=title, summary=summary, thumb=thumb, art=art, include_container=True),
#     rating_key = url,
#     title = title,
#     summary = summary,
#     thumb = thumb,
#     art = art,
#     items = [
#       MediaObject(
#         parts = [
#           PartObject(
#             key = Callback(PlayScraper, url=url, processor=processor)
#           )
#         ],
#         optimized_for_streaming = True
#       )
#     ]
#   )

#   if include_container:
#     return ObjectContainer(objects=[clip_obj])
#   else:
#     return clip_obj

# ####################################################################################################
# @indirect
# @route('video/navix/playscraper')
# def PlayScraper(item):

#   result = Processor(item)

#   if result is not None:
#     return IndirectResponse(VideoClipObject, key=Callback(PlayStream(url=result['playurl'], clip=result['playpath'], swf_url=result['swfplayer'], pageurl=result['pageurl'], timeout=result['timeout'], live=result['live'])))
#   else:
#     raise Ex.MediaNotAvailable

####################################################################################################
class FakeApp:

  debug = True
  url_useragent = ''
  navi_version = 1
  navi_sub_version = 1
  storage = None
  url_open_timeout = 120

  def __init__(self):
    self.storage = FakeStorage()

class FakeStorage:

    stuff = None

    def __init__(self):
      self.stuff = dict()

    def get(self, id, **kwargs):
      item = None
      try:
        LogDebug('============ getting item %s' % id)
        item = self.stuff[id]
      except Exception, e:
        return item

      return item

    def set(self, id, data, **kwargs):
        LogDebug('============ setting item %s' % id)
        self.stuff[id] = data
