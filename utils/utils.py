import socket
import urllib2

try: import cStringIO as StringIO
except: import StringIO

def Log(app, string):
  print string

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
