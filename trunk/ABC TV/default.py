 
#abctv.py Version 0.1
#Author Voightkampff voightkampff@gmail.com
#Based on the TWiT script by Greg Chrystall greg@chrystall.co.nz
#Enjoy, email bugs to above address.
#
#
#
#Note this is the first release, heavily copied from other XBMC Scripts.

import xml.dom.minidom, urllib, os, os.path, xbmc, xbmcgui, string, traceback, time

ACTION_MOVE_LEFT        = 1	
ACTION_MOVE_RIGHT       = 2
ACTION_MOVE_UP          = 3
ACTION_MOVE_DOWN        = 4
ACTION_PAGE_UP          = 5
ACTION_PAGE_DOWN        = 6
ACTION_SELECT_ITEM      = 7
ACTION_HIGHLIGHT_ITEM   = 8
ACTION_PARENT_DIR       = 9
ACTION_PREVIOUS_MENU    = 10
ACTION_SHOW_INFO        = 11
ACTION_PAUSE            = 12
ACTION_STOP             = 13
ACTION_NEXT_ITEM        = 14
ACTION_PREV_ITEM        = 15

# dialog object for the whole app
dialog = xbmcgui.DialogProgress()

# Setup logging routines
ROOT_DIR = os.getcwd()+'\\'
IMAGE_DIR = ROOT_DIR+'images\\'
DO_LOGGING = True
LOG_FILE_NAME = ROOT_DIR + "abctvLog.txt"

if DO_LOGGING:
	LOG_FILE = open(LOG_FILE_NAME, 'w')

def LOG(message):
	if DO_LOGGING:
		LOG_FILE.write(str(message)+"\n")
		LOG_FILE.flush()

def LOGCLOSE():
	if DO_LOGGING:
		LOG_FILE.close()

itemElements		= ['title','link','pubDate', 'description']
rssFeeds		= {'Sunday Arts' : 'http://abc.net.au/tv/sundayarts/video/sundayarts_mp4.xml',
			'Gardening Australia' : 'http://abc.net.au/gardening/video/gardening_mp4.xml',
			'First Tuesday Book Club' : 'http://abc.net.au/tv/firsttuesday/video/firsttuesday_mp4.xml',
			'Media Watch' : 'http://abc.net.au/mediawatch/vodcast/mediawatch_mp4.xml',
			'The Einstein Factor' : 'http://abc.net.au/einsteinfactor/video/einstein_mp4.xml',
			'The New Inventors' : 'http://abc.net.au/tv/newinventors/video/newinventors_mp4.xml',
			'7.30 Report' : 'http://www.abc.net.au/7.30/xml/730_vodcast_wmv.xml',
			'Dig TV' : 'http://www.abc.net.au/dig/podcast/digtvvid_rss.xml',
			'Good Game' : 'http://abc.net.au/tv/goodgame/video/vodcast/goodgame_mp4.xml',
			'Jtv' : 'http://www.abc.net.au/jtv/vodcast/vodcastMp4.xml',
			'Lateline' : 'http://www.abc.net.au/lateline/xml/ll_vodcast.xml',
			'The Chaser\'s War On Everything' : 'http://abc.net.au/tv/chaser/war/vodcast/chaser_mp4.xml',
			'The Cook and The Chef' : 'http://abc.net.au/tv/cookandchef/video/vodcast/vodcast_mp4.xml'}

