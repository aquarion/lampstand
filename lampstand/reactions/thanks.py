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

		self.channelMatch = re.compile(".*Thanks,? (\S+)\s*\.?$", re.IGNORECASE)
		self.privateMatch = []

	def channelAction(self, connection, user, channel, message):
		print "[Generic Reaction] called"

		word = self.channelMatch.findall(message)[0];

		if not word:
			return False;

		number = random.randint(0,10)

		if word in connection.people and number == 7:
			thanks = self.thanks(word);
			print "[THANKS] Thanks, %s: %s" % (word, thanks)
			connection.message(channel, thanks)
			return True
		elif word in connection.people:
			print "Found, but not random"
		else:
			print "Random was %d" % number

		return False


	def thanks(self, word):
			
		word = word.lower().strip()
		if not word:
			return false	


		print "Thanks, %s" % word

		if word[0] in ("a","e","i","o","u"):

			print "That starts with a vowel, using the whole word"

			thanks = word

		else:	

			scrugg = re.split(r'[aeiouy]', word, 1);
	
			#scrugg = re.split(r'[^aeiouy]+', word)
	
			print scrugg

			if len(scrugg) < 2:
				print "Failed to split on vowels"
				return false
	
	
			if(len(scrugg) > 1):
				print "Using second element"
				thanks = scrugg[1]
			else:
				print "Using whole word"
				thanks = word
	
		if not thanks or len(thanks) < 1:
			print "Thanks isn't good enough: %s" % thanks
			return false

		print thanks	

		if(thanks[0] == "a"):
			thanks = "Th%s" % thanks 
		elif(thanks[0] == "o"):
			thanks = "Th%s" % thanks 
		else:
			thanks = "Tha%s" % thanks
	
		return thanks
