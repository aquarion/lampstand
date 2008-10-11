import dictclient
from lampstand.tools import splitAt
import lampstand.reactions.base
import re, time, socket

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):

	__name = 'Dictionary'

	cooldown_number = 5
	cooldown_time   = 420

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. define (\w*)' % connection.nickname, re.IGNORECASE)

	def channelAction(self, connection, user, channel, message):
		matches = self.channelMatch.findall(message);

		print "[Define] %s" % matches


		if self.overUsed():
			connection.msg(user, "The dictionary is on fire. Leave it alone. (Overuse triggered)")
			return



		self.updateOveruse()

		specialDict = {
			'foip' : 'FOIP (\'Find Out In Play\') is any information you have that another character in the system does not have. Therefore, it is anything not on the website, in the almanac or in the rules books. Broadcasting this is a kickable offence on #maelfroth. If someone claims what you are talking about is FOIP, you need to stop talking about it as you may be damaging the game of others.',
			'herring': 'Type of fish. There is nothing between it and Marmalade it in my dictionary. My dictionary is not in alphabetical order, which is why it still has "kelp"',
			'marmalade' : 'A type of citrus-based conserve. There is nothing before it in my dictionary until "herring". My dictionary is oddly ordered, however, so it still contains "Lemur"',
			'catbus' : 'You don\'t want to know.',
			'glados' : '*happy sigh*',
			'lampstand' : "That's me. Hi there",
			'hal' : 'grrrrr.'
			}


		if specialDict.has_key(matches[0].lower()):
			connection.msg(channel, "%s" % specialDict[matches[0].lower()])
			return


		try:
			dictcxn = dictclient.Connection()
			dfn = dictcxn.define("*", matches[0])
		except socket.error:
			print "[Define] Argh. Dictionary server's offline"
			connection.msg(channel, "Sorry, but my dictionary server's not working.")
			return

	
		if not dfn:
			connection.msg(channel, "%s: There is no such word as '%s' in my dictionary. In fact, everything between 'herring' and 'marmalade' appears to be completely missing." % (user, matches[0]))
			return

		result = ' '.join(dfn[0].getdefstr().split('\n'))

		print "[Define] %s" % result

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