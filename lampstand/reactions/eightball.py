from lampstand import eightball
import lampstand.reactions.base


from lampstand.tools import splitAt
import re, time, random, sys

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):


	__name = 'Eightball'
	
	cooldown_number = 6
	cooldown_time   = 360
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('^%s.  ?ask the 8.ball' % connection.nickname, re.IGNORECASE)


	def channelAction(self, connection, user, channel, message):
		print "[8Ball] called"


		if self.overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(user, "The 8-ball says: 'Find a new prophet, I quit.', I'd give it a while to cool down." )
			return True


		self.updateOveruse()
		
		connection.msg(channel, "%s: %s" % (user, eightball.question()) )

		return True
