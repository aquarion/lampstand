#!/usr/bin/python

#


"""
I am Lampstand. Beware.


Todo:

	* Database admins, probably.
	* King James Bible
	* Choose incoming IP
	* All the cool shit in your head
"""



# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, threads, defer
from twisted.python import log

from datetime import datetime
from twisted.internet.task import LoopingCall

# system imports
import time, sys
import re, os
import string
import exceptions

import random

random.seed()

import MySQLdb

import lampstand.reactions;

import ConfigParser

from lampstand import sms

class MessageLogger:
	"""
	An independent logger class (because separation of application
	and protocol logic is a good thing).
	"""
	def __init__(self, file):
		self.file = file

	def log(self, message):
		"""Write a message to the file."""
		timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
		self.file.write('%s %s\n' % (timestamp, message))
		self.file.flush()

	def close(self):
		self.file.close()

class ChannelActions:
	peopleToIgnore = ('ChanServ')

	def __init__(self, connection):
		self.connection = connection


	def action(self, user, channel, message):
			for channelModule in self.connection.channelModules:
				if hasattr(channelModule, "channelMatch"):
					if isinstance(channelModule.channelMatch, tuple) or isinstance(channelModule.channelMatch, list):
						indx = 0
						for channelSubMatch in channelModule.channelMatch:
							if channelSubMatch.match(message):
								result = channelModule.channelAction(self.connection, user, channel, message, indx)
								if result == True:
									return True
							indx = indx+1;
					elif channelModule.channelMatch.match(message):
						print 'Channel Matched on %s' % channelModule
						result = channelModule.channelAction(self.connection, user, channel, message)
						if result == True:
							print "ChannelAction successfully replied, returning to loop"
							return True;
						else:
							print "ChannelAction declined, returning to loop"
				
				if hasattr(channelModule, "everyLine"):
					result = False
					result = channelModule.everyLine(self.connection, user, channel, message)
					if result == True:
						return True
					

			#print "< %s/%s: %s" % (user, channel, message)


	def leave(self, reason, user, parameters):

			if user == self.connection.original_nickname and self.connection.nickname != self.connection.original_nickname:
					self.connection.register(self.connection.original_nickname)

			for leaveModule in self.connection.leaveModules:
				leaveModule.leaveAction(self.connection, user, reason, parameters)



	def join(self, user, parameters):

			for joinModule in self.connection.joinModules:
				joinModule.joinAction(self.connection, user, reason, parameters)

			#print "< %s/%s: %s" % (user, channel, message)



	def nickChange(self, old_nick, new_nick):

		if new_nick not in self.connection.people:
			self.connection.people.append(new_nick)
			print "Added %s to user list" % new_nick

		if (old_nick in self.connection.people):
			self.connection.people.remove(old_nick)
			print "Removed %s from user list" % old_nick

		if old_nick == self.connection.original_nickname and self.connection.nickname != self.connection.original_nickname:
				self.connection.register(self.connection.original_nickname)

		if old_nick in self.peopleToIgnore or new_nick in self.peopleToIgnore:
			print "(Ignoring)"
		else:
			matched = 0
			for nickChangeModule in self.connection.nickChangeModules:
				nickChangeModule.nickChangeAction(self.connection, old_nick, new_nick)


class PrivateActions:

	peopleToIgnore = ('ChanServ')

	def __init__(self, connection):
		self.connection = connection

	def action(self, user, channel, message):
			
		if user in self.peopleToIgnore or user == self.connection.nickname:
			print "(Ignoring %s on principle)" % user 
		else:

			matched = 0
			

			for privateModule in self.connection.privateModules:
				if isinstance(privateModule.privateMatch, tuple) or isinstance(privateModule.privateMatch, list):
					indx = 0
					for privateSubMatch in privateModule.privateMatch:
						if privateSubMatch.match(message):
							matched = matched + 1
							privateModule.privateAction(self.connection, user, channel, message, indx)
						indx = indx+1;
				elif privateModule.privateMatch.match(message):
					matched = matched + 1
					print 'private Matched on %s' % privateModule
					privateModule.privateAction(self.connection, user, channel, message)

			if matched == 0:
				peopleToIgnore = ('NickServ', 'MemoServ', 'ChanServ')
				if user in peopleToIgnore:
					print "(Ignoring %s for not matching)" % user
				else:
					self.connection.msg(user, "I didn't understand that, sorry. Docs: http://www.maelfroth.org/lampstand.php")
					print "Sending Sorry to %s" % user

	

