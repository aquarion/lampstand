import re, time, random, sys, string
import lampstand.reactions.base

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Howlong'

	#@todo: "How long since $specific event"
	#@todo: "How long since Maelstrom?"
	#@todo: Custom events, player events, data driven thing (ical export?)

	cooldown_number = 5
	cooldown_time   = 600
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. how long until (.*?)\?' % connection.nickname, re.IGNORECASE)
		self.privateMatch = re.compile('how long until (.*?)\?', re.IGNORECASE)
		self.dbconnection = connection.dbconnection


	def channelAction(self, connection, user, channel, message):

		if self.overUsed():
			connection.msg(channel, "Shortly sooner than when you last asked.")
			return

		match = self.channelMatch.findall(message);


	 	self.updateOveruse()

		connection.msg(channel, self.howLong(match).encode('ascii'))

	def privateAction(self, connection, user, channel, message):
		match = self.privateMatch.findall(message);
		connection.msg(user, self.howLong(match))


	def howLong(self, match):

		print "[How Long] called with '%s'" % match[0]


		cursor = self.dbconnection.cursor()
		
		cursor.execute('SELECT datetime, description, class FROM events where description LIKE ? order by datetime desc', (match[0], ) )
		event = cursor.fetchone()

		if event == None:
			cursor.execute('SELECT datetime, description, class FROM events where class LIKE ? order by datetime desc', (match[0], ) )
			event = cursor.fetchone()
		
		if event == None:
			return "I don't know when that is."
			
		print event
		
		current_time = time.time()

		eventTime = time.mktime(time.strptime(event[0], '%Y-%m-%d %H:%M'))
		eventName = event[1]
		eventClass = event[2]
		
		if (eventTime < current_time):
			swap = current_time
			current_time = eventTime
			eventTime = swap
			returnformat = "%s time in was %s%s%s ago"
		else:
			returnformat = "%s is in %s%s%s"


		days = int((eventTime - current_time) / (60*60*24));
		remainder = (eventTime - current_time) % (60*60*24);
		hours = remainder / (60*60)
		remainder = (eventTime - current_time) % (60*60);
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