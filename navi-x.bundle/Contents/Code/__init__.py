# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
from feed import *

####################################################################################################

VIDEO_PREFIX = "/video/naviplex"
MAIN_URL       = "http://www.navi-x.org/playlists/med_port.plx"
NAME           = L('Title')
CACHE_INTERVAL = 1800
ART            = 'art-default.jpg'
ICON           = 'icon-default.png'
DEBUG          = True

####################################################################################################

def Start():

    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

def VideoMainMenu():

    dir = MediaContainer(viewGroup="InfoList")
    content = GetContents(MAIN_URL)
    feed = Feed(content)
    for item in feed.items:
      if item.thumb != None:
        thumb = item.thumb
      else:
        thumb = R(ICON)
      if item.icon != None:
        art = item.icon
      else:
        art = R(ART)
      dir.Append(
          Function(
            DirectoryItem(
              ReadPage,
              item.name,
              subtitle=item.description,
              summary=item.description,
              thumb=item.thumb,
              art=R(ART)
            ),
            url=item.URL
        )
      )

    return dir

# ****************************************************
# by wrapping the read for the url, i abstract the method
# which means we can easily switch to the plex framework method
# or use urllib, or whatever.
# ****************************************************
def GetContents(url):
  Log("requesting url: " + url.strip())
  playlist = ""
  try:
    playlist = HTTP.Request(url.strip())
  except:
    Log("error fetching playlist")
  #Log(playlist)
  return playlist

def ReadPage(sender, url):   
    dir = MediaContainer(title2=sender.itemTitle)
    dir.viewGroup = "InfoList"
    content = GetContents(url)    
    feed = Feed(content)
    for item in feed.items:
      if item.thumb != None:
        thumb = str(item.thumb)
      else:
        thumb = R(ICON)
      if item.icon!=None:
        art = str(item.icon)
      else:
        art=R(ART)
      if item.type=="video":
        #dir.Append(
        #    Function(
        #      WebVideoItem(
        #        ShowVideo,
        #        title=item.name, 
        #        summary=None, 
        #        thumb=item.thumb,
        #        art=art
        #      ),
        #      url=item.URL
        #   )
        #)
        dir.Append(RTMPVideoItem(item.URL, item.processor, title=item.name, summary=item.name, thumb=thumb))
      else:
        dir.Append(
            Function(
              DirectoryItem(
                ReadPage,
                item.name,
                subtitle=item.description,
                summary=item.description,
                thumb=item.thumb,
                art=R(ART)
              ),
              url=item.URL
           )
        )
    return dir

def ShowVideo(sender, url):
  return Redirect(RTMPVideoItem(url))

def CallbackExample(sender,url):

    ## you might want to try making me return a MediaContainer
    ## containing a list of DirectoryItems to see what happens =)

    return MessageContainer(
        "Not implemented",
        "In real life, you'll make more than one callback,\nand you'll do something useful.\nsender.itemTitle=%s" % sender.itemTitle
    )

