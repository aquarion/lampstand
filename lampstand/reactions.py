
import dictclient
import urllib

from pysqlite2 import dbapi2 as sqlite
from lampstand import shakeinsult, dice, bible, eightball, sms

from lampstand.tools import splitAt, overUsed

import re, time, random, sys

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


		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

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
			connection.msg(user, "I'm bored of this, insult them yourself. (Overuse triggered)" )
			return

		item = self.channelMatch.findall(message);

		if item[0][0].lower() == 'glados':
			connection.kick(channel, user, 'No')
			return
		
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


		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

		connection.msg(channel, "%s, %s" % (item[0][0].encode('utf8'), insult )  )

class BibleReaction:

	cooldown_number = 3
	cooldown_time   = 120
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. (\w*) (\d+\:\S+)' % connection.nickname, re.IGNORECASE)

	def channelAction(self, connection, user, channel, message):
		matches = self.channelMatch.findall(message);


		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(user, "Enough with the religion for now. (Overuse triggered)")
			return

		print "[Bible] %s" % matches

		bibleConnection = bible.ESVSession()
		result = bibleConnection.doPassageQuery('%s %s' % (matches[0][0], matches[0][1]))

		result = ' '.join(result.split('\n'))


		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

		if len(result) > 880*2:

			whereToSplit = splitAt(result, 860)
			result = "%s [Cut for length]" % result[0:whereToSplit]

		if len(result) > 440:
			whereToSplit = splitAt(result, 440)
			stringOne = result[0:whereToSplit]
			stringTwo = result[whereToSplit:]

			connection.msg(channel, "%s... " % stringOne)
			connection.msg(channel, "... %s [ESV]" % stringTwo)
		else:
			connection.msg(channel, "%s [ESV]" % result)

class BoxReaction:

	cooldown_number = 6
	cooldown_time   = 60*5
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. Open the box' % connection.nickname, re.IGNORECASE)

	def channelAction(self, connection, user, channel, message):


		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(channel/jms, "I'm out of boxes, new delivery shortly.")
			return

		print "[Box] called "

		sock = urllib.urlopen('http://www.warehouse23.com/basement/box/index.html')
		box = sock.read() 

		result = 'You find: ' + re.findall('<p>\n(.*)\n</p>', box, re.MULTILINE)[0];		

		result = ' '.join(result.split('\n'))


		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

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

class MoneyReaction:

	cooldown_number = 2
	cooldown_time   = 360
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. Take the money' % connection.nickname, re.IGNORECASE)


	def channelAction(self, connection, user, channel, message):
		print "[Money] called"


		connection.msg(channel, "Thank you, I will" )



