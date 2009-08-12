import lampstand.reactions.base

from lampstand.tools import splitAt
import re, time, random, sys

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):


	__name = 'Choose'
	
	cooldown_number = 6
	cooldown_time   = 360
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('^%s. (.* or .*)' % connection.nickname, re.IGNORECASE)
		self.privateMatch = re.compile('(.* or .*)\??$', re.IGNORECASE)

	def channelAction(self, connection, user, channel, message):
		print "[Choose] called"


		if self.overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(channel, "I'm not running your life for you, go away." )
			return
		
		self.updateOveruse()
		
		match = self.channelMatch.findall(message)
		
		reaction = self.choose(match[0])
		if reaction.lower() == "death" and user.lower() != "aquarion":
			connection.kick(channel,user, "Death")
		else:
			connection.msg(channel, "%s: %s" % (user, reaction))


	def privateAction(self, connection, user, channel, message):
		print "[Choose] called"


		if self.overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			connection.msg(user, "I'm not running your life for you, go away." )
			return
		
		self.updateOveruse()
		
		match = self.privateMatch.findall(message)
		print "Match: %s" % match

		reaction = self.choose(match[0])
		connection.msg(user, "%s: %s" % (user, reaction))

	def choose(self, message):
		if message[-1:] == "?":
			message = message[:-1]

		if message[0:7].lower() == "choose ":
			message = message[7:]

		print message[0:7]
		print message
		orsplit = message.split(" or ")

		choose = []

		for thing in orsplit:
			lst = thing.split(", ")
			for x in lst:
				choose.append(x)
		print choose

		for thing in choose:
			if thing.lower() == "glados":
				return "GLaDOS. Obviously"

			if thing.lower() == "hal":
				choose.remove(thing)

		print choose
		return random.choice(choose)
