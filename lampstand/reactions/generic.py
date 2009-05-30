import re, time, random
import lampstand.reactions.base

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	
	__name = 'Generic'
	
	cooldown_number = 2
	cooldown_time   = 360
	uses = []

	def __init__(self, connection):

		self.reactions = (('.*pokes %s', '', "Do I look like a facebook user? Fuck off."),
			('%s. What is best in life?', 'Not Telling', (
				"To crush your enemies, see them driven before you, and to hear the lamentations of their women!", 
				"To obsess over and romanticise your enemies, see them get in a taxi you wanted, and to hear their girlfriends enclosed in plastic", 
				"To crush your enemies, see them driven before you, and to hear the laminations of their women!",
				"To crush your anemones, see them driven before you, and to hear the lamentations of their women!"
				)),
			('%s. Take the money', "Thank you, I shall.", "Already did."),
			('%s. How long til .*\?', "Two hours.", "That's tomorrow, isn't it?"),
			('%s. Open the pod bay doors', "I think you have your AIs confused.", "I can't do that, Dave"),
			('%s. Where do you get the boxes?', "", "The boxes come from SJGames' http://www.warehouse23.com/basement/ Level One")
			)

		self.channelMatch = []
		self.privateMatch = []

		for reaction in self.reactions:
			self.channelMatch.append(re.compile(reaction[0] % connection.nickname, re.IGNORECASE))
			self.privateMatch.append(re.compile(reaction[0] % connection.nickname, re.IGNORECASE))

	def channelAction(self, connection, user, channel, message, matchindex):
		print "[Generic Reaction] called"


		if self.overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			if self.reactions[matchindex][1] != '':
				connection.msg(channel, self.reactions[matchindex][1])
				return


		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

		if self.reactions[matchindex][2] != '':
			if type(self.reactions[matchindex][2]) == type(tuple()):
				reaction = random.choice(self.reactions[matchindex][2])
			else:
				reaction = self.reactions[matchindex][2]
			connection.msg(channel, reaction)
			return

	def privateAction(self, connection, user, channel, message, matchindex):
		#match = self.privateMatch.findall(message);
		#connection.msg(user, self.howLong(match).encode('ascii'))

		print "[Generic Reaction] called"


		if self.overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			if self.reactions[matchindex][1] != '':
				connection.msg(user, self.reactions[matchindex][1])
				return


		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

		if self.reactions[matchindex][2] != '':
			if type(self.reactions[matchindex][2]) == type(tuple()):
				print "list"
				reaction = random.choice(self.reactions[matchindex][2])
			else:
				print "Not list"
				print type(self.reactions[matchindex][2])
				reaction = self.reactions[matchindex][2]
			connection.msg(user, reaction)
			return

