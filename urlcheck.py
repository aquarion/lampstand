#!/usr/bin/python
import ConfigParser
import requests
import MySQLdb
import os, sys, re, socket

class urlCheck():
	config = {}
	
	def __init__(self):
		self.loadConfig()
		self.connectToDB()
		
	def loadConfig(self):
		basedir = os.path.dirname(os.path.abspath(sys.argv[0]))
		config = ConfigParser.ConfigParser()
		config.read(["defaults.ini", basedir+'/config.ini'] )
		self.config = config
	
	def connectToDB(self):
		self.dbconnection = MySQLdb.connect(user = self.config.get("database","user"), passwd = self.config.get("database","password"), db = self.config.get("database","database"))
		
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
		
	
	def checkBatch(self):
		query = 'SELECT id, message, checked_status, checked_repeat FROM urllist WHERE datediff(`checked_date`, NOW()) > 90 or `checked_date` = 0 '
		
		update_query = "UPDATE `urllist` SET checked_date = NOW(), checked_status = %s, checked_repeat = %s where id = %s"
		
		cursor = self.dbconnection.cursor()
		cursor.execute(query)
		links = cursor.fetchall()
		n = 0
		for link in links:
			urls = self.grabUrls(link[1])
			print link
			print urls
			if len(urls) == 0:
				continue

			url = urls[0]
			
			status_code = self.get_url(url)
			
			if status_code == link[2]:
				repeat_code = link[3]+1
			else:
				repeat_code = 1
			params = (status_code, repeat_code, link[0])
			print params
			cursor.execute(update_query, params)
			print " -"
			n = n + 1
			if n == 20:
				n = 0
				print "Commitment!!\n-"
				self.dbconnection.commit()
			
		self.dbconnection.commit()
		
	def get_url(self, url):
		try:
			r = requests.get(url, timeout=10)
			return r.status_code
		except requests.exceptions.Timeout:
			return 504 # Gateway Timeout
		except (requests.exceptions.ConnectionError, socket.gaierror, socket.error):
			return 502 # Bad Gateway
		except requests.exceptions.TooManyRedirects:
			return 508 # Loop Detected
		except (requests.exceptions.RequestException, AttributeError, UnicodeError):
			return 418 # I'm a teapot

if __name__ == '__main__':
	checker  = urlCheck()
	
	checker.checkBatch()
