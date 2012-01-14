import time, ConfigParser
def __init__ ():
	pass

class Reaction:

	#canSay = ("Aquarion")
	
	__name = 'Base'
	
	cooldown_number = 6
	cooldown_time   = 360
	uses = []
	
	def __str__(self):
		return self.__name
		
	def __repr__(self):
		return '<%s Reaction>' % self


	def __init__(self, connection):
		pass
		

	def getconfig(self, connection):
		try:
			config = connection.config.items(self.__name)
			print "Haiku Config!"
			self.config = {}
			for item in config:
				self.config[item[0]] = item[1]
		except ConfigParser.NoSectionError:
			print "no config for %s" % self.__name
			pass
		
		
	#def privateAction(self, connection, user, channel, message, matchindex = 0):


	def overUsed(self, uses = False, number = False, cooldown = False):

		if (uses != False):
			print "Note: %s is still using the old overused syntax" % self.__name;
		

		if len(self.uses) >= self.cooldown_number:
			first_use = int(self.uses[0])
			use_allowed_again = first_use + self.cooldown_time
			if time.time() < use_allowed_again:
				print "Use Blocked. Try again in %s" % (int(use_allowed_again) - time.time());
				return True
			else:
				print "Now %s, Limit at %s (%d)" % (time.time(), use_allowed_again, time.time() - int(use_allowed_again) )
	
		return False
		
	def updateOveruse(self):
		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[1:self.cooldown_number]
		## Overuse Detectection ##

