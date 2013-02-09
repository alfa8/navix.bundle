import nose
import urllib2

from portal.feed import *

class TestPortal:

  main = "http://www.navixtreme.com/playlists/med_port.plx"
  content = None
  feed = None

  @classmethod
  def setup_class(self):
    self.content = urllib2.urlopen(self.main).read()
    self.feed = feed = Feed(self.content)

  def portal_can_be_reached_test(self):
    print '%d items' % len(self.feed.items)
    assert(len(self.feed.items) > 0)

  def portal_has_a_version_number_test(self):
    print self.feed.version
    assert(self.feed.version > 0)

  def portal_has_a_title_test(self):
    print self.feed.title
    assert(self.feed.title is not None)

  def portal_has_a_logo_image_test(self):
    print self.feed.logo
    assert(self.feed.logo is not None)

  def portal_has_a_background_image_test(self):
    print self.feed.background
    assert(self.feed.background is not None)

  def all_main_items_have_type_test(self):
    for item in self.feed.items:
      print 'type = %s' % item.type
      assert(item.type != '')

  def all_main_items_have_name_test(self):
    for item in self.feed.items:
      print 'name = %s' % item.name
      assert(item.name != '')

  def all_main_items_have_url_test(self):
    for item in self.feed.items:
      print 'url = %s' % item.url
      assert(item.url != '')
