#!/usr/bin/python

#


"""
I am Lampstand. Beware.


Todo:

	* Move databases to MySQL instead of sqlite
	* Store events in database instead of hash
	* Same for admins, probably.
	* Multiple matching regexes for each module
		* So we can combine do/say into one module
	* Generic reaction module
		* Shift favourite/Cohan into same
	* King James Bible
	* Quotes Interface
	* iCal interface
	* Shift all Reactions into other files
	* Generify overuse a bit better
	* Make Overuse code tell the person who is trying to overuse it that they suck
	* Fix "Since" events.
	* NickServ support
	* Choose incoming IP
	* All the cool shit in your head
"""

def splitAt(string, number):
	if len(string) > number:
		index = number
		whitespace =  re.compile('\s')
		while not whitespace.match(string[index]) and index != 0:
			#print "%d: %s" % (index, string[index])
			index = index -1

		return index
	else:
		return number

def overUsed(uses, number, cooldown):

		if len(uses) >= number:
			first_use = int(uses[0])
			use_allowed_again = first_use + cooldown
			if time.time() < use_allowed_again:
				print "Use Blocked. Try again in %s" % (int(use_allowed_again) - time.time());
				return True

		return False


# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys
import re
import cPickle
from pysqlite2 import dbapi2 as sqlite
import string

from lampstand import shakeinsult, dice, bible, eightball, sms

import dictclient

class MessageLogger:
	"""
	An independent logger class (because separation of application
	and protocol logic is a good thing).
	"""
	def __init__(self, file):
		self.file = file

	def log(self, message):
		"""Write a message to the file."""
		timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
		self.file.write('%s %s\n' % (timestamp, message))
		self.file.flush()

	def close(self):
		self.file.close()

class ChannelActions:

	def __init__(self, connection):
		self.connection = connection


	def action(self, user, channel, message):
			for channelModule in self.connection.channelModules:
				if isinstance(channelModule.channelMatch, tuple):
					for channelSubMatch in channelModule.channelMatch:
						if channelSubMatch.match(message):
							channelModule.channelAction(self.connection, user, channel, message)
				elif channelModule.channelMatch.match(message):
					#print 'Channel Matched on %s' % channelModule
					channelModule.channelAction(self.connection, user, channel, message)

			#print "< %s/%s: %s" % (user, channel, message)

class PrivateActions:

	peopleToIgnore = ('ChanServ')

	def __init__(self, connection):
		self.connection = connection

	def action(self, user, channel, message):
		if user in self.peopleToIgnore:
			print "(Ignoring)"
		else:
			matched = 0
			for privateModule in self.connection.privateModules:
				if privateModule.privateMatch.match(message):
					matched = matched + 1
					print 'Private Matched on %s' % privateModule
					privateModule.privateAction(self.connection, user, channel, message)
			if matched == 0:
				self.connection.msg(user, "I didn't understand that, sorry. Hi, I'm Lampstand. I'm a bot built for #maelfroth by Aquarion <nicholas@aquarionics.com>. Please talk to him if you have a problem with me. Some documentation about me is at http://hol.istic.net/lampstand")


class NickChangeActions:

	peopleToIgnore = ('ChanServ')

	def __init__(self, connection):
		self.connection = connection

	def action(self, old_nick, new_nick):
		if old_nick in self.peopleToIgnore or new_nick in self.peopleToIgnore:
			print "(Ignoring)"
		else:
			matched = 0
			for nickChangeModule in self.connection.nickChangeModules:
				nickChangeModule.nickChangeAction(self.connection, old_nick, new_nick)


class DiceReaction:

	cooldown_number = 5
	cooldown_time   = 60
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. roll (\d*d\d*)(.*)' % connection.nickname, re.IGNORECASE)


	def channelAction(self, connection, user, channel, message):


		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(user, "The dice are too hot to touch. Give them a couple of minutes to cool down." )
			return

		item = self.channelMatch.findall(message);

		print "[ROLLING DICE] %s" % item
		try:
			result = dice.roll(item[0][0]);
		except:
			connection.msg(channel, "The dice blew up." )
			return

		print "[ROLLING DICE] %s, got %s" % (item[0], result)


		if result == False:
			connection.msg(channel, "%s: I don't understand that format yet, sorry :(" % user )
			return

		display = result[0]
		total = 0
	 	for elem in result[0]:
	 		total = total + elem

		originaltotal = total

		message = "%s Total %s " % (display, total)

		print "Item: %s " % item

		if len(item[0]) > 1 and item[0][1] != '':
			modifier = ''.join(item[0][1].split(' '))
			print "Modifier is %s" % modifier
			print "Modifier is %s -- %s" % (modifier[0], modifier[1:])


			if modifier[0] == "+":
				total = total + string.atof(modifier[1:])
			if modifier[0] == "-":
				total = total - string.atof(modifier[1:])
			if modifier[0] == "*":
				total = total * string.atof(modifier[1:])
			if modifier[0] == "/":
				total = total / string.atof(modifier[1:])

			message = "%s %s = %d " % (display, modifier, total)


		connection.msg(channel, "%s, You rolled %s, you got %s" % (user, item[0][0], message )  )


