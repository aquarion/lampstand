from lampstand.tools import splitAt
import re, time, random, sys, datetime
import lampstand.reactions.base
from lampstand import tools

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Whowas'


	def __init__(self, connection):
		#self.channelMatch = re.compile('.*')
		self.channelMatch    = re.compile('%s.? have you seen (.*)\??' % connection.nickname, re.IGNORECASE)
		#self.seenMatch    = re.compile('%s.? have you seen (.*)\??' % connection.nickname, re.IGNORECASE)
		self.privateMatch = re.compile('have you seen (.*)\??', re.IGNORECASE)
		self.dbconnection = connection.dbconnection
		

	def channelAction(self, connection, user, channel, message):

		print "[WHOWAS] requested"
		self.channel = channel;

		matches = self.channelMatch.findall(message)
		searchingfor = matches[0];

		if searchingfor[-1:] == "?":
			searchingfor = searchingfor[0:-1]
		space = re.compile(".*\s.*")
		if searchingfor.lower() == "your mum":
			connection.msg(channel, "%s: Not since she took on one piece of crumpet too many" % user)
		elif space.match(searchingfor):
			connection.msg(channel, "No idea, %s. Have you looked under the sofa?" % user)
		elif searchingfor.lower() == user.lower():
			connection.msg(channel, "Yes. You're over there. Hello %s. Did you want a cookie or something?" % user)
		elif searchingfor.lower() == connection.nickname.lower():
			connection.msg(channel, "I'm right here.")
		else:
			result = self.lastseen(searchingfor);
			if searchingfor in connection.people:
				result = "%s. Also, I think they're currently online!" % (result)
			if len(result) > 440:
				whereToSplit = splitAt(result, 440)
				stringOne = result[0:whereToSplit]
				stringTwo = result[whereToSplit:]
	
				connection.msg(channel, "%s... " % stringOne.encode('utf8'))
				connection.msg(channel, "... %s" % stringTwo.encode('utf8'))
			else:
				connection.msg(channel, result.encode('utf8'))
		return True
		
	def everyLine(self, connection, user, channel, message):
			cursor = self.dbconnection.cursor()
			cursor.execute('replace into lastseen (username, last_seen, last_words, channel) values (%s, %s, %s, %s)', (user, int(time.time()), message, channel) )
			
			self.dbconnection.commit()

	def leaveAction(self, connection, user, reason, params):

		channel = params[0]
		print "[WHOWAS] saw a nick leave: %s quit, saying %s (%s)" % (user, reason, params)
		cursor = self.dbconnection.cursor()
			
		cursor.execute('replace into lastquit (username, last_quit, reason, method, channel) values (%s, %s, %s, %s, %s)', (user, int(time.time()), params[-1], reason, channel) )
		
		print int(time.time())

	def privateAction(self, connection, user, channel, message):

		self.channel = "PM";

		print "[WHOWAS] privately requested"
		if self.privateMatch.match(message):
			matches = self.privateMatch.findall(message)
			searchingfor = matches[0]
			if searchingfor[-1:] == "?":
				searchingfor = searchingfor[0:-1]
			space = re.compile(".*\s.*")
			if searchingfor.lower() == "your mum":
				connection.msg(user, "%s: Not since she took on one piece of crumpet too many" % user)
			elif space.match(searchingfor):
				connection.msg(user, "No idea, %s. Have you looked under the sofa?" % user)
			elif searchingfor.lower() == user.lower():
				connection.msg(user, "Yes. You're over there. Hello %s. Did you want a cookie or something?" % user)
			elif searchingfor.lower() == connection.nickname.lower():
				connection.msg(user, "I'm right here.")
			else:
				result = self.lastseen(searchingfor);
				if searchingfor in connection.people:
					result = "%s, plus, I think they're online right now.!" % (result)
					
				if len(result) > 440:
					whereToSplit = splitAt(result, 440)
					stringOne = result[0:whereToSplit]
					stringTwo = result[whereToSplit:]
		
					connection.msg(user, "%s... " % stringOne.encode('utf8'))
					connection.msg(user, "... %s" % stringTwo.encode('utf8'))
				else:
					connection.msg(user, result.encode('utf8'))
					
			#returnMessage = self.lastseen(searchingfor)
			#print "[WHOWAS] %s " % returnMessage
			#connection.msg(user, returnMessage.encode('utf8'))


	def nickChangeAction(self, connection, old_nick, new_nick):
		print "[WHOWAS] saw a nick change"
		new_nick = ">%s" % new_nick
		cursor = self.dbconnection.cursor()
		cursor.execute('replace into lastseen (username, last_seen, last_words) values (%s, %s, %s)', (old_nick, time.time(), new_nick) )

	def lastseen(self, searchingfor, after_timestamp = 0, depth = 0):
	
		print "Looking for %s after %s" % (searchingfor, after_timestamp)
		
		if depth > 4:
			return ' ... and at that point I gave up';

		cursor = self.dbconnection.cursor()
		cursor.execute('SELECT username, last_seen, last_words, channel FROM lastseen where username LIKE %s and last_seen > %s order by last_seen desc', (searchingfor, int(after_timestamp)) )
		
		
		print 'SELECT username, last_seen, last_words, channel FROM lastseen where username LIKE %s and last_seen > %s order by last_seen desc limit 1' % ( searchingfor, after_timestamp) 
				
		result = cursor.fetchone()
		if result == None:
			message = "I haven't seen %s say anything" % searchingfor
			print "Looking for a quit for %s after %s" % (searchingfor, after_timestamp)
			return "%s%s" % (message, self.lastquit(after_timestamp, searchingfor))
		elif (result[2][0] == ">"): 
			# Last action is a rename
		
			deltadesc = "ago"
			
			if (after_timestamp == 0):
				print "No after timestamp"
				print result[1]
				print "Now"
				print time.localtime()
				print "Lastseen"
				print time.localtime(result[1])
				now = time.mktime(time.localtime())
				deltadiff = now - result[1]
			else:
				print "After timestamp %s" % after_timestamp
				print time.localtime()
				now = after_timestamp
				deltadesc = "later"
				deltadiff = result[1] - after_timestamp
			
			deltastring = tools.niceTimeDelta(deltadiff)
		
			if ((now - result[1]) > 86400):
				timefmt = "%a %d/%b/%Y %H:%M"
			else:
				timefmt = "%H:%M";			
			#timefmt = "%a %d/%b/%Y %H:%M"

			timechanged = datetime.datetime.fromtimestamp(result[1]).strftime(timefmt)
		
			message = "I last saw %s %s %s (%s) relabeling themselves as \"%s\". %s" % (result[0], deltastring, deltadesc, timechanged, result[2][1:], self.lastseen(result[2][1:], int(result[1]), depth +1 ))
		
		else:
			# Last action is a phrase
			print "Found a last phrase:"
			print result
			deltadesc = "ago"
			
			if (after_timestamp == 0):
				print "No after timestamp"
				print result[1]
				print "Now is %s" % time.localtime()
				print "Localtime of %s is %s" % (result[1], time.localtime(result[1]))
				now = time.mktime(time.localtime())
				deltastring = tools.niceTimeDelta(now - result[1])
			else:
				#print "After timestamp %s" % after_timestamp
				#print time.localtime()
				#print "Localtime of %s is %s" % (result[1], time.localtime(result[1]))
				#now = after_timestamp
				
				now = time.mktime(time.localtime(result[1]))
				
				deltadesc = "later"
				deltastring = tools.niceTimeDelta(result[1] - after_timestamp)
				print "Happening after %s" % after_timestamp
				print "Event happened  %s" % result[1]

			

			if ((now - result[1]) > 86400):
				timefmt = "%a %d/%b/%Y %H:%M"
			else:
				timefmt = "%H:%M";			

			timechanged = datetime.datetime.fromtimestamp(result[1]).strftime(timefmt)

			if (result[3] != self.channel):
				message = "I last saw %s %s %s (%s) on %s" % (result[0], deltastring, deltadesc, timechanged, result[3])
			else:
				message = "I last saw %s %s %s (%s) saying \"%s\"" % (result[0], deltastring, deltadesc, timechanged, result[2])

		return "%s%s" % (message, self.lastquit(result[1], searchingfor))


	def lastquit(self, lasttime, searchingfor):
		cursor = self.dbconnection.cursor()
		cursor.execute('SELECT last_quit, reason from lastquit where username LIKE %s and last_quit > %s', (searchingfor, lasttime ) )


		quitresult = cursor.fetchone();
		if quitresult == None:
			print "No quit for %s after %s" % (searchingfor, lasttime)

			return "";
		else:
			print "Quit result"
			
			print quitresult
			
			quittime = time.localtime(quitresult[0])
			timedelta = time.mktime(quittime) - lasttime;

			print quittime
			
			print "Localtime of %s is %s" % (quitresult[0], time.localtime(quitresult[0]))

			if(timedelta < 60):
				deltastring = "seconds"
			else:
				deltastring = tools.niceTimeDelta(timedelta);

			if (timedelta > 86400):
				timefmt = "%a %d/%b/%Y %H:%M"
			else:
				timefmt = "%H:%M";			

			quittime = datetime.datetime.fromtimestamp(quitresult[0]).strftime(timefmt)
			#quittime = datetime.datetime.fromtimestamp(quitresult[0]).strftime("%H:%M")			

			return ", they quit %s later (%s) with the message '%s'" % (deltastring, quittime, quitresult[1])

		return message;
