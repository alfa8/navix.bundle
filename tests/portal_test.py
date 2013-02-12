import nose
import urllib2

from portal.feed import *

class TestPortal:

  main = "http://www.navixtreme.com/playlists/med_port.plx"
  feed = None

  @classmethod
  def setup_class(self):
    content = urllib2.urlopen(self.main).read()
    self.feed = Feed(content)

  def can_be_reached_test(self):
    print '%d items' % len(self.feed.items)
    assert len(self.feed.items) > 0

  def has_a_version_number_test(self):
    print self.feed.version
    assert self.feed.version > 0

  def has_a_title_test(self):
    print self.feed.title
    assert self.feed.title is not None

  def has_a_logo_image_test(self):
    print self.feed.logo
    assert self.feed.logo is not None

  def has_a_background_image_test(self):
    print self.feed.background
    assert self.feed.background is not None

  def main_items_have_type_test(self):
    for item in self.feed.items:
      print 'type = %s' % item.type
      assert item.type != ''

  def main_items_have_name_test(self):
    for item in self.feed.items:
      print 'name = %s' % item.name
      assert item.name != ''

  def main_items_have_path_test(self):
    for item in self.feed.items:
      print 'url = %s' % item.path
      assert item.path != ''
