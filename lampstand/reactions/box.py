import re, time, urllib, sys
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

		print "[Box] called "

		sock = urllib.urlopen('http://www.warehouse23.com/basement/box/index.html')
		box = sock.read() 

		result = 'You find: ' + re.findall('<p>\n(.*)\n</p>', box, re.MULTILINE)[0];		

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