import re, time, random, sys, string, datetime
import lampstand.reactions.base
import dateutil.parser
from subprocess import *
from lampstand import tools

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'When Is'

	#@todo: "How long since $specific event"
	#@todo: "How long since Maelstrom?"
	#@todo: Custom events, player events, data driven thing (ical export?)

	cooldown_number = 5
	cooldown_time   = 600
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. when (is|was) (.*?)\?' % connection.nickname, re.IGNORECASE)
		self.privateMatch = re.compile('when (is|was) (.*?)\?', re.IGNORECASE)
		self.dbconnection = connection.dbconnection


	def channelAction(self, connection, user, channel, message):

		if self.overUsed():
			connection.msg(channel, "Shortly sooner than when you last asked.")
			return

		match = self.channelMatch.findall(message);


	 	self.updateOveruse()

		connection.msg(channel, self.howLong(match).encode('ascii'))
		return True

	def privateAction(self, connection, user, channel, message):
		match = self.privateMatch.findall(message);
		connection.msg(user, self.howLong(match).encode('ascii'))


	def howLong(self, match):

		print "[When is] called with '%s'" % match[0][1]
		
		

		eventSearch = match[0][1]
		eventName   = match[0][1]
		tiswas      = match[0][0]

		if (match[0][0] == "is"):
			print "Until match"
			firstTry = (">", "asc")
			thenTry = ("<", "desc")
		else:
			print "since match: %s " % match
			firstTry = ("<", "desc")
			thenTry = (">", "asc")

		cursor = self.dbconnection.cursor()
			
		# First, try direct description matches. First in the future (past if it's since)...	
                rawquery = 'SELECT datetime, description, class, datetime_end, UNIX_TIMESTAMP(datetime) as datetime_epoch, UNIX_TIMESTAMP(datetime_end) as datetime_end_epoch, url FROM events where (description LIKE %%s or aliases LIKE %%s) and datetime %s now() order by datetime %s'
                

		query = rawquery % (firstTry[0], firstTry[1])
		
		cursor.execute(query, (eventSearch, "%%%s%%" % eventSearch) )
		event = cursor.fetchone()

		# Second, try Description matches in the past (future if it's since)...
		if event == None:
			query = rawquery % (thenTry[0], thenTry[1])
			cursor.execute(query, (eventSearch, "%%%s%%" % eventSearch) )
			event = cursor.fetchone()


		# Now set up the class query:
		rawquery =	'SELECT datetime, description, class, datetime_end, UNIX_TIMESTAMP(datetime) as datetime_epoch, UNIX_TIMESTAMP(datetime_end) as datetime_end_epoch, url FROM events where class LIKE %%s and datetime %s now() order by datetime %s'

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
		eventClass = event[2]
	
		# Then give up
		if event == None:
			return "No idea, sorry. There's a list of stuff I know about at http://www.maelfroth.org/events.php"
			
		print event
		eventName  = event[1]

		# 0 datetime, 1 description, 2 class, 3 date_end, 4 date_epoch, 5 date_end_epoch
		
		current_time = time.time()

		timeformat = "%A %d %B %Y at %H:%M";

		if(event[5] == None or event[5] == 0):
			start = datetime.datetime.fromtimestamp(event[4]).strftime(timeformat);
			message = "%s: %s %s %s" % (eventClass, eventName, tiswas, start);
			print "Using is (No time out data)"
		else:
			start = datetime.datetime.fromtimestamp(event[4]).strftime(timeformat)
			end   = datetime.datetime.fromtimestamp(event[5]).strftime(timeformat)
			message = "%s: %s %s from %s to %s" % (eventClass, eventName, tiswas, start, end);
			print "Using time in (No time out data)"

		if event[6]:
			message += ", more info at %s" % event[6]

		return message