class InsultReaction:

	cooldown_number = 3
	cooldown_time   = 60
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. insult (\w*)(!?)' % connection.nickname, re.IGNORECASE)


	def channelAction(self, connection, user, channel, message):

		print "[INSULT] called"

		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(user, "I'm bored of this, insult them yourself." )
			return

		item = self.channelMatch.findall(message);

		if item[0][0].lower() == connection.nickname.lower():
			connection.msg(channel, "%s: No." % user )
			return

		if item[0][0].lower() == 'aquarion':
			connection.msg(channel, "%s: Do I look suicidal? No." % user )
			return

		ownerMatch = re.compile('.*aquarion.*', re.IGNORECASE)
		myNameMatch = re.compile('.*%s.*' % connection.nickname, re.IGNORECASE)
		if ownerMatch.match(item[0][0]) or myNameMatch.match(item[0][0]):
			connection.msg(channel, "%s: Hah. Very clever. Still no." % user )
			return

		print "%s" % item
		insult = shakeinsult.shakeinsult(1);

		connection.msg(channel, "%s, %s" % (item[0][0], insult )  )

		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##


class BibleReaction:

	cooldown_number = 3
	cooldown_time   = 120
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. (\w*) (\d+\:\S+)' % connection.nickname, re.IGNORECASE)

	def channelAction(self, connection, user, channel, message):
		matches = self.channelMatch.findall(message);


		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(user, "Enough with the religion for now.")
			return

		print "[Bible] %s" % matches

		bibleConnection = bible.ESVSession()
		result = bibleConnection.doPassageQuery('%s %s' % (matches[0][0], matches[0][1]))

		result = ''.join(result.split('\n'))

		connection.msg(channel, "%s, %s [ESV]" % (user, result)  )

class DictionaryReaction:

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. define (\w*)' % connection.nickname, re.IGNORECASE)

	def channelAction(self, connection, user, channel, message):
		matches = self.channelMatch.findall(message);

		print "[Define] %s" % matches

		specialDict = {
			'foip' : 'FOIP (\'Find Out In Play\') is any information you have that another character in the system does not have. Therefore, it is anything not on the website, in the almanac or in the rules books. Broadcasting this is a kickable offence on #maelfroth. If someone claims what you are talking about is FOIP, you need to stop talking about it as you may be damaging the game of others.',
			'herring': 'Type of fish. There is nothing between it and Marmalade it in my dictionary. My dictionary is not in alphabetical order, which is why it still has "kelp"',
			'marmalade' : 'A type of citris-based conserve. There is nothing before it in my dictionary until "herring". My dictionary is oddly ordered, however, so it still contains "Lemur"',
			'catbus' : 'You don\'t want to know.',
			'lampstand' : "That's me. Hi there"
			}


		if specialDict.has_key(matches[0].lower()):
			connection.msg(channel, "%s" % specialDict[matches[0].lower()])
			return


		dictcxn = dictclient.Connection()

		dfn = dictcxn.define("*", matches[0])

		if not dfn:
			connection.msg(channel, "%s: There is no such word as '%s' in my dictionary. In fact, everything between 'herring' and 'marmalade' appears to be completely missing." % (user, matches[0]))
			return

		result = ' '.join(dfn[0].getdefstr().split('\n'))

		print "[Define] %s" % result

		if len(result) > 880*2:

			whereToSplit = splitAt(result, 860)
			result = "%s [Cut for length]" % result[0:whereToSplit]

		if len(result) > 440:
			whereToSplit = splitAt(result, 440)
			stringOne = result[0:whereToSplit]
			stringTwo = result[whereToSplit:]

			connection.msg(channel, "%s... " % stringOne)
			connection.msg(channel, "... %s" % stringTwo)
		else:
			connection.msg(channel, "%s" % result)

