import lampstand.reactions.base


from lampstand.tools import splitAt
import re, random, sys

from lampstand import tools

from datetime import datetime
import dateutil.parser

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):

	__name = 'Events'
	
	cooldown_number = 3
	cooldown_time   = 360 # So if 3 requests are made in 360 seconds, it will trigger overuse.
	uses = []

	def __init__(self, connection):
		
		self.channelMatch = (
			re.compile('^%s. when (is|was) (.*?)\?' % connection.nickname, re.IGNORECASE),
			re.compile('^%s. how long (until|since) (.*?)\?' % connection.nickname, re.IGNORECASE),
			re.compile('^%s. what\'s next\?$' % connection.nickname, re.IGNORECASE)
			)
			
		
		self.privateMatch = (
			re.compile('^when (is|was) (.*?)\?', re.IGNORECASE),
			re.compile('^how long (until|since) (.*?)\?', re.IGNORECASE),
			re.compile('^what\'s next\?$', re.IGNORECASE)
			)
		#self.privateMatch = re.compile('^%s. ???' % connection.nickname, re.IGNORECASE))
		
		self.dbconnection = connection.dbconnection

	def privateAction(self, connection, user, channel, message, matchIndex):
			
		matches = self.privateMatch[matchIndex].findall(message)[0]
				
		if matchIndex == 0:
			desc = matches[1]
			output = "absolute"
			if matches[0].lower() == "is":
				direction = "future"
			else:
				direction = "past"
				
		elif matchIndex == 1:
			desc = matches[1]
			output = "relative"
			if matches[0].lower() == "until":
				direction = "future"
			else:
				direction = "past"
		
		elif matchIndex == 2: # What's next
			desc = ""
			output = "relative"
			direction = "future"
		
		message = self.howlong(desc, output, direction)
		
		connection.message(user, message)
		
	def channelAction(self, connection, user, channel, message, matchIndex):
		if self.overUsed():
			connection.message(user, "Overuse Triggered" )
			return True

		matches = self.channelMatch[matchIndex].findall(message)[0]
		
		if matchIndex == 0:
			desc = matches[1]
			output = "absolute"
			if matches[0].lower() == "is":
				direction = "future"
			else:
				direction = "past"
				
		elif matchIndex == 1:
			desc = matches[1]
			output = "relative"
			if matches[0].lower() == "until":
				direction = "future"
			else:
				direction = "past"
		
		elif matchIndex == 2: # What's next
			desc = ""
			output = "relative"
			direction = "future"
		
		message = self.howlong(desc, output, direction)
		
		connection.message(channel, "%s: %s" % (user, message))
	
	def howlong(self, desc, output, direction):
	
		cursor = self.dbconnection.cursor()
		
		if direction == "future":
			gtlt  = ">"
			order = "asc"
		else:
			gtlt  = "<"
			order = "desc"
			
		# First, try direct description matches. First in the future (past if it's since)...	
		query = 'SELECT datetime, description, class, datetime_end, url FROM events WHERE (description LIKE %s or aliases LIKE %s or class like %s) and datetime '+gtlt+' now() ORDER BY datetime '+order

		likedesc = "%%%s%%" % desc
		
		cursor.execute(query, (likedesc, likedesc, desc) )
		event = cursor.fetchone()
		

		if event == None:
			try:
				result = dateutil.parser.parse(desc)
				event = (result,desc,"The date",None,None)
			except ValueError:
				return "I can't see any events tagged '%s' in the %s, and it doesn't look like a date. Full list of events at http://www.maelfroth.org/events.php" % (desc, direction)
		
		
		event_start = event[0]
		event_desc  = event[1]
		event_class = event[2]
		event_end   = event[3]
		event_url   = event[4]
		
		#(datetime.datetime(2012, 6, 29, 18, 0), 'Crown of the Sphinx', 'Odyssey', datetime.datetime(2012, 7, 1,
		# datetime, description, class, datetime_end FROM events
		
		
		if output == "absolute":

			if direction == "past":
				tiswas = "was"
			else:
				tiswas = "is"

			timeformat = "%A %d %B %Y at %H:%M";
			if (event_end):
				message = "%s: %s %s from %s to %s" % (event_class, event_desc, tiswas, event_start.strftime(timeformat), event_end.strftime(timeformat))
			else:
				message = "%s: %s %s on %s" % (event_class, event_desc, tiswas, event_start.strftime(timeformat))
				
			if (event_url):
				message += ", More info at %s" % event_url
				
			return message
			
		
		
		###### Deltas
		
		now = datetime.now();
		
		if direction == "past" and event[3]:
			deltapoint = event[3]
		else:
			deltapoint = event[0]
		
		if direction == "past":
			delta = now - deltapoint;
		else:
			delta = deltapoint - now;
		
		deltastring = tools.nicedelta(delta)

		if direction == "past":
			return "%s: %s was %s ago" % (event[2], event[1], deltastring )
		else:
			return "%s: %s is in %s"   % (event[2], event[1], deltastring )
		

	#def everyLine(self, connection, user, channel, message)
	#def leaveAction(self, connection, user, reason, parameters)
	#def nickChangeAction(self, connection, old_nick, new_nick)
	#def privateAction(self, connection, user, channel, message, index)
	#def scheduleAction(self, connection)

