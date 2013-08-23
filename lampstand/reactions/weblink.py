import re, time, os
import lampstand.reactions.base
from lampstand import tools
import bitly_api
import urlparse

import gdata.youtube
import gdata.youtube.service

import requests
import BeautifulSoup

import StringIO
import Image

from twitter import Twitter

from twitter.oauth import OAuth, write_token_file, read_token_file
from twitter.oauth_dance import oauth_dance


def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Weblink'

	def __init__(self, connection):
		self.channelMatch = [
			re.compile('%s: Shorten that( URL)?' % connection.nickname, re.IGNORECASE),            #0
			re.compile('%s: Shorten (.*?)\'s? (link|url)' % connection.nickname, re.IGNORECASE),   #1
			re.compile('%s: Shorten this (link|url): (.*)$' % connection.nickname, re.IGNORECASE), #2
			re.compile('.*https?\:\/\/', re.IGNORECASE)]                                           #3
		self.dbconnection = connection.dbconnection
		self.bitly = bitly_api.Connection(connection.config.get("bitly","username"), connection.config.get("bitly","apikey"))
			
		self.yt_service = gdata.youtube.service.YouTubeService()
		self.yt_service.ssl = True
		
		self.lastlink = {}

		OAUTH_FILENAME  = os.environ.get('HOME', '') + os.sep + '.lampstand_oauth'
		CONSUMER_KEY    = connection.config.get("twitter", "consumer_key")
		CONSUMER_SECRET = connection.config.get("twitter", "consumer_secret")		

		if not os.path.exists(OAUTH_FILENAME):
			oauth_dance(
				"Lampstand", CONSUMER_KEY, CONSUMER_SECRET,
				OAUTH_FILENAME)
		
		self.oauth_token, self.oauth_token_secret = read_token_file(OAUTH_FILENAME)
		
		self.twitter = Twitter(
			auth=OAuth(
				self.oauth_token, self.oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET),
				secure=True,
				domain='api.twitter.com')

	def channelAction(self, connection, user, channel, message, matchindex):

		print "[WEBLINK] Activated, matchindex is %d" % matchindex

		if matchindex == 3: # Weblink
			print "[WEBLINK] That looks like a weblink : %s" % message

			links = self.grabUrls(message)
		
			print links
			now = time.time()
			
			
			for url in links:
				title = self.getTitle(url)
							
				if(title):
					connection.message(channel, "[ %s ]" % title)
						

				cursor = self.dbconnection.cursor()
				cursor.execute('insert into urllist (time, username, message, channel, url, title) values (%s, %s, %s, %s, %s, %s)', (now, user, message, channel, url, title) )

			self.lastlink[channel] = {'id': cursor.lastrowid, 'url': links[0] }

			self.dbconnection.commit()

		elif matchindex == 0: # Shorten That
			print "[WEBLINK] Shortening URL"

			print self.lastlink
			surl = self.bitly.shorten(self.lastlink[channel]['url'])
			
			url_split = urlparse.urlparse(self.lastlink[channel]['url'])
			output = "%s: %s link shortened to %s" % (user, url_split[1], surl['url'])
			connection.message(channel,output)

			cursor = self.dbconnection.cursor()
			cursor.execute('update urllist set shorturl = %s where id = %s', ( surl['url'], self.lastlink[channel]['id'] ) )
			self.dbconnection.commit()

		elif matchindex == 1: # SHorten user's url
	                for module in connection.channelModules:
	                        if module.__name == "Memory":
	                                memory = module;
			
			matches = self.channelMatch[matchindex].findall(message)[0]
			print matches
			result = memory.search(channel, matches[0], "http");
			print result

			if len(result) == 0:
				output = "%s: I've no idea which link you mean" % user
				connection.message(channel,output)
			else:
				links = self.grabUrls(result[-1]['message'])

				for link in links:
					surl = self.bitly.shorten(link)
					url_split = urlparse.urlparse(link)
					output = "%s: %s link shortened to %s" % (user, url_split[1], surl['url'])
					connection.message(channel,output.encode("utf-8"))
				

		elif matchindex == 2: # Shorten this URL
			print "[WEBLINK] Shortening requested URL : %s" % message
			links = self.grabUrls(message)

			if len(links) == 0:
				print "[WEBLINK] No links found"
				connection.message(channel, "%s: I see no links in that" % user)
				return

			print links

			cursor = self.dbconnection.cursor()
			for link in links:
				print link
				now = time.time()
				surl = self.bitly.shorten(link)
				cursor.execute('insert into urllist (time, username, message, channel, shorturl) values (%s, %s, %s, %s, %s)', (now, user, message, channel, surl['url']) )
				url_split = urlparse.urlparse(link)
				output = "%s: %s link shortened to %s" % (user, url_split[1], surl['url'])
				connection.message(channel,output)
				


	def grabUrls(self, text):

		"""Given a text string, returns all the urls we can find in it."""

		urls = '(?: %s)' % '|'.join("""http https telnet gopher file wais ftp""".split())
		ltrs = r'\w'
		gunk = r'/#~:.?+=&%@!\-'
		punc = r'.:?\-,'
		any = "%(ltrs)s%(gunk)s%(punc)s" % { 	'ltrs' : ltrs,
							'gunk' : gunk,
							'punc' : punc }

		url = r"""
		    \b                            # start at word boundary
			%(urls)s    :             # need resource and a colon
			[%(any)s]  +?             # followed by one or more
						  #  of any valid character, but
						  #  be conservative and take only
						  #  what you need to....
		    (?=                           # look-ahead non-consumptive assertion
			    [%(punc)s]*           # either 0 or more punctuation
			    (?:   [^%(any)s]      #  followed by a non-url char
				|                 #   or end of the string
				  $
			    )
		    )
		    """ % {'urls' : urls,
			   'any' : any,
			   'punc' : punc }
		
		url_re = re.compile(url, re.VERBOSE | re.MULTILINE)

		return url_re.findall(text)

	def getTitle(self, url):
		title = False
	
		urlp = urlparse.urlparse(url)
		print url

		if "twitter" in urlp.netloc.split("."):
			path = urlp.path.split("/");
			id = path[-1]
			tweet = self.twitter.statuses.show(id=id)
			print tweet
			title = "@%s (%s): %s" % (tweet['user']['name'], tweet['user']['screen_name'], tweet['text'])
		elif "youtube" in urlp.netloc.split("."):
			print "That's a Youtube Link"
			query = urlparse.parse_qs(urlp.query)
			if "v" in query.keys():
				print "That's a Youtube Link with a v! %s " % query['v'][0]
				entry = self.yt_service.GetYouTubeVideoEntry(video_id=query['v'][0])
				print entry
				deltastring = tools.niceTimeDelta(int(entry.media.duration.seconds))
				#deltastring = entry.media.duration.seconds
				title = "Youtube video: %s (%s)" % (entry.media.title.text, deltastring)
				print title
				#connection.message(channel,title)
		else:
			if urlp.netloc == "www.bbc.co.uk":
				url = "http://altru.istic.net/thingsnstuff/proxy.php?f="+url
			else:
				print "Netloc: %s" % urlp.netloc
			headers = {'User-agent': 'Lampstand IRC Bot (contact aquarion@maelfroth.org)'}
			try:
				req = requests.get(url, headers=headers, timeout=30)
			except requests.exceptions.Timeout:
				return "That link timed out"
			k = len(req.content) / 1024
			if req.status_code != 200:
				title = "That link returned an error %s" % (req.status_code)
			elif req.headers['content-type'].find("text/html") != -1 or req.headers['content-type'].find("application/xhtml+xml") != -1:
				soup = BeautifulSoup.BeautifulSoup(req.text, convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES)
				title = soup.title.string
			else:
				if req.headers['content-type'].find("image/") == 0:
					image_file = StringIO.StringIO(req.content)
					#color = most_colour.most_colour(image_file)
					
					image_file.seek(0)
					im = Image.open(image_file)
					try:
						im.seek(1)
						title = "An animation, %dx%d (%dk)" % (im.size[0], im.size[1], k)
					except:
						title = "An image, %dx%d (%dk)" % (im.size[0], im.size[1], k)
				else:
					title = "A %s file (%dk)" % (req.headers['content-type'], k)
			
		return title.strip()
