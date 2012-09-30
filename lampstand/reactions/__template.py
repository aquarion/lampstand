from lampstand import eightball
import lampstand.reactions.base


from lampstand.tools import splitAt
import re, time, random, sys

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):

	__name = 'PackageName'
	
	cooldown_number = 3
	cooldown_time   = 360 # So if 3 requests are made in 360 seconds, it will trigger overuse.
	uses = []

	def __init__(self, connection):
		#self.channelMatch = re.compile('^%s. ???' % connection.nickname, re.IGNORECASE))
		#self.privateMatch = re.compile('^%s. ???' % connection.nickname, re.IGNORECASE))


	def channelAction(self, connection, user, channel, message, index):
		
		if self.overUsed():
			connection.message(user, "Overuse Triggered" )
			return True


	#def everyLine(self, connection, user, channel, message)
	#def leaveAction(self, connection, user, reason, parameters)
	#def nickChangeAction(self, connection, old_nick, new_nick)
	#def privateAction(self, connection, user, channel, message, index)
	#def scheduleAction(self, connection)