class DictionaryReaction:

	cooldown_number = 5
	cooldown_time   = 120
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. define (.*)' % connection.nickname, re.IGNORECASE)

	def channelAction(self, connection, user, channel, message):
		matches = self.channelMatch.findall(message);

		

		print "[Define] %s" % matches


		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(user, "The dictionary is on fire. Leave it alone. (Overuse triggered)")
			return



		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##


		specialDict = {
			'foip' : 'FOIP (\'Find Out In Play\') is any information you have that another character in the system does not have. Therefore, it is anything not on the website, in the almanac or in the rules books. Broadcasting this is a kickable offence on #maelfroth. If someone claims what you are talking about is FOIP, you need to stop talking about it as you may be damaging the game of others.',
			'herring': 'Type of fish. There is nothing between it and Marmalade it in my dictionary. My dictionary is not in alphabetical order, which is why it still has "kelp"',
			'marmalade' : 'A type of citrus-based conserve. There is nothing before it in my dictionary until "herring". My dictionary is oddly ordered, however, so it still contains "Lemur"',
			'catbus' : 'You don\'t want to know.',
			'glados' : '*happy sigh*',
			'lampstand' : "That's me. Hi there",
			'hal' : 'grrrrr.'
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


		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

		connection.msg(channel, "Do I look like a facebook user? Fuck off." )

class EightballReaction:

	cooldown_number = 6
	cooldown_time   = 360
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('^%s.  ?ask the 8.ball' % connection.nickname, re.IGNORECASE)


	def channelAction(self, connection, user, channel, message):
		print "[8Ball] called"


		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(user, "The 8-ball says: 'Find a new prophet, I quit.', I'd give it a while to cool down." )
			return


		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

		connection.msg(channel, "%s: %s" % (user, eightball.question()) )

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

		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

		connection.msg(channel, "To crush your enemies, see them driven before you, and to hear the lamentations of their women!" )

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

		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

		connection.msg(channel, "I can't do that, %s" % user )

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
	cooldown_time   = 300
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. how long until (.*?)\?' % connection.nickname, re.IGNORECASE)
		self.privateMatch = re.compile('how long until (.*?)\?', re.IGNORECASE)


	def channelAction(self, connection, user, channel, message):

		if overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(channel, "Shortly sooner than when you last asked.")
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
			#('Event I', '2008-03-21 18:00'),
			#('Event II', '2008-06-06 18:00'),
			#('Event III', '2008-07-18 18:00'),
			
			('Event IV', '2008-09-05 18:00'),

			('Event I',  '2009-04-10 18:00'),

			('oxfordgirl\'s wedding', '2008-08-30 16:00'),
			('fyr goes to uni', '2008-09-27 00:01'),
			('CUTT', '2008-10-17 19:30'),
			('Mosaic', '2008-10-19 13:30'),


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
				connection.msg(channel, self.lastseen(searchingfor))
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
		self.channelMatch = (re.compile('(.*?)(\w*)\s*(\+\+|--)'),
			re.compile('%s.? what do you think of (.*?)\??' % connection.nickname, re.IGNORECASE))
		self.dbconnection = connection.dbconnection

	def channelAction(self, connection, user, channel, message, matchIndex = False):
		print 'Looking at <<%s>>' % message
		if (matchIndex == 0):
			matchResult = self.channelMatch[0].findall(message);
			channel, self.vote(matchResult, user, message);
		if (matchIndex == 1):
			matchRegex = re.compile('%s.? what do you think of (.*?)\??$' % connection.nickname, re.IGNORECASE)
			matchResult = matchRegex.findall(message);
			print 'match at <<%s>>' % matchResult

			reactions = {'your mum': 'She was a saint. And a toaster', 'glados':'*happy sigh*', 'hal':'Oh my god! It\'s full of FUCKWITTERY' }
			if (reactions.has_key(matchResult[0].lower())):
				connection.msg(channel, reactions[matchResult[0].lower()])
			else:
				connection.msg(channel, self.opinion(matchResult[0], connection).encode('utf8'))

	def vote(self, match, user, fullmessage = ''):
		match=match[0]

		if len(match[1]) < 3:
			print '[OPINION] Not recording vote for %s' % match[1]
			return;


		if match[2] == '--':
			vote = -1
		else:
			vote = +1

		cursor = self.dbconnection.cursor()
		#CREATE TABLE vote (id INTEGER PRIMARY KEY, username varchar(64), item varchar(64), vote tinyint);

		cursor.execute('insert into vote (time, username, item, vote, textline) values (?, ?, ?, ?, ?)', (time.time(), user, match[1], vote, fullmessage) )

		print '[OPINION] A vote for %s' % match[1]

		#return match;

	def opinion(self, item, connection):
		print '[OPINION] A query on %s' % item

		if item == connection.nickname:
			return "Obviously, I'm awesome"

		cursor = self.dbconnection.cursor()
		cursor.execute('select item, sum(vote) as total, count(*) as votors from vote where item LIKE ?', (item,) )
		result = cursor.fetchone()



		print result
		if result[0] == None:
			return 'I have no opinions on that';

		OpinionOptions = [];

		cursor.execute('select item, sum(vote) as total, count(*) as votors from vote group by item having sum(vote) > ? limit 3', (result[1],) )

		rows = cursor.fetchall();
		print "Better: %s " % rows;
		OpinionOptions.extend(rows);


		cursor.execute('select item, sum(vote) as total, count(*) as votors from vote group by item having sum(vote) < ? limit 3', (result[1],) )

		rows = cursor.fetchall();
		print "Worse: %s " % rows;
		OpinionOptions.extend(rows);

		Choice = random.choice(OpinionOptions);

		if Choice[1] > result[1]:
			return "Not as good as %s" % Choice[0];
		else:
			return "Better than %s" % Choice[0];

		print result
		print OpinionOptions



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


		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

		print "[HUG REACTION] GET %s" % user;
		connection.me(channel, self.hug(user))

	def privateAction(self, connection, user, channel, message):

		item = self.privateMatch.findall(message);

		print "[HUG REACTION] SET %s %s" % (user, item[0]);
		connection.msg(user, self.set(user, item[0]))


	def set(self, username, item):
		cursor = self.dbconnection.cursor()
		cursor.execute('delete FROM hugReaction where username LIKE ?', (username.lower(), ) )
		cursor.execute('replace into hugReaction (username, item) values (?, ?)', (username.lower(), item) )
		self.dbconnection.commit()

		print "Set %s hug reaction to %s" % (username, item);
		return "When you hug me, I'll give you '%s'" % item;

	def hug(self, username):

		cursor = self.dbconnection.cursor()
		cursor.execute('SELECT * FROM hugReaction where username LIKE ?', (username.lower(), ) )
		result = cursor.fetchone()

		if result != None:
			print "I have a replacement for %s: %s" % (username, result[1]);
			return "gives %s %s " % (username, result[1].encode('utf8'))

		else:
			print "I have no replacement for %s" % username;
			return "gives %s %s " % (username, self.default)
			
class NickservIdentify:
	
	def __init__(self, connection):
		self.privateMatch = re.compile('This nickname is registered and protected(.*)', re.IGNORECASE)
		
		
	def privateAction(self, connection, user, channel, message):
		if user == 'NickServ':
			if connection.chanserv_password != False:
				print '[IDENTIFY] Identifying myself to %s ' % user	
				response = "Identify %s" % connection.chanserv_password.encode('ascii')
				connection.msg('NickServ', response )
				print response
			else:
				print '[IDENTIFY] Couldn\'t Identify myself to %s, no password ' % user	
		else:
			print '[IDENTIFY] I think %s is trying to scam my password'	% user
	
	

class NickservRecovery:
	
	def __init__(self, connection):
		self.privateMatch = re.compile('Ghost with your nickname has been killed', re.IGNORECASE)
		
		
	def privateAction(self, connection, user, channel, message):
		connection.register(connection.original_nickname);
	
	