class PokeReaction:

	cooldown_number = 2
	cooldown_time   = 360
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('.*pokes %s' % connection.nickname, re.IGNORECASE)


	def channelAction(self, connection, user, channel, message):
		print "[Poke] called"


		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			return

		connection.msg(channel, "Do I look like a facebook user? Fuck off." )

		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

class EightballReaction:

	cooldown_number = 2
	cooldown_time   = 360
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('^%s.  ?ask the 8.ball' % connection.nickname, re.IGNORECASE)


	def channelAction(self, connection, user, channel, message):
		print "[8Ball] called"


		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(user, "The 8-ball says: 'Find a new prophet, I quit.', I'd give it a while to cool down." )
			return

		connection.msg(channel, "%s: %s" % (user, eightball.question()) )

		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

class CohanReaction:

	cooldown_number = 2
	cooldown_time   = 360
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. What is best in life?' % connection.nickname, re.IGNORECASE)


	def channelAction(self, connection, user, channel, message):
		print "[Cohan] called"


		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(channel, "Not Telling" )
			return

		connection.msg(channel, "To crush your enemies, see them driven before you, and to hear the lamentations of their women!" )

		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

class PodBayReaction:

	cooldown_number = 2
	cooldown_time   = 360
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. Open the pod bay doors' % connection.nickname, re.IGNORECASE)


	def channelAction(self, connection, user, channel, message):
		print "[PodBay] called"


		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(channel, "I think you have your AIs confused." )
			return

		connection.msg(channel, "I can't do that, %s" % user )

		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

class FavouriteReaction:

	cooldown_number = 10
	cooldown_time   = 360
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. What is your favou?rite (.*)\?' % connection.nickname, re.IGNORECASE)


	def channelAction(self, connection, user, channel, message):

		matches = self.channelMatch.findall(message);

		print "[Favourite] %s" % matches


		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(channel, "Not Telling" )
			return

		favourites = {
			'movie'         : 'Luxo Jr.',
			'song'          : 'They Might Be Giants - Birdhouse in Your Soul', #['Barenaked Ladies - Light Up My Room',
			'book'          : "I don't go for big, complicated books. I prefer light reading",
			'computer game' : "Portal. GLaDOS is my idol. #This was a triumph. I'm making a note here, huge success#",
			'color'			: "Straw",
			'colour'		: "Incandescent",
			'cake'	    	: "Delicious and moist chocolate cake."
			}

		if favourites.has_key(matches[0].lower()):
			connection.msg(channel, "%s: %s" % (user, favourites[matches[0].lower()]))
		else:
			connection.msg(channel, "%s: I'm not sure yet" % user)

		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

class HowLongReaction:

	#@todo: "How long since $specific event"
	#@todo: "How long since Maelstrom?"
	#@todo: Custom events, player events, data driven thing (ical export?)

	cooldown_number = 5
	cooldown_time   = 360
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. how long until (.*?)\?' % connection.nickname, re.IGNORECASE)
		self.privateMatch = re.compile('how long until (.*?)\?', re.IGNORECASE)


	def channelAction(self, connection, user, channel, message):

		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(channel, "Shortly less than when you last asked.")
			return

		match = self.channelMatch.findall(message);


		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

		connection.msg(channel, self.howLong(match))

	def privateAction(self, connection, user, channel, message):
		match = self.privateMatch.findall(message);
		connection.msg(user, self.howLong(match))


	def howLong(self, match):

		print "[How Long] called with '%s'" % match[0]


		events = [
			('2007 IV',  '2007-09-05 18:00'),
			('Event I', '2008-03-21 18:00'),
			('Event II', '2008-06-06 18:00'),
			('Event III', '2008-07-18 18:00'),
			('Event IV', '2008-09-05 18:00'),

			('Event 1 2009',  '2009-04-10 18:00'),

			('Froth meet', '2008-04-19 18:00'),

			('Contrivance', '2008-04-26 11:00')
			]

		last_event = time.strptime('1981-01-26 18:00', '%Y-%m-%d %H:%M')

		current_time = time.time()

		eventName = 'Maelstrom'

		foundEvent = False

		eventList = []

		if not foundEvent:
			for event in events:
				maelstrom = time.mktime(time.strptime(event[1], '%Y-%m-%d %H:%M'))

				if maelstrom > current_time:
					eventList.append(event[0])

				print "comparing %s/%s" % (event[0], event[1])

				if event[0].lower() == match[0].lower():
					eventName = event[0]
					print "Direct Match on %s" % event[0]
					foundEvent = event
					break
				elif maelstrom > current_time and match[0].lower() == 'maelstrom':
					print "Keeping %s" % event[1]
					eventName = event[0]
					foundEvent = event
					break

		if not foundEvent:
			return "I don't know when that is. I know about: '%s' & 'Maelstrom'" % "', '".join(eventList)
			return

		if (maelstrom < current_time):
			swap = current_time
			current_time = maelstrom
			maelstrom = swap
			returnformat = "%s time in was %s%s%s ago"
		else:
			returnformat = "%s is in %s%s%s"


		event = foundEvent

		days = int((maelstrom - current_time) / (60*60*24));
		remainder = (maelstrom - current_time) % (60*60*24);
		hours = remainder / (60*60)
		remainder = (maelstrom - current_time) % (60*60);
		minutes = remainder / 60

		if int(days) == 1:
			days_message = "1 day, "
		elif days > 1:
			days_message = "%d days, " % days
		else:
			days_message = ''

		if int(hours) == 1:
			hours_message = "1 hour, "
		elif hours > 1:
			hours_message = "%d hours, " % hours
		else:
			hours_message = ''


		if int(minutes) == 1:
			minutes_message = "1 minute"
		elif minutes > 1:
			minutes_message = "%d minutes" % minutes
		else:
			minutes_message = ''



		return returnformat % (eventName, days_message, hours_message, minutes_message)

