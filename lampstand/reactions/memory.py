from lampstand.tools import splitAt
import re, time, random, sys, datetime
import lampstand.reactions.base
from lampstand import tools

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Memory'


	def __init__(self, connection):
		self.dbconnection = connection.dbconnection
		self.memory = {}
		self.channelMatch = ()
		
		self.memorysize = 100
	
	def everyLine(self, connection, user, channel, message):
		if not self.memory.has_key(channel):
			print "New memorybank for %s channel" % channel
			self.memory[channel] = []
		
		line = {"timestamp": time.localtime(time.time()), "user": user, "message": message}
		self.memory[channel].append(line)
		if len(self.memory[channel]) > self.memorysize:
			limit = 0 -  self.memorysize
			self.memory[channel] = self.memory[channel][limit:]

	def search(self, channel, user = False, filter = False):
		pass

	def dump(self, connection, user, reason, params):
		print self.memory
