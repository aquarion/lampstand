import re, time
import lampstand.reactions.base
import bitly_api

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Weblink'

	def __init__(self, connection):
		self.channelMatch = [re.compile('.*https?\:\/\/', re.IGNORECASE), re.compile('%s: Shorten that( URL)?' % connection.nickname, re.IGNORECASE)]
		self.dbconnection = connection.dbconnection
		self.bitly = bitly_api.Connection(connection.config.get("bitly","username"), connection.config.get("bitly","apikey"))
		self.lastlink = {}

	def channelAction(self, connection, user, channel, message, matchindex):

		if matchindex == 0:
			print "[WEBLINK] That looks like a weblink : %s" % message

			links = self.grabUrls(message)
		
			print links
			now = time.time()

			cursor = self.dbconnection.cursor()
			cursor.execute('insert into urllist (time, username, message, channel) values (%s, %s, %s, %s)', (now, user, message, channel) )

			self.lastlink[channel] = {'id': cursor.lastrowid, 'url': links[0] }

			self.dbconnection.commit()
		elif matchindex == 1:
			print "[WEBLINK] Shortening URL"

			print self.lastlink
			surl = self.bitly.shorten(self.lastlink[channel]['url'])
			
			output = "%s: %s" % (user, surl['url'])

			connection.msg(channel,output.encode("utf-8"))

			cursor = self.dbconnection.cursor()
			cursor.execute('update urllist set shorturl = %s where id = %s', ( surl['url'], self.lastlink[channel]['id'] ) )
			self.dbconnection.commit()

			


	def grabUrls(self, text):

		"""Given a text string, returns all the urls we can find in it."""

		urls = '(?: %s)' % '|'.join("""http https telnet gopher file wais ftp""".split())
		ltrs = r'\w'
		gunk = r'/#~:.?+=&%@!\-'
		punc = r'.:?\-'
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