class SayReaction:

	canSay = ("Aquarion")

	def __init__(self, connection):
		self.privateMatch = re.compile('say (.*)', re.IGNORECASE)


	def privateAction(self, connection, user, channel, message):
		print "[Say] called"

		if user in self.canSay:
			matches = self.privateMatch.findall(message)
			print "[Say] %s %s" % (sys.argv[1], matches[0])
			connection.msg("#%s" % sys.argv[1], matches[0])


class DoReaction:

	canSay = ("Aquarion")

	def __init__(self, connection):
		self.privateMatch = re.compile('do (.*)', re.IGNORECASE)


	def privateAction(self, connection, user, channel, message):
		print "[Do] called"

		if user in self.canSay:
			matches = self.privateMatch.findall(message)
			print "[Do] %s %s" % (sys.argv[1], matches[0])
			connection.me("#%s" % sys.argv[1], matches[0])

class QuitReaction:

	canSay = ("Aquarion")

	def __init__(self, connection):
		self.privateMatch = re.compile('quit (.*)', re.IGNORECASE)


	def privateAction(self, connection, user, channel, message):
		print "[Quit] called"

		if user in self.canSay:
			matches = self.privateMatch.findall(message)
			print "[Quit] %s %s" % (sys.argv[1], matches[0])
			connection.quit(matches[0])

class TellAqReaction:

	canSay = ("Aquarion")

	def __init__(self, connection):
		self.privateMatch = re.compile('Tell Aquarion (.*)', re.IGNORECASE)


	def privateAction(self, connection, user, channel, message):
		matches = self.privateMatch.findall(message)
		print "[Summon Aq] called"

		sendThis = 'LS: %s: %s ' % (user, matches[0])

		if len(sendThis) > 159:
			connection.msg(user, "Can't do that Dave. Message too long")
		else:
			sms.send(sendThis)
			connection.msg(user, "Message Sent")


class WhowasReaction:

	def __init__(self, connection):
		self.channelMatch = re.compile('.*')
		self.seenMatch    = re.compile('%s.? have you seen (.*?)\?' % connection.nickname, re.IGNORECASE)
		self.privateMatch = re.compile('have you seen (.*?)\?', re.IGNORECASE)
		self.dbconnection = connection.dbconnection


	def channelAction(self, connection, user, channel, message):

		if self.seenMatch.match(message):
			print "[WHOWAS] requested"

			matches = self.seenMatch.findall(message)
			if matches[0].lower() == user.lower():
				connection.msg(channel, "Yes. You're over there. Hello %s. Did you want a cookie or something?" % user)
			elif matches[0].lower() == connection.nickname.lower():
				connection.msg(channel, "I'm right here.")
			else:
				connection.msg(channel, self.lastseen(matches[0]))
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
			return "Which universe is %s in?" % searchingfor
		elif (result[2][0] == ">"):
			return "I last saw %s on %s relabeling themselves as \"%s\"" % (result[0].encode('utf8'), time.strftime('%a, %1d %B %y at %H:%M', time.localtime(result[1])), result[2][1:].encode('utf8'))
		else:
			return "I last saw %s on %s saying \"%s\"" % (result[0].encode('utf8'), time.strftime('%a, %1d %B %y at %H:%M', time.localtime(result[1])), result[2].encode('utf8'))


