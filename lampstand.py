#!/usr/bin/python

#


"""
I am Lampstand. Beware.


Todo:

	* Move databases to MySQL instead of sqlite
	* Store events in database instead of hash
	* Same for admins, probably.
	* Multiple matching regexes for each module
		* So we can combine do/say into one module
	* Generic reaction module
		* Shift favourite/Cohan into same
	* King James Bible
	* Quotes Interface
	* iCal interface
	* Shift all Reactions into other files
	* Generify overuse a bit better
	* Make Overuse code tell the person who is trying to overuse it that they suck
	* Fix "Since" events.
	* NickServ support
	* Choose incoming IP
	* All the cool shit in your head
"""



# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys
import re, os
import string
import exceptions

from pysqlite2 import dbapi2 as sqlite


#from lampstand.reactions import *

import lampstand.reactions;

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
				if isinstance(channelModule.channelMatch, tuple) or isinstance(channelModule.channelMatch, list):
					indx = 0
					for channelSubMatch in channelModule.channelMatch:
						if channelSubMatch.match(message):
							channelModule.channelAction(self.connection, user, channel, message, indx)
						indx = indx+1;
				elif channelModule.channelMatch.match(message):
					#print 'Channel Matched on %s' % channelModule
					channelModule.channelAction(self.connection, user, channel, message)

			#print "< %s/%s: %s" % (user, channel, message)


	def leave(self, reason, user, parameters):

			if (user in self.connection.people):
				self.connection.people.remove(user)
				print "Removed %s from user list" % user
			else:
				print "No %s in %s" % (user, self.connection.people)

			if user == self.connection.original_nickname and self.connection.nickname != connection.original_nickname:
					self.connection.register(self.original_nickname)

			for leaveModule in self.connection.leaveModules:
				if isinstance(leaveModule.leaveMatch, tuple):
					for leaveSubMatch in leaveModule.leaveMatch:
						if leaveSubMatch.match(message):
							leaveModule.leaveAction(self.connection, user, reason, params)
				elif leaveModule.leaveMatch.match(message):
					#print 'Channel Matched on %s' % channelModule
					leaveModule.leaveAction(self.connection, user, reason, params)



	def join(self, user, parameters):

			if user not in self.connection.people:
				self.connection.people.append(user)
				print "Added %s to user list" % user
			else:
				print "%s is in %s" % (user, self.connection.people)


			for joinModule in self.connection.joinModules:
				if isinstance(joinModule.joinMatch, tuple):
					for joinSubMatch in joinModule.joinMatch:
						if joinSubMatch.match(message):
							joinModule.joinAction(self.connection, user, reason, params)
				elif joinModule.joinMatch.match(message):
					#print 'Channel Matched on %s' % channelModule
					joinModule.joinAction(self.connection, user, reason, params)

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
		print 'Scanning...'
			
		if user in self.peopleToIgnore:
			print "(Ignoring)"
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
					print "(Ignoring)"
				else:
					self.connection.msg(user, "I didn't understand that, sorry. Docs: http://www.maelfroth.org/lampstand.php")



