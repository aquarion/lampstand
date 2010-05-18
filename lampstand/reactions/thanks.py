import re, time, random, sys
import lampstand.reactions.base

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	
	__name = 'Thanks'
	
	cooldown_number = 2
	cooldown_time   = 360
	uses = []

	def __init__(self, connection):

		self.channelMatch = re.compile(".*Thanks,? (\w+)\.?$", re.IGNORECASE)
		self.privateMatch = []

	def channelAction(self, connection, user, channel, message):
		print "[Generic Reaction] called"

		word = self.channelMatch.findall(message)[0];

		if not word:
			return false;

		thanks = self.thanks(word);

		print "[THANKS] Thanks, %s: %s" % (word, thanks)

		connection.msg(channel, thanks)
		return true



	def thanks(self, word):
			
		word = word.lower().strip()
		if not word:
			return false	
	
		scrugg = re.split(r'[aeiouy]', word, 1);
	
		#scrugg = re.split(r'[^aeiouy]+', word)
	
		if len(scrugg) < 2:
			return false
	
	
		if(len(scrugg) > 1):
			thanks = scrugg[1]
		else:
			thanks = word
	
		if not thanks or len(thanks) < 1:
			return false

		print thanks	

		if(thanks[0] == "a"):
			thanks = "Th%s" % thanks 
		elif(thanks[0] == "o"):
			thanks = "Tho%s" % thanks 
		else:
			thanks = "Tha%s" % thanks
	
		return thanks
