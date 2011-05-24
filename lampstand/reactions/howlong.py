import re, time, random, sys, string, datetime
import lampstand.reactions.base
import dateutil.parser
from subprocess import *
from lampstand import tools

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
	timein = "decimal"

	def __init__(self, connection):
		self.channelMatch = [re.compile('%s. how long (until|since) (.*?)\??$' % connection.nickname, re.IGNORECASE),re.compile('%s. how long\?$' % connection.nickname, re.IGNORECASE), re.compile('%s. what\'s next\?$' % connection.nickname, re.IGNORECASE), re.compile("%s: How Long times in (.*)" % connection.nickname, re.IGNORECASE) ]
		self.privateMatch = re.compile('how long (until|since) (.*?)\??$', re.IGNORECASE)
		self.dbconnection = connection.dbconnection


	def channelAction(self, connection, user, channel, message, matchIndex):

		print "[HOWLONG] Matched with %s" % matchIndex;


		if self.overUsed():
			connection.msg(channel, "Shortly sooner than when you last asked.")
			return

		print matchIndex;

		if matchIndex == 3:
			match = self.channelMatch[3].findall(message);

			if (tools.convertNiceTime(1, match[0]) == False):
				connection.msg(channel, "%s: I don't support that time format. Try: dec, oct, hex, roman" % user)
				return True

			self.timein = match[0]
			print "Set timein to %s" % self.timein
			connection.msg(channel, "%s: Done" % user)
			return True;

		if(matchIndex == 0):
			match = self.channelMatch[0].findall(message);
		else:
			match = [["until", "%"]]

	 	self.updateOveruse()

		connection.msg(channel, self.howLong(match).encode('ascii'))
		return True

	def privateAction(self, connection, user, channel, message):
		match = self.privateMatch.findall(message);
		connection.msg(user, self.howLong(match).encode('ascii'))


	def howLong(self, match):

		print "[How Long] called with '%s'" % match[0][1]
		
		eventSearch = match[0][1]
		eventName = match[0][1]
	
		if eventName.lower() == "downtime opens" or eventName.lower() == "downtime returns":
			return "FOIP."

		if eventName.lower() == "downtime closes" or eventName.lower() == "panic":
			return "Shortly after your mum."


		if (match[0][0] == "until"):
			print "Until match"
			firstTry = (">", "asc")
			thenTry = ("<", "desc")
			tiswas = "is"
		else:
			print "since match: %s " % match
			firstTry = ("<", "desc")
			thenTry = (">", "asc")
			tiswas = "was"

		cursor = self.dbconnection.cursor()
			
		# First, try direct description matches. First in the future (past if it's since)...	
		rawquery = 'SELECT datetime, description, class, datetime_end, UNIX_TIMESTAMP(datetime) as datetime_epoch, UNIX_TIMESTAMP(datetime_end) as datetime_end_epoch FROM events where (description LIKE %%s or aliases LIKE %%s) and datetime %s now() order by datetime %s'

		try:
			result = dateutil.parser.parse(eventSearch)
			event = (result,eventSearch,"",None,time.mktime(result.timetuple()),None)
		except ValueError: 		

			query = rawquery % (firstTry[0], firstTry[1])
		
			cursor.execute(query, (eventSearch, "%%%s%%" % eventSearch) )
			event = cursor.fetchone()
	
			print query % (eventSearch, "%%%s%%" % eventSearch)
		
			# Second, try Description matches in the past (future if it's since)...
			if event == None:
				query = rawquery % (thenTry[0], thenTry[1])
				cursor.execute(query, (eventSearch, "%%%s%%" % eventSearch) )
				event = cursor.fetchone()
				if tiswas == "was":
					tiswas = "is"
				else:
					tiswas = "was"

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


		# Aborted attempt to handle arbitary dates
		#if event == None:
		#	print "Attempting to parse %s as date" % eventSearch
		#	try:
		#		cmd = "'echo strtotime(\"%s\")\;'" % eventSearch
		#		#print cmd
		#		#sysres = subprocess.Popen(["/usr/bin/php",cmd ], stdout=subprocess.PIPE).communicate()
		#		output = Popen(["/usr/bin/php", "-r", cmd], stdout=PIPE).communicate()[0]
		#		print output
		#		#sysres = os.system(cmd);
		#		print "Sysres: %s " % sysres;
		#		if not sysres == 0:
		#			eventDate = datetime.datetime.fromtimestamp(sysres);
		#			#epoch = time.mktime(eventDate.timetuple();
		#			event = (eventDate, eventDate.isoformat(" "), "Time", None, epoch, None)
		#	except ValueError:
		#		pass
		
		print event
	
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
			returnformat = "%s %s %s ago"
			if timing_position == 'i':
				timing_position = 'was'
			else:
				timing_position = "%sed" % timing_position
		else:
			returnformat = "%s %ss in %s"


		timedelta = (eventTime - current_time)


		deltastring = tools.niceTimeDelta(timedelta, self.timein)

		print returnformat % (eventName, timing_position, deltastring)

		return returnformat % (eventName, timing_position,deltastring)
