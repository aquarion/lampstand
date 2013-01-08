import re, time, urllib, sys
import random
import lampstand.reactions.base
from lampstand.tools import splitAt
import simplejson

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Box'

	cooldown_number   = 2
	cooldown_time     = 300
	uses              = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. Open the box' % connection.nickname, re.IGNORECASE)

	def channelAction(self, connection, user, channel, message):


		if self.overUsed():
			connection.message(channel, "I'm out of boxes, new delivery shortly.")
			return

		print "[Box] called "


		box = simplejson.load(urllib.urlopen("http://warehousebasement.com/api.php"))

		print box

		result = 'In a box on level %s you find %s' % (box['level'], box['description'])

		connection.message(channel, "%s" % result)

		return True
