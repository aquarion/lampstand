import re, time, random, sys, datetime
import haikufinder
import cPickle  as pickle

from lampstand import tools
from lampstand.tools import splitAt
import lampstand.reactions.base

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Haiku'
	
	


	def __init__(self, connection):
		self.config = {}
		
		self.getconfig(connection)
		
		print "Haiku Init!"
		self.channelMatch = (re.compile('%s. how many syllables in ([\w ]*)\??' % connection.nickname, re.IGNORECASE),
			re.compile('%s. (\w*) has (\d\d?) syllables?\.?' % connection.nickname, re.IGNORECASE)
			)
		self.dbconnection = connection.dbconnection
		
		self.channels = {}
		self.haikus   = {}
		self.load()

	def channelAction(self, connection, user, channel, message, matchindex):
				
		if matchindex == 0: # How many
			return self.countSyllables(connection, user, channel, message)
			
		if matchindex == 1: # Cheat sheet
			return self.cheatSheet(connection, user, channel, message)
	
	def everyLine(self, connection, user, channel, message):
		channelname = channel[1:]
		if self.config.has_key(channelname) and self.config[channelname] == "ignore":
			print "[HAIKU] Ignoring channel %s " % channelname
			return False
			
		# Fallback
		return self.findHaiku(connection, user, channel, message)
	
	def countSyllables(self, connection, user, channel, message):
		
		matches = self.channelMatch[0].findall(message)
		
		#print matches
		
		syllables = haikufinder.LineSyllablizer(matches[0]).count_syllables()
		#syllables = haikufinder.HaikuFinder(matches[0]).count_syllables()
		
		if syllables == 1:
			ordinal = ""
		elif syllables == -1:
			connection.message(channel, "%s: I don't know, so I ignore it." % user)
			return True
		else:
			ordinal = "s"
		
		connection.message(channel, "%s: \"%s\" has %s syllable%s" % (user, matches[0], syllables, ordinal))
		return True

	def save(self):
		print "[Haiku] Saving database..."
		output = open("haiku_cheatsheet.pkl.db", 'wb')
		pickle.dump(self.cheatsheet, output)
		output.close()

	def load(self):
		print "[Haiku] Loading database..."
		try:
			input = open("haiku_cheatsheet.pkl.db", 'rb')
			self.cheatsheet = pickle.load(input)
			input.close()
			for word, count in self.cheatsheet:
				print "[Haiku] %s has %d syllables" % (word, int(count))
				haikufinder.HaikuFinder.add_word(word, int(count));
		except:
			self.cheatsheet = {}


	def cheatSheet(self, connection, user, channel, message):
		print "Cheatsheet"
		
		
		matches = self.channelMatch[1].findall(message)
		
		haikufinder.HaikuFinder.add_word(matches[0][0], int(matches[0][1]));

		self.cheatsheet[matches[0][0]] = int(matches[0][1]);

		self.save()
				

		connection.message(channel, "%s: If you say so" % user)
		
		return True
	
	def findHaiku(self, connection, user, channel, message):
		
		if not self.channels.has_key(channel):
			self.channels[channel] = []
		
		self.channels[channel].append(message)
		if len(self.channels[channel]) > 3:
			self.channels[channel] = self.channels[channel][-3:]
		
		#print "Content for %s: %s " % (channel, " ".join(self.channels[channel]))
			
		haikus = haikufinder.HaikuFinder(" ".join(self.channels[channel])).find_haikus()
		
		#print haikus
		
		if len(haikus):
			
			channelname = channel[1:]
			if self.config.has_key(channelname) and not self.config[channelname] == "ignore":
				channelout = "#%s" % self.config[channelname]
			else:
				channelout = channel;
				
			connection.message(channelout, "That looked like a haiku on %s: %s " % (channel, " // ".join(haikus[0])))
			self.channels[channel] = []
			self.lasthaiku[channel] = " // ".join(haikus[0])
			return True
		
		return False
