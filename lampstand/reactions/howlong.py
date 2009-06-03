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
		self.channelMatch = re.compile('%s. how long (until|since) (.*?)\?' % connection.nickname, re.IGNORECASE)
		self.privateMatch = re.compile('how long (until|since) (.*?)\?', re.IGNORECASE)
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
		connection.msg(user, self.howLong(match).encode('ascii'))


	def howLong(self, match):

		print "[How Long] called with '%s'" % match[0][1]
		
		

		eventSearch = match[0][1]
		eventName = match[0][1]

		aliases = { 'cunts do christmas' : 'Havocstan Midwinter Festival'}
		if aliases.has_key(eventName.lower()):
			print "found alias"
			eventSearch = aliases[eventName.lower()]


		if (match[0][0] == "until"):
			print "Until match"
			firstTry = (">", "asc")
			thenTry = ("<", "desc")
		else:
			print "since match: %s " % match
			firstTry = ("<", "desc")
			thenTry = (">", "asc")

		cursor = self.dbconnection.cursor()
			
		# First, try direct description matches. First in the future (past if it's since)...	
		rawquery = 'SELECT datetime, description, class, datetime_end, UNIX_TIMESTAMP(datetime) as datetime_epoch, UNIX_TIMESTAMP(datetime_end) as datetime_end_epoch FROM events where description LIKE %%s and datetime %s now() order by datetime %s'
		
		query = rawquery % (firstTry[0], firstTry[1])
		
		cursor.execute(query, (eventSearch, ) )
		event = cursor.fetchone()

		# Second, try Description matches in the past (future if it's since)...
		if event == None:
			query = rawquery % (thenTry[0], thenTry[1])
			cursor.execute(query, (eventSearch, ) )
			event = cursor.fetchone()


		# Now set up the class query:
		rawquery =	'SELECT datetime, description, class, datetime_end, UNIX_TIMESTAMP(datetime) as datetime_epoch, UNIX_TIMESTAMP(datetime_end) as datetime_end_epoch FROM events where class LIKE %%s and datetime %s now() order by datetime %s'

		# Third, try Class matches in the future (past if it's since)...
		if event == None:
			query = rawquery % (firstTry[0], firstTry[1]) 
			cursor.execute(query, (eventSearch, ) )
			event = cursor.fetchone()
			
		# Fourth, try Class matches in the past (future if it's since)...
		if event == None:
			query = rawquery % (thenTry[0], thenTry[1]) 
			cursor.execute(query, (eventSearch, ) )
			event = cursor.fetchone()
		
		# Then give up
		if event == None:
			return "No idea, sorry. There's a list of stuff I know about at http://www.maelfroth.org/events.php"
			
		print event
		eventName  = event[1]

		# 0 datetime, 1 description, 2 class, 3 date_end, 4 date_epoch, 5 date_end_epoch
		
		current_time = time.time()

		if(event[5] == None):
			print "Using is (No time out data)"
			timing_position = "i"
			eventTime = int(event[4])
		elif (int(event[4]) > current_time):
			print "Using time in"
			timing_position = "start"
			eventTime = int(event[4])
		elif event[5]:
			print "Using time out"
			timing_position = "end"
			eventTime = int(event[5])
		else:
			print "Using time in (No time out data)"
			timing_position = "i"
			eventTime = int(event[4])

		#eventName = event[1]
		eventClass = event[2]
		
		if (eventTime < current_time):
			swap = current_time
			current_time = eventTime
			eventTime = swap
			returnformat = "%s %s %s%s%s ago"
			if timing_position == 'i':
				timing_position = 'was'
			else:
				timing_position = "%sed" % timing_position
		else:
			returnformat = "%s %ss in %s%s%s"


		days = int((eventTime - current_time) / (60*60*24));
		remainder = (eventTime - current_time) % (60*60*24);
		hours = remainder / (60*60)
		remainder = (eventTime - current_time) % (60*60);
		minutes = remainder / 60

		if (days < 5):
			hours = hours + (24*days)
			days = 0;

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

		print returnformat % (eventName, timing_position, days_message, hours_message, minutes_message)

		return returnformat % (eventName, timing_position, days_message, hours_message, minutes_message)