class LampstandLoop(irc.IRCClient):
	"""An IRC Bot for #maelfroth."""

	nickname = "Lampstand"
	original_nickname = "Lampstand"
	#nickname = "Newstand"
	#original_nickname = "Newstand"
	alt_nickname = "Catbus"
	password = False

	dbconnection = False
	config = False

	date_started = False

	def scheduledTasks(self):
		for scheduledTaskModule in self.scheduledTaskModules:
			try:
				scheduledTaskModule.scheduleAction(self)
			except:
				pass

	def connectionMade(self):

		self.date_started = datetime.now()

		self.config = self.factory.config
		
		
		self.dbconnection = MySQLdb.connect(user = self.config.get("database","user"), passwd = self.config.get("database","password"), db = self.config.get("database","database"))
			
		#threads.deferToThread(self.scheduledTasks)
		#reactor.callInThread(self.scheduledTask);
		
		
		self.nickname = self.config.get("irc","nickname")
		self.password = self.config.get("irc","password")
		self.original_nickname = self.nickname
		self.alt_nickname = self.config.get("irc","altnickname")

		self.realname = "Lampstand L. Lampstand."
		self.userinfo = "I'm a bot! http://wiki.maelfroth.org/lampstandDocs"
		
		logfile = self.config.get("logging", "logfile");

		irc.IRCClient.connectionMade(self)
		self.logger = MessageLogger(open(logfile, "a"))

		self.channel    = ChannelActions(self)
		self.private    = PrivateActions(self)

		self.people = []
		self.population = {}

		self.channelModules = []
		self.privateModules = []
		self.nickChangeModules = []
		self.leaveModules = []
		self.joinModules = []
		self.scheduledTaskModules = []


		for thingy in config.items("modules"):
			self.installModule(thingy[0])

		self.logger.log("[connected at %s]" %
						time.asctime(time.localtime(time.time())))
		
		self.loopy = LoopingCall(self.scheduledTasks)
		self.loopy.start(5)

	def installModule(self, moduleName):

		self.removeModuleActions(moduleName);

		module = 'lampstand.reactions.%s' % moduleName

		rtn = '';
		
		print "Installing %s" % moduleName

		if (sys.modules.has_key(module)):
			self.removeModuleActions(moduleName)
			print 'Reloading %s' % module
			reload(sys.modules[module]);
			rtn = 'Reloaded %s' % module
			print rtn
		else:
			try:
				rtn = 'Loaded %s' % module
				__import__(module)
			except exceptions.ImportError:
				rtn = 'Epic Fail loading %s, Not found' % module
			except:
				rtn = 'Epic Fail loading %s, Threw an exception' % module


		self.addModuleActions(moduleName)
		return rtn


	def removeModuleActions(self, module):

		module = 'lampstand.reactions.%s' % module
		
		for reaction in self.channelModules:
			if reaction.__module__ == module:
				self.channelModules.remove(reaction)

		for reaction in self.privateModules:
			if reaction.__module__ == module:
				self.privateModules.remove(reaction)

		for reaction in self.nickChangeModules:
			if reaction.__module__ == module:
				self.nickChangeModules.remove(reaction)

		for reaction in self.leaveModules:
			if reaction.__module__ == module:
				self.leaveModules.remove(reaction)

		for reaction in self.joinModules:
			if reaction.__module__ == module:
				self.joinModules.remove(reaction)

		for reaction in self.scheduledTaskModules:
			if reaction.__module__ == module:
				self.scheduledTaskModules.remove(reaction)

	def addModuleActions(self, moduleName):

		module = sys.modules['lampstand.reactions.%s' % moduleName]

		reaction = module.Reaction(self)

		if hasattr(reaction, 'channelMatch') or hasattr(reaction, 'everyLine'):
			print '[%s] Installing channel text reaction' % (moduleName)
			self.channelModules.append(reaction)

		if hasattr(reaction, 'privateMatch'):
			print '[%s] Installing private text reaction' % moduleName
			self.privateModules.append(reaction)

		if hasattr(reaction, 'nickChangeAction'):
			print '[%s] Installing nick change reaction' % moduleName
			self.nickChangeModules.append(reaction)

		if hasattr(reaction, 'leaveAction'):
			print '[%s] Installing channel leave reaction' % moduleName
			self.leaveModules.append(reaction)

		if hasattr(reaction, 'joinAction'):
			print '[%s] Installing channel join reaction' % moduleName
			self.joinModules.append(reaction)
		
		if hasattr(reaction, 'scheduleAction'):
			print '[%s] Installing schedule reaction' % moduleName
			self.scheduledTaskModules.append(reaction)


	def connectionLost(self, reason):
		print "Connection lost for reason %s" % reason
		irc.IRCClient.connectionLost(self, reason)
		self.logger.log("[disconnected at %s]" %
						time.asctime(time.localtime(time.time())))
		self.logger.close()


	def nickservGhost(self):
		if self.password != False:
			print '[IDENTIFY] Recovering my nickname '
			self.msg('nickserv', "Ghost %s %s" % (self.original_nickname, self.password.encode('utf8') ) )

	# callbacks for events

	def signedOn(self):

		if (self.nickname != self.original_nickname):
			self.nickservGhost()

		"""Called when bot has succesfully signed on to server."""
				
		for item in config.items("channels"):
			self.join("#%s" % item[0])
		
	def joined(self, channel):
		"""This will get called when the bot joins the channel."""
		self.logger.log("[I have joined %s]" % channel)

	def privmsg(self, user, channel, msg):
		"""This will get called when the bot receives a message."""
		user = user.split('!', 1)[0]
		self.logger.log("<%s> %s" % (user, msg))


		print "%s/%s: %s" % (channel, user, msg)
		#self.logger.log("<%s> %s" % (self.nickname, msg))

		if (msg[0:3] == '***'):
			return

		# Check to see if they're sending me a private message
		if channel.lower() == self.nickname.lower():
			self.private.action(user, channel, msg)
			return
		else:
			self.channel.action(user, channel, msg)

		# Otherwise check to see if it is a message directed at me
		#if msg.startswith(self.nickname + ":"):
		#    msg = self.channel.action(user, channel, msg)



	def action(self, user, channel, msg):
		print "* %s/%s: %s" % (user, channel, msg)
		"""This will get called when the bot sees someone do an action."""
		user = user.split('!', 1)[0]
		self.channel.action(user, channel, msg)
		self.logger.log("* %s %s" % (user, msg))

	def message(self, user, message, length=200):
		return self.msg(user,message.encode("utf-8"),length)

	# irc callbacks


	def irc_NICK(self, prefix, params):
		"""Called when an IRC user changes their nickname."""
		old_nick = prefix.split('!')[0]
		new_nick = params[0]
		self.logger.log("%s is now known as %s" % (old_nick, new_nick))
		self.channel.nickChange(old_nick, new_nick)
		for channel, people in self.population.items():
			if old_nick in people:
				self.population[channel].remove(old_nick)
			
			if not new_nick in people:
				self.population[channel].append(new_nick)
		
		if not new_nick in self.people:
			self.people.append(new_nick)
		
		if old_nick in self.people:
			self.people.remove(old_nick)

		print self.people
		print self.population


	def irc_PART(self, prefix, params):
		"""Saw someone part from the channel"""
		print "Saw a part: %s %s" % (prefix, params)
		nickname = prefix.split('!')[0]
		self.channel.leave('part', nickname, params)

		print params

		self.leave(nickname, params[0])
		pass

	def irc_QUIT(self, prefix, params):
		"""Saw someone Quit from the channel"""
		print "Saw a quit: %s %s" % (prefix, params)
		nickname = prefix.split('!')[0]
		self.channel.leave('quit', nickname, params)

		for channel, people in self.population.items():
			self.leave(nickname, channel)
			
		pass

	def irc_TOPIC(self, prefix, params):
		"""Saw someone change the topic"""
		print "Saw a topic change: %s %s" % (prefix, params)
		pass

	def irc_JOIN(self, prefix, params):
		"""Saw someone Join the channel"""
		print "Saw a join: %s %s" % (prefix, params)
		nickname = prefix.split('!')[0]
		channel = params[0]


		if nickname not in self.people:
			self.people.append(nickname)
			print "Added %s to user list" % nickname
		else:
			print "%s is in %s" % (nickname, self.people)
		
		if not self.population.has_key(channel):
			self.population[channel] = []
			
		if nickname not in self.population[channel]:
			self.population[channel].append(nickname)
			print "Added %s to %s user list" % (nickname, channel)
		else:
			print "%s is in %s already" % (nickname, channel)

		print self.population

		self.channel.join(nickname, params)
		pass

	def irc_RPL_TOPIC(self, prefix, params):
		"""??????????"""
		print "Saw a RPL_TOPIC (!!): %s %s" % (prefix, params)
		pass

	def irc_ERR_NICKNAMEINUSE(self, prefix, params):
		"""??????????"""
		print "Saw a irc_ERR_NICKNAMEINUSE (!!): %s %s" % (prefix, params)
		if (self.nickname == self.original_nickname):
			print '[IDENTIFY] Downgrading to  '	+self.alt_nickname
			self.register(self.alt_nickname)
			self.nickname = self.alt_nickname
		elif (self.nickname == self.alt_nickname):
			print '[IDENTIFY] Downgrading to  '	+self.original_nickname+'_'
			self.register(self.original_nickname+'_')
			self.nickname = self.original_nickname+'_'

		pass


	def irc_RPL_NAMREPLY(self, prefix, params):
		"""??????????"""
		print "Saw a irc_RPL_NAMREPLY (!!): %s %s" % (prefix, params)

		server = prefix
		myname = params[0]
		atsign = params[1]
		channel = params[2]
		names = params[3].split(' ');

		#people = []

		self.population[channel] = []

		for nickname in names:
			print "saw %s" % nickname
			if len(nickname) == 0:
				pass
			elif nickname[0] == '@' or nickname[0] == '+':
				if not nickname[1:] in self.people:
					self.people.append(nickname[1:])
				self.population[channel].append(nickname[1:])
			else:
				if not nickname in self.people:
					self.people.append(nickname)
				self.population[channel].append(nickname)

		print 'People: %s' % self.people
		print 'Population: %s' % self.population

		#self.people = people


		pass

	def irc_333(self, prefix, params):
		"""??????????"""
		print "Saw a 333 (!!): %s %s" % (prefix, params)
		pass

	def userKicked(self, kickee, channel, kicker, message):
		"""Saw someone kicked from the channel"""
		print "Saw a kick: %s kicked %s saying %s" % (kickee, kicker, message)
		self.channel.leave('kick', kickee, message)
		self.leave(kickee, channel)

		pass

	def leave(self, nickname, channel):
		
		if nickname[1:] in self.population[channel]:
			self.population[channel].remove(nickname[1:])
			print "[LEAVE] Removed %s from %s user list" % (nickname, channel)
		
		if nickname in self.population[channel]:
			self.population[channel].remove(nickname)
			print "[LEAVE] Removed %s from %s user list" % (nickname, channel)

		found = False
		for channel, people in self.population.items():
			if nickname in people:
				found = True
				print "[LEAVE] Found %s in %s user list, keeping in dictionary" % (nickname, channel)
				return
		if not found:
			print "[LEAVE] Lost %s entirely" % nickname
			self.people.remove(nickname)

	def loadConfig(self):
		basedir = os.path.dirname(os.path.abspath(sys.argv[0]))
		config = ConfigParser.ConfigParser()
		config.read(["defaults.ini", basedir+'/config.ini'] )
		self.config = config		
			


class LampstandFactory(protocol.ClientFactory):
	"""We make Lampstands

	A new protocol instance will be created each time we connect to the server.
	"""

	# the class of the protocol to build when new connection is made
	protocol = LampstandLoop

	def __init__(self, config):
		self.config = config

	def clientConnectionLost(self, connector, reason):
		"""If we get disconnected, reconnect to server."""
		sms.send('Lampstand: HAZ NO CONEXON')
		#Todo: Implement backoff
		time.sleep(45) # Our very own fourty five second claim.
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		print "connection failed:", reason
		reactor.stop()


if __name__ == '__main__':
	cwd = os.getcwd() 
	print "Error log is %s/stderr.log" % cwd
	
	basedir = os.path.dirname(os.path.abspath(sys.argv[0]))
	config = ConfigParser.ConfigParser()
	config.read(["defaults.ini", basedir+'/config.ini'] )

	# create factory protocol and application
	f = LampstandFactory(config)

	# connect factory to this host and port
	server = config.get("connection", "server");
	port = config.getint("connection", "port");
	reactor.connectTCP(server, port, f)


	# run bot

	reactor.run()