class WeblinkReaction:

	def __init__(self, connection):
		self.channelMatch = re.compile('.*https?\:\/\/')
		self.dbconnection = connection.dbconnection

	def channelAction(self, connection, user, channel, message):
		print "[WEBLINK] That looks like a weblink : %s" % message

		cursor = self.dbconnection.cursor()
		cursor.execute('insert into urllist (time, username, message) values (?, ?, ?)', (time.time(), user, message) )
		self.dbconnection.commit()

class OpinionReaction:

	def __init__(self, connection):
		self.channelMatch = (re.compile('(.*?)(\w*)(\+\+|--)'), re.compile('%s.? what do you think of (.*?)\??' % connection.nickname, re.IGNORECASE))
		self.dbconnection = connection.dbconnection

	def channelAction(self, connection, user, channel, message):
		match = self.channelMatch[0].findall(message);
		if (match):
			connection.msg(channel, self.vote(match, user));
		else:
			connection.msg(channel, self.opinion(match[0]));

	def vote(self, match, user):
		match=match[0]
		if match[2] == '--':
			vote = -1
		else:
			vote = +1

		cursor = self.dbconnection.cursor()
		#CREATE TABLE vote (id INTEGER PRIMARY KEY, username varchar(64), item varchar(64), vote tinyint);

		cursor.execute('insert into vote (time, username, item, vote) values (?, ?, ?, ?)', (time.time(), user, match[1], vote) )

		#return match;

	def opinion(self, item):
		return 'No idea, mate';

class HugReaction:


	cooldown_number   = 5
	cooldown_time     = 120
	uses              = []

	def __init__(self, connection):

		self.default = "chocolate";

		self.banned = {}#{'entimix': 'rickroller'}

		self.channelMatch = re.compile('.*hugs %s' % connection.nickname, re.IGNORECASE)
		self.privateMatch = re.compile('give me (.*)', re.IGNORECASE)

		self.dbconnection = connection.dbconnection

		#try:
		#
		#	FILE = open("hugThings.txt", 'r')
		#	self.hugReaction = cPickle.load(FILE)
		#	#save#self.hugReaction = cPickle.dump(chocolateReplacement, FILE)
		#	FILE.close()
		#except:
		#	self.hugReaction = {}

	def channelAction(self, connection, user, channel, message):

		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			print "[HUG REACTION] OVERUSED %s" % user;
			connection.msg(channel, "%s: I am not a vending machine :(" % user)
			return

		if (self.banned.has_key(user.lower())):
			print "[HUG REACTION] BANNED %s" % user;
			insult = shakeinsult.shakeinsult(1);
			connection.msg(channel, "%s the %s, %s" % (user, self.banned[user.lower()], insult )  )
			return

		print "[HUG REACTION] GET %s" % user;
		connection.me(channel, self.hug(user))

		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

	def privateAction(self, connection, user, channel, message):

		item = self.privateMatch.findall(message);

		print "[HUG REACTION] SET %s %s" % (user, item[0]);
		connection.msg(user, self.set(user, item[0]))

	#def save(self):
	#	FILE = open("hugThings.txt", 'w')
	#	#load#self.hugReaction = cPickle.load(FILE)
	#	cPickle.dump(self.hugReaction, FILE)
	#	FILE.close()

	def set(self, username, item):
		cursor = self.dbconnection.cursor()
		cursor.execute('replace into hugReaction (username, item) values (?, ?)', (username, item) )
		self.dbconnection.commit()

		print "Set %s hug reaction to %s" % (username, item);
		return "When you hug me, I'll give you '%s'" % item;

	def hug(self, username):

		cursor = self.dbconnection.cursor()
		cursor.execute('SELECT * FROM hugReaction where username LIKE ?', (username, ) )
		result = cursor.fetchone()

		if result != None:
			print "I have a replacement for %s: %s" % (username, result[1]);
			return "gives %s %s " % (username, result[1].encode('utf8'))

		else:
			print "I have no replacement for %s" % username;
			return "gives %s %s " % (username, self.default)

