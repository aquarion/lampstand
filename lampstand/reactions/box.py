import re, time, urllib, sys
import random
import lampstand.reactions.base
from lampstand.tools import splitAt

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Box'

	cooldown_number   = 5
	cooldown_time     = 600
	uses              = []

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. Open the box' % connection.nickname, re.IGNORECASE)

	def channelAction(self, connection, user, channel, message):


		if self.overUsed():
			connection.msg(channel, "I'm out of boxes, new delivery shortly.")
			return

		#connection.msg(channel, "Sorry, %s, the warehouse is on strike, and boxes aren't available" % user)
		#return
		
		print "[Box] called "

		level = random.randint(1,5);


		sock = urllib.urlopen('http://www.warehouse23.com/basement/box/index.html?level=%d' % level)
		box = sock.read() 

		description = re.findall('<p>\n(.*)\n</p>', box, re.MULTILINE)[0];		

		result = 'In a box on level %d there is %s ' % (level, description)

		result = ' '.join(result.split('\n'))

		result = re.sub(r'<[^>]*?>', '', result) 

		self.updateOveruse()

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

		return True