class LampstandLoop(irc.IRCClient):
	"""An IRC Bot for #maelfroth."""

	nickname = "Lampstand"
	original_nickname = "Lampstand"
	alt_nickname = "Catbus"

	chanserv_password = False


	dbconnection = False

	def connectionMade(self):

		if os.path.exists('%s.db' % self.factory.channel):
			print "Loading database database %s " % self.factory.channel
			self.dbconnection = sqlite.connect('%s.db' % self.factory.channel)
		else:
			print "Couldn't load database %s " % self.factory.channel
			reactor.stop()


		if (self.dbconnection):
			cursor = self.dbconnection.cursor()
			cursor.execute('SELECT server, password FROM nickserv where server = ?', (self.factory.server,) )
			result = cursor.fetchone()

			if result != None:
				self.chanserv_password = result[1];
				print "Chanserv Password is "+result[1];
			else:
				print "Couldn't find a chanserv password for "+self.factory.server
		else:
				print "No database, not loading nickserv password"



		irc.IRCClient.connectionMade(self)
		self.logger = MessageLogger(open(self.factory.channel+'.log', "a"))

		self.channel    = ChannelActions(self)
		self.private    = PrivateActions(self)

		self.people = []

		self.channelModules = []
		self.privateModules = []
		self.nickChangeModules = []
		self.leaveModules = []
		self.joinModules = []

		defaultModules = ('admin', 'hug', 'eightball', 'generic')

		for thingy in defaultModules:
			self.installModule(thingy)

		self.logger.log("[connected at %s]" %
						time.asctime(time.localtime(time.time())))

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

	def addModuleActions(self, moduleName):

		module = sys.modules['lampstand.reactions.%s' % moduleName]

		reaction = module.Reaction(self)

		if hasattr(reaction, 'channelMatch'):
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


	def connectionLost(self, reason):
		irc.IRCClient.connectionLost(self, reason)
		self.logger.log("[disconnected at %s]" %
						time.asctime(time.localtime(time.time())))
		self.logger.close()


	def nickservGhost(self):
		if self.chanserv_password != False:
			print '[IDENTIFY] Recovering my nickname '
			self.msg('nickserv', "Ghost %s %s" % (self.original_nickname, self.chanserv_password.encode('utf8') ) )

	# callbacks for events

	def signedOn(self):

		if (self.nickname != self.original_nickname):
			self.nickservGhost()

		"""Called when bot has succesfully signed on to server."""
		self.join(self.factory.channel)

	def joined(self, channel):
		"""This will get called when the bot joins the channel."""
		self.logger.log("[I have joined %s]" % channel)
		#sms.send('Lampstand: I have returned to %s' % channel)

	def privmsg(self, user, channel, msg):
		"""This will get called when the bot receives a message."""
		user = user.split('!', 1)[0]
		self.logger.log("<%s> %s" % (user, msg))


		print "> %s/%s: %s" % (user, channel, msg)
		#self.logger.log("<%s> %s" % (self.nickname, msg))

		if (msg[0:3] == '***'):
			return

		# Check to see if they're sending me a private message
		if channel.lower() == self.nickname.lower():
			print 'Scanning as private message (%s == %s)' % (channel, self.nickname)
			self.private.action(user, channel, msg)
			return
		else:
			print 'Scanning as public message (%s != %s)' % (channel, self.nickname)
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


	# irc callbacks

	def irc_NICK(self, prefix, params):
		"""Called when an IRC user changes their nickname."""
		old_nick = prefix.split('!')[0]
		new_nick = params[0]
		self.logger.log("%s is now known as %s" % (old_nick, new_nick))
		self.channel.nickChange(old_nick, new_nick)

	def irc_PART(self, prefix, params):
		"""Saw someone part from the channel"""
		print "Saw a part: %s %s" % (prefix, params)
		nickname = prefix.split('!')[0]
		self.channel.leave('part', nickname, params)
		pass

	def irc_QUIT(self, prefix, params):
		"""Saw someone Quit from the channel"""
		print "Saw a quit: %s %s" % (prefix, params)
		nickname = prefix.split('!')[0]
		self.channel.leave('quit', nickname, params)
		pass

	def irc_TOPIC(self, prefix, params):
		"""Saw someone change the topic"""
		print "Saw a topic change: %s %s" % (prefix, params)
		pass

	def irc_JOIN(self, prefix, params):
		"""Saw someone Join the channel"""
		print "Saw a join: %s %s" % (prefix, params)
		nickname = prefix.split('!')[0]
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

		people = []

		for nickname in names:
			print "saw %s" % nickname
			if len(nickname) == 0:
				pass
			elif nickname[0] == '@' or nickname[0] == '+':
				people.append(nickname[1:])
			else:
				people.append(nickname)

		print 'People: %s' % people

		self.people = people


		pass

	def irc_333(self, prefix, params):
		"""??????????"""
		print "Saw a 333 (!!): %s %s" % (prefix, params)
		pass

	def userKicked(self, kickee, channel, kicker, message):
		"""Saw someone kicked from the channel"""
		print "Saw a kick: %s kicked %s saying %s" % (kickee, kicker, message)
		self.channel.leave('kick', kickee, message)
		pass



class LampstandFactory(protocol.ClientFactory):
	"""We make Lampstands

	A new protocol instance will be created each time we connect to the server.
	"""

	# the class of the protocol to build when new connection is made
	protocol = LampstandLoop

	def __init__(self, channel, server):
		self.channel = channel
		self.server = server

	def clientConnectionLost(self, connector, reason):
		"""If we get disconnected, reconnect to server."""
		#connector.connect()
		#sms.send('Lampstand: HAZ NO CONEXON')

	def clientConnectionFailed(self, connector, reason):
		print "connection failed:", reason
		reactor.stop()


if __name__ == '__main__':
	# initialize logging
	log.startLogging(sys.stdout)

	if len(sys.argv) < 2:
		print "Not enough arguments. Try %s #channel [server]" % sys.argv[0]
		sys.exit(1)

	server = "cosmos.esper.net"

	if len(sys.argv) == 3:
		server = sys.argv[2]

	# create factory protocol and application
	f = LampstandFactory(sys.argv[1], server)

	# connect factory to this host and port
	reactor.connectTCP(server, 6667, f)

	# run bot
	reactor.run()
