import nose
from nose.tools import *
import urllib2

from portal.feed import *
from processor.nipl import *
from utils.utils import *

class TestNipl:

  content = """type=video
name=Cosmopolis HD
thumb=http://ia.media-imdb.com/images/M/MV5BMTY1NjI0MDYyNV5BMl5BanBnXkFtZTcwNDIzMDEyOA@@._V1_SX500_SY999_.jpg
date=2013-02-12
URL=http://movreel.com/iugst07me2j8
processor=http://scrape.navixtreme.com/cgi-bin/boseman/Processors/movreel
player=default
rating=-1.00
description=Riding across Manhattan in a stretch limo in order to get a haircut, a 28-year-old billionaire asset manager's day devolves into an odyssey with a cast of characters that start to tear his world apart./description
"""

  def video_feed_item_has_required_attributes_test(self):

    item = FeedItem(self.content)

    assert item is not None
    # assert_equal(item.type, 'video')
    # assert_equal(item.name, 'The Bourne Legacy 2012 720P')
    # assert_equal(item.date, '2013-02-08')
    # assert_equal(item.path, 'http://180upload.com/k756ufzu1078')
    # assert_equal(item.processor, 'http://www.navixtreme.com/proc/180upload')
    # assert_equal(item.player, 'default')
    # assert_equal(item.rating, '-1.00')

  def nipl_test(self):

    app = FakeApp()
    item = FeedItem(self.content)

    #phase 1 retreive processor data
    url = "".join([item.processor, '?url=', urllib.quote_plus(item.path), '&phase=0'])
    Log(app, 'NAVI-X: Get Processor - ' + url)
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
        Log(app, traceback.format_exc() )
        results = []

    if len(results) > 0:
        vars = ["".join(['v', str(i+1),'=', urllib.quote_plus(value), '&']) for i, value in enumerate(results)]
        url = "".join([item.processor, '?', "&".join(vars) ])
        rawdata = urlopen(app, str(url), {'cookie':'version=1.'+str(app.navi_sub_version)+'; platform=plexapp'})
        try: path = rawdata['content'].readline()
        except: path = ''
        rawdata['content'].close()

        Log(app, 'NAVI-X PROCESS: Path - ' + path)

        item.setVar('path', path)
        return item
    else: return item

class FakeApp:

  debug = True
  url_useragent = ''
  navi_version = 1
  navi_sub_version = 1
  storage = None
  url_open_timeout = 10000

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