class DiggNationViewer(xbmcgui.Window):
	def __init__(self):
		dialog.create("Getting RSS Feeds")
		self.feeds = {}
		self.urlsInOrder = []
		W = self.getWidth()
		H = self.getHeight()
		LOG("Image: " + IMAGE_DIR + 'background.png')
		self.ctrlBackGround = xbmcgui.ControlImage(0, 0, W, H, IMAGE_DIR + 'background.png')
		self.addControl(self.ctrlBackGround)
		self.ctrlLogo = xbmcgui.ControlImage(50, 30, 351, 118, IMAGE_DIR + 'logo.png')
		self.addControl(self.ctrlLogo)
		
		
		self.shows		= xbmcgui.ControlList(40,150,240,365)
		self.itemList		= xbmcgui.ControlList(290,150,370,365,'font13','0xFFFFFFFF')
		
		self.addControl(self.shows)
		self.addControl(self.itemList)
		#Move left and right.
		self.shows.controlRight(self.itemList)
		self.shows.controlLeft(self.itemList)
		self.itemList.controlRight(self.shows)
		self.itemList.controlLeft(self.shows)
		count = 1.0
		for name, url in sorted(rssFeeds.iteritems()):
			progress = int(((count / float(len(rssFeeds))) * 100.0))
			dialog.update(progress, "Getting " + name + " RSS Feed.")
			#self.feeds[name] = FeedItems(url).getData()
			self.shows.addItem(name)
			count = count + 1.0
		dialog.close()
		#self.updateItems('Twit')
		self.setFocus(self.shows)
		
	def onAction(self, action):
		if action == ACTION_PREVIOUS_MENU:
			if DO_LOGGING:
				LOGCLOSE()
			self.close()
	
	def onControl(self, control):
		if(control == self.itemList):
			try:
				LOG("Item list clicked...")
				LOG(self.itemList.getSelectedPosition())
				position = self.itemList.getSelectedPosition()
				filename = self.urlsInOrder[position]
				LOG("Playing: " + filename)
				if filename:
					LOG("Before Player Call")
					try:
						xbmc.Player().play(str(filename))
					except:
						LOG("Player Exception")
					LOG("After Player Call")
				else:
					xbmcgui.Dialog().ok('ERROR', 'Most likely video unavailable for download.')
			except:
				xbmc.output('ERROR: playing %s' % ( filename) )
			
		if(control == self.shows):
			print "Clicked: "
			self.changeShow(self.shows.getSelectedItem().getLabel())
	
	def changeShow(self, show):
		dialog.create("Getting " + show + " RSS Feed.")
		self.updateItems(show)
		dialog.close()
	
	def updateItems(self, show):
		LOG("rssFeeds Keys:")
		for key in rssFeeds.keys():
			LOG(key)
		if(rssFeeds.has_key("Twit")):
			LOG("HAS TWIT!")
			LOG(str(rssFeeds["Twit"]))
		if(not self.feeds.has_key(show)):
			try:
				self.feeds[show] = FeedItems(rssFeeds[show]).getData()
			except:
				xbmcgui.Dialog().ok("Error", "Could not get rss feed: '" + show + "'")
				return
		self.itemList.reset()
		self.urlsInOrder = None
		self.urlsInOrder = []
		for item in self.feeds[show]:
			self.itemList.addItem(item.getElement("title"))
			self.urlsInOrder.append(item.getElement("mediaUrl"))
	
	def cancelOpen():
		if DO_LOGGING:
			LOGCLOSE()
		self.close()



class FeedItems:
	def __init__(self, url):
		self.dom = None
		f = urllib.urlopen(url)
		xmlDocument = f.read()
		f.close()
		self.dom = xml.dom.minidom.parseString(xmlDocument)
		self.data = []
		self.extractURLNameDictionary()
		
	
	def extractURLNameDictionary(self):
		items = self.dom.getElementsByTagName("item")
		for item in items:
			elements = {}
			for itemElement in itemElements:
				try:
					elements[itemElement] = item.getElementsByTagName(itemElement)[0].childNodes[0].data.strip()
					#print itemElement, " = ", item.getElementsByTagName(itemElement)[0].childNodes[0].data
				except:
					pass
			try:
				elements["mediaUrl"] = item.getElementsByTagName("enclosure")[0].getAttribute("url").strip()
			except:
				try:
					elements["mediaUrl"] = item.getElementsByTagName("link")[0].childNodes[0].data.strip()
				except: 
					xbmcgui.Dialog().ok("Error", "Problem building feed.")
			self.data.append(RSSItem(elements))
		
	def getData(self):
		return self.data
class RSSItem:
	def __init__(self, elements):
		# list that includes required item elements
		self.elements = elements
		
	def getElement(self, element):
		return self.elements[element]
		
	def getElementNames(self):
		return self.elements.keys()
		
	def hasElement(self, element):
		return self.elements.has_key(element)
	
w = DiggNationViewer()
w.doModal()
del w


