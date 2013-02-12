import nose
import urllib2

from portal.feed import *

class TestPortalPlaylists:

  main = "http://www.navixtreme.com/playlists/med_port.plx"
  feed = None

  @classmethod
  def setup_class(self):
    content = urllib2.urlopen(self.main).read()
    self.feed = Feed(content)

  def have_required_attributes_test(self):
    for item in self.feed.items:
      content = urllib2.urlopen(item.path).read()
      feed = Feed(content)
      yield self.check_single_feed, feed

  def check_single_feed(self, feed):
    assert feed is not None
    assert feed.items is not None
    assert len(feed.items) > 0
    for item in feed.items:
      assert item.type != ''
      assert item.name != ''
      assert item.path != ''
