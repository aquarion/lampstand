from lampstand.tools import splitAt
import re, time, random, sys
import lampstand.reactions.base

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Whowas'


	def __init__(self, connection):
		self.channelMatch = re.compile('.*')
		self.seenMatch    = re.compile('%s.? have you seen (.*)\??' % connection.nickname, re.IGNORECASE)
		self.privateMatch = re.compile('have you seen (.*)\??', re.IGNORECASE)
		self.dbconnection = connection.dbconnection
		

	def channelAction(self, connection, user, channel, message):

		if self.seenMatch.match(message):
			print "[WHOWAS] requested"

			matches = self.seenMatch.findall(message)

			searchingfor = matches[0];

			if searchingfor[-1:] == "?":
				searchingfor = searchingfor[0:-1]
			space = re.compile(".*\s.*")
			if space.match(searchingfor):
				connection.msg(channel, "No idea, %s. Have you looked under the sofa?" % user)
			elif searchingfor.lower() == user.lower():
				connection.msg(channel, "Yes. You're over there. Hello %s. Did you want a cookie or something?" % user)
			elif searchingfor.lower() == connection.nickname.lower():
				connection.msg(channel, "I'm right here.")
			else:
				result = self.lastseen(searchingfor);
				if len(result) > 440:
					whereToSplit = splitAt(result, 440)
					stringOne = result[0:whereToSplit]
					stringTwo = result[whereToSplit:]
		
					connection.msg(channel, "%s... " % stringOne.encode('utf8'))
					connection.msg(channel, "... %s" % stringTwo.encode('utf8'))
				else:
					connection.msg(channel, result.encode('utf8'))
		else:
			cursor = self.dbconnection.cursor()


			cursor.execute('replace into lastseen (username, last_seen, last_words) values (?, ?, ?)', (user, time.time(), message) )
			self.dbconnection.commit()


	def privateAction(self, connection, user, channel, message):
		print "[WHOWAS] privately requested"
		if self.privateMatch.match(message):
			matches = self.privateMatch.findall(message)
			searchingfor = matches[0]
			if searchingfor[-1:] == "?":
				searchingfor = searchingfor[0:-1]
			space = re.compile(".*\s.*")
			if space.match(searchingfor):
				connection.msg(user, "No idea, %s. Have you looked under the sofa?" % user)
			elif searchingfor.lower() == user.lower():
				connection.msg(user, "Yes. You're over there. Hello %s. Did you want a cookie or something?" % user)
			elif searchingfor.lower() == connection.nickname.lower():
				connection.msg(user, "I'm right here.")
			else:
				result = self.lastseen(searchingfor);
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
		cursor.execute('replace into lastseen (username, last_seen, last_words) values (?, ?, ?)', (old_nick, time.time(), new_nick) )

	def leaveAction(self, connection, user, reason, params):
		print "[WHOWAS] saw a nick leave: %s quit, saying %s (%s)" % (user, reason, params)
		cursor = self.dbconnection.cursor()
		cursor.execute('replace into lastquit (username, last_quit, reason, method) values (?, ?, ?, ?)', (user, time.time(), params[-1], reason) )
		#print 'replace into lastquit (username, last_quit, reason) values (%s, %s, %s)' % (user, time.time(), params[1])
	def lastseen(self, searchingfor, after_timestamp = 0, depth = 0):
	
		print "Looking for %s after %s" % (searchingfor, after_timestamp)
		
		if depth > 4:
			return ' ... and at that point I gave up';

		cursor = self.dbconnection.cursor()
		cursor.execute('SELECT username, last_seen, last_words FROM lastseen where username LIKE ? and last_seen > ? order by last_seen desc', (searchingfor, int(after_timestamp)) )
		
		
		print 'SELECT username, last_seen, last_words FROM lastseen where username LIKE %s and last_seen < %s order by last_seen desc' % ( searchingfor, after_timestamp) 
				
		result = cursor.fetchone()
		if result == None:
			return "I haven't seen %s say anything" % searchingfor
		elif (result[2][0] == ">"):
			return "I last saw %s on %s relabeling themselves as \"%s\". %s" % (result[0], time.strftime('%a, %1d %B %y at %H:%M', time.localtime(result[1])), result[2][1:], self.lastseen(result[2][1:], int(result[1]), depth +1 ))
		else:
			return "I last saw %s on %s saying \"%s\"" % (result[0], time.strftime('%a, %1d %B %y at %H:%M', time.localtime(result[1])), result[2])