class LampstandLoop(irc.IRCClient):
	"""An IRC Bot for #maelfroth."""

	nickname = "Lampstand"



	def connectionMade(self):
		irc.IRCClient.connectionMade(self)
		self.logger = MessageLogger(open(self.factory.filename, "a"))

		self.channel    = ChannelActions(self)
		self.private    = PrivateActions(self)
		self.nickchange = NickChangeActions(self)

		self.dbconnection = sqlite.connect('lampstand.db')


		self.channelModules = []
		self.channelModules.append(HugReaction(self))
		self.channelModules.append(PodBayReaction(self))
		self.channelModules.append(InsultReaction(self))
		self.channelModules.append(WhowasReaction(self))
		#self.channelModules.append(RevelationReaction(self))
		self.channelModules.append(BibleReaction(self))
		self.channelModules.append(DiceReaction(self))
		self.channelModules.append(WeblinkReaction(self))
		self.channelModules.append(PokeReaction(self))
		self.channelModules.append(DictionaryReaction(self))
		self.channelModules.append(OpinionReaction(self))
		self.channelModules.append(HowLongReaction(self))
		self.channelModules.append(FavouriteReaction(self))
		self.channelModules.append(CohanReaction(self))
		self.channelModules.append(EightballReaction(self))

		self.privateModules = []
		self.privateModules.append(TellAqReaction(self))
		self.privateModules.append(WhowasReaction(self))
		self.privateModules.append(HugReaction(self))
		self.privateModules.append(SayReaction(self))
		self.privateModules.append(DoReaction(self))
		self.privateModules.append(QuitReaction(self))
		self.privateModules.append(HowLongReaction(self))

		self.nickChangeModules = []
		self.nickChangeModules.append(WhowasReaction(self))

		self.logger.log("[connected at %s]" %
						time.asctime(time.localtime(time.time())))

	def connectionLost(self, reason):
		irc.IRCClient.connectionLost(self, reason)
		self.logger.log("[disconnected at %s]" %
						time.asctime(time.localtime(time.time())))
		self.logger.close()


	# callbacks for events

	def signedOn(self):
		"""Called when bot has succesfully signed on to server."""
		self.join(self.factory.channel)

	def joined(self, channel):
		"""This will get called when the bot joins the channel."""
		self.logger.log("[I have joined %s]" % channel)
		#sms.send('Lampstand: I have returned to %s' % channel)

	def privmsg(self, user, channel, msg):
		"""This will get called when the bot receives a message."""
		user = user.split('!', 1)[0]
		self.logger.log("<%s> %s" % (user, msg))


		print "> %s/%s: %s" % (user, channel, msg)
		self.logger.log("<%s> %s" % (self.nickname, msg))

		if (msg[0:3] == '***'):
			return

		# Check to see if they're sending me a private message
		if channel == self.nickname:
			self.private.action(user, channel, msg)
			return
		else:
			self.channel.action(user, channel, msg)

		# Otherwise check to see if it is a message directed at me
		#if msg.startswith(self.nickname + ":"):
		#    msg = self.channel.action(user, channel, msg)



	def action(self, user, channel, msg):
		"""This will get called when the bot sees someone do an action."""
		user = user.split('!', 1)[0]
		self.channel.action(user, channel, msg)
		self.logger.log("* %s %s" % (user, msg))

	# irc callbacks

	def irc_NICK(self, prefix, params):
		"""Called when an IRC user changes their nickname."""
		old_nick = prefix.split('!')[0]
		new_nick = params[0]
		self.logger.log("%s is now known as %s" % (old_nick, new_nick))
		self.nickchange.action(old_nick, new_nick)


class LampstandFactory(protocol.ClientFactory):
	"""We make Lampstands

	A new protocol instance will be created each time we connect to the server.
	"""

	# the class of the protocol to build when new connection is made
	protocol = LampstandLoop

	def __init__(self, channel, filename):
		self.channel = channel
		self.filename = filename

	def clientConnectionLost(self, connector, reason):
		"""If we get disconnected, reconnect to server."""
		#connector.connect()
		sms.send('Lampstand: HAZ NO CONEXON')

	def clientConnectionFailed(self, connector, reason):
		print "connection failed:", reason
		reactor.stop()


if __name__ == '__main__':
	# initialize logging
	log.startLogging(sys.stdout)

	if len(sys.argv) < 3:
		print "Not enough arguments. Try %s #channel logfile [server]" % sys.argv[0]
		sys.exit(1)

	server = "cosmos.esper.net"

	if len(sys.argv) == 4:
		server = sys.argv[3]

	# create factory protocol and application
	f = LampstandFactory(sys.argv[1], sys.argv[2])

	# connect factory to this host and port
	reactor.connectTCP(server, 6667, f)

	# run bot
	reactor.run()
