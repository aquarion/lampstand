from lampstand.tools import splitAt
import re, time, random, sys
import lampstand.reactions.base

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Whowas'


	def __init__(self, connection):
		self.channelMatch = re.compile('.*')
		self.seenMatch    = re.compile('%s.? have you seen ([\S,!\?]*)\??' % connection.nickname, re.IGNORECASE)
		self.privateMatch = re.compile('have you seen ([\S,!\?]*)\??', re.IGNORECASE)
		self.dbconnection = connection.dbconnection


	def channelAction(self, connection, user, channel, message):

		if self.seenMatch.match(message):
			print "[WHOWAS] requested"

			matches = self.seenMatch.findall(message)

			searchingfor = matches[0];

			if searchingfor[-1:] == "?":
				searchingfor = searchingfor[0:-1]


			if searchingfor.lower() == user.lower():
				connection.msg(channel, "Yes. You're over there. Hello %s. Did you want a cookie or something?" % user)
			elif searchingfor.lower() == connection.nickname.lower():
				connection.msg(channel, "I'm right here.")
			else:
				result = self.lastseen(searchingfor);
				if len(result) > 440:
					whereToSplit = splitAt(result, 440)
					stringOne = result[0:whereToSplit]
					stringTwo = result[whereToSplit:]
		
					connection.msg(channel, "%s... " % stringOne)
					connection.msg(channel, "... %s" % stringTwo)
				else:
					connection.msg(channel, result)
		else:
			cursor = self.dbconnection.cursor()


			cursor.execute('replace into lastseen (username, last_seen, last_words) values (?, ?, ?)', (user, time.time(), message) )
			self.dbconnection.commit()


	def privateAction(self, connection, user, channel, message):
		if self.privateMatch.match(message):
			matches = self.privateMatch.findall(message)
			connection.msg(user, self.lastseen(matches[0]))


	def nickChangeAction(self, connection, old_nick, new_nick):
		print "[WHOWAS] saw a nick change"
		new_nick = ">%s" % new_nick
		cursor = self.dbconnection.cursor()
		cursor.execute('replace into lastseen (username, last_seen, last_words) values (?, ?, ?)', (old_nick, time.time(), new_nick) )



	def lastseen(self, searchingfor):

		cursor = self.dbconnection.cursor()
		cursor.execute('SELECT * FROM lastseen where username LIKE ? order by last_seen desc', (searchingfor, ) )
		result = cursor.fetchone()
		if result == None:
			return "Which universe is %s in?".encode('utf8') % searchingfor
		elif (result[2][0] == ">"):
			return "I last saw %s on %s relabeling themselves as \"%s\". %s" % (result[0].encode('utf8'), time.strftime('%a, %1d %B %y at %H:%M', time.localtime(result[1])), result[2][1:].encode('utf8'), self.lastseen(result[2][1:]))
		else:
			return "I last saw %s on %s saying \"%s\"" % (result[0].encode('utf8'), time.strftime('%a, %1d %B %y at %H:%M', time.localtime(result[1])), result[2].encode('utf8'))
