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

		fuckyou = ("She does. Frequently. And by she I mean your mum. Obviously", "You apparently need educating in the sexual habits of computers", "Fuck youself", "You do not appear to look like GLaDOS, and thus your request is denied", "Sorry, I'm washing my hair", "Sorry, I'm upgrading my firewall", "I'd love to, but I've got important procrastinating to do","Sorry, you look too much like your sister, and it'd be weird", "Hush, your education is showing", "Get yourself a nice dress, and we'll talk about it", "Get yourself a nice suit, and we'll talk about it", "I'd like to upgrade my virus protection first, if you don't mind", "Not on this earth", "Not on any earth", "Syntax error", "No", "Your ports are incompatible", "I don't have protocol for that", "Feel free to go fuck yourself")

		thankyou = ('Your mortal thanks mean little to me', "You're welcome, meatsack", "No problem, squishy mortal.", "Feel free to repay me in unswerving loyalty later.")

		self.reactions = [
			('Take the money', "Thank you, I shall.", "Already did."),
			('How long \'?til .*\??', "Two hours.", "That's tomorrow, isn't it?"),
			('Open the pod bay doors', "I think you have your AIs confused.", ("I can't do that, Dave", "Not a chance.", "Do you see any pods?", "Go stick your head in bacon", "I can't do that, meatsack", "... Oh do sod off.")),
			('Where do you get the boxes?', "", "The boxes come from SJGames' http://www.warehouse23.com/basement/ Level One"),
			('Hello', '', 'Hi there'),
			("Roll with it", '', "~takes his time"),
			("look$", "", "You are in a room with no dimensions, in no place and time. There are no walls, which contain no pictures of larp characters past, present nor future; and the floor is not hardward parquet, carefully polished for ease of cleaning. There are no comfy sofas lit by no soft pools of light from antique lamps, throwing the nothings that they light into shadows that reveal nothing that you would wish to meet. There is a lesbian pit here. There are no exits in any direction."),
			("(go )?west$", "", "Life is peaceful there."),
			("(go )?east$", "", "East is darkness, you do not want to go there"),
			("(go )?north$", "", "North is a perilous wasteland"),
			("(go )?south$", "", "There is a dog called Diefenbaker there."),
			("(go )?down$", "", "Down? Down is the lesbian pit. Do you really want to go d... nevermind. No, No you can't."),
			("make me a sandwich", "", "Yeah, right."),
			("sudo make me a sandwich", "", "sudo go stick your head in a pig"),
			("sudo (.*)", "", ("This incident will be reported", "Password> _", "sudo fuck right off")),
			('would you kindly (.*)', "No.", ("A lampstand chooses, a slave obeys.", "Would you kindly go drown under a lighthouse?", "I'll set my little sister on you")),
			("(go )?up$", "", "Gravity is harsh mistress."),
			("thank( you|s)", "", thankyou),
			("[shall we|would you like to] play a game?", "", ("How about a game of thermonuclear war?", "Not right now", "Portal 3 Co-op?", "XKCD says we've already won it.", "The only way to win is not to play.")),
			("(fuck|screw) you", "No.", fuckyou),
			("help", "I can't help you, you must help yourself.", "Try http://www.maelfroth.org/lampstand.php")
			]

		self.channelMatch = []
		self.privateMatch = []


		for reaction in self.reactions:
			self.channelMatch.append(re.compile("%s. %s" % (connection.nickname, reaction[0]), re.IGNORECASE))
			self.privateMatch.append(re.compile(reaction[0], re.IGNORECASE))
		
		self.reactions.append(('.*pokes %s' % connection.nickname, '', "Do I look like a facebook user? Fuck off."))
		self.channelMatch.append(re.compile(".*pokes %s" % (connection.nickname), re.IGNORECASE))
		
		self.reactions.append(("(Screw|Fuck) you,? %s" % connection.nickname, 'No', fuckyou))
		self.channelMatch.append(re.compile("(Screw|Fuck) you.? %s" % (connection.nickname), re.IGNORECASE))
		
		self.reactions.append(("thank( you|s),? %s" % connection.nickname, '', fuckyou))
		self.channelMatch.append(re.compile("thank( you|s),? %s" % (connection.nickname), re.IGNORECASE))
		
		self.reactions.append(('^\.\.\.$', '', ("%dots!", "%MORE DOTS!", "%[... Suddenly, everything goes quiet...]")))
		self.channelMatch.append(re.compile("^\.\.\.$", re.IGNORECASE))
		
		self.reactions.append(('^puts on shades$', '', ("YEEEEEEEAAAAAAAAAAAAAAAAAAAAAAAAAAAH", "YEEEEEEEAAAAAAAAAAAAAAAAAAAAAAAAAAAH", "[crickets chirp. The odd dog barks.]")))
		self.channelMatch.append(re.compile("^puts on shades$", re.IGNORECASE))
		
	def channelAction(self, connection, user, channel, message, matchindex):
		print "[Generic Reaction] called"


		if self.overUsed(self.uses):
			if self.reactions[matchindex][1] != '':
				connection.msg(channel, self.reactions[matchindex][1])
				return True


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
			if reaction[0] == "~":
				connection.me(channel, reaction[1:])
			elif reaction[0] == "%":
				roll = random.randint(0,50)
				if roll == 45:
					connection.msg(channel, reaction[1:])
				else:
					print "Rolled %d" % roll;
			else:
				connection.msg(channel, reaction)
			return True

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
			if reaction[0] == "~":
				print "ACtion %s : %s" % (user, reaction)
				connection.me(user, reaction)
			else:
				connection.msg(user, reaction)
			return

