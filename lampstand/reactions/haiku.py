from lampstand.tools import splitAt
import re, time, random, sys, datetime
import lampstand.reactions.base
from lampstand import tools
import haikufinder

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Haiku'
	
	


	def __init__(self, connection):
		self.channelMatch = (re.compile('%s. how many syllables in (\w*)\??' % connection.nickname, re.IGNORECASE),
			re.compile('%s. (\w*) has (\d\d?) syllables?\.?' % connection.nickname, re.IGNORECASE),
			re.compile('.*')
			)
		self.dbconnection = connection.dbconnection
		
		self.channels = {}

	def channelAction(self, connection, user, channel, message, matchindex):
				
		if matchindex == 0: # How many
			return self.countSyllables(connection, user, channel, message)
			
		if matchindex == 1: # Cheat sheet
			return self.cheatSheet(connection, user, channel, message)
					
		# Fallback
		return self.findHaiku(connection, user, channel, message)
	
	def countSyllables(self, connection, user, channel, message):
		
		matches = self.channelMatch[0].findall(message)
		
		print matches
		
		syllables = haikufinder.LineSyllablizer(matches[0]).count_syllables()
		#syllables = haikufinder.HaikuFinder(matches[0]).count_syllables()
		
		if syllables == 1:
			ordinal = ""
		elif syllables == -1:
			connection.msg(channel, "%s: I don't know, so I ignore it." % user)
			return True
		else:
			ordinal = "s"
		
		connection.msg(channel, "%s: %s has %s syllable%s" % (user, matches[0], syllables, ordinal))
		return True
	
	def cheatSheet(self, connection, user, channel, message):
		print "Cheatsheet"
		
		
		matches = self.channelMatch[1].findall(message)
		
		haikufinder.HaikuFinder.add_word(matches[0][0], int(matches[0][1]));
		
		connection.msg(channel, "%s: If you say so" % user)
		
		return True
	
	def findHaiku(self, connection, user, channel, message):
		
		if not self.channels.has_key(channel):
			self.channels[channel] = []
		
		self.channels[channel].append(message)
		if len(self.channels[channel]) > 3:
			self.channels[channel] = self.channels[channel][-3:]
		
		print "Content for %s: %s " % (channel, " ".join(self.channels[channel]))
			
		haikus = haikufinder.HaikuFinder(" ".join(self.channels[channel])).find_haikus()
		
		print haikus
		
		if len(haikus):
			connection.msg("#lampstand", "Hey, cool. A haiku on %s: %s " % (channel, " // ".join(haikus[0])))
			self.channels[channel] = []
			return True
		
		return False
