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
import re
import string


from lampstand.reactions import *

import dictclient

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

	def __init__(self, connection):
		self.connection = connection


	def action(self, user, channel, message):
			for channelModule in self.connection.channelModules:
				if isinstance(channelModule.channelMatch, tuple):
					for channelSubMatch in channelModule.channelMatch:
						if channelSubMatch.match(message):
							channelModule.channelAction(self.connection, user, channel, message)
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
		if user in self.peopleToIgnore:
			print "(Ignoring)"
		else:
			matched = 0
			for privateModule in self.connection.privateModules:
				if privateModule.privateMatch.match(message):
					matched = matched + 1
					print 'Private Matched on %s' % privateModule
					privateModule.privateAction(self.connection, user, channel, message)
			if matched == 0:
				self.connection.msg(user, "I didn't understand that, sorry. Hi, I'm Lampstand. I'm a bot built for #maelfroth by Aquarion <nicholas@aquarionics.com>. Please talk to him if you have a problem with me. Some documentation about me is at http://hol.istic.net/lampstand")



class LampstandLoop(irc.IRCClient):
	"""An IRC Bot for #maelfroth."""

	nickname = "Lampstand"



	def connectionMade(self):
		irc.IRCClient.connectionMade(self)
		self.logger = MessageLogger(open(self.factory.filename, "a"))

		self.channel    = ChannelActions(self)
		self.private    = PrivateActions(self)
		
		self.people = []
		

		self.dbconnection = sqlite.connect('lampstand.db')


		self.channelModules = []
		self.channelModules.append(HugReaction(self))
		self.channelModules.append(PodBayReaction(self))
		self.channelModules.append(InsultReaction(self))
		self.channelModules.append(WhowasReaction(self))
		#self.channelModules.append(RevelationReaction(self))
		self.channelModules.append(BibleReaction(self))
		self.channelModules.append(DiceReaction(self))
		self.channelModules.append(WeblinkReaction(self))
		self.channelModules.append(PokeReaction(self))
		self.channelModules.append(DictionaryReaction(self))
		self.channelModules.append(OpinionReaction(self))
		self.channelModules.append(HowLongReaction(self))
		self.channelModules.append(FavouriteReaction(self))
		self.channelModules.append(CohanReaction(self))
		self.channelModules.append(EightballReaction(self))

		self.privateModules = []
		self.privateModules.append(TellAqReaction(self))
		self.privateModules.append(WhowasReaction(self))
		self.privateModules.append(HugReaction(self))
		self.privateModules.append(SayReaction(self))
		self.privateModules.append(DoReaction(self))
		self.privateModules.append(QuitReaction(self))
		self.privateModules.append(HowLongReaction(self))

		self.nickChangeModules = []
		self.nickChangeModules.append(WhowasReaction(self))

		self.leaveModules = []
		
		self.joinModules = []

		self.logger.log("[connected at %s]" %
						time.asctime(time.localtime(time.time())))

	def connectionLost(self, reason):
		irc.IRCClient.connectionLost(self, reason)
		self.logger.log("[disconnected at %s]" %
						time.asctime(time.localtime(time.time())))
		self.logger.close()


	# callbacks for events

	def signedOn(self):
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
		self.logger.log("<%s> %s" % (self.nickname, msg))

		if (msg[0:3] == '***'):
			return

		# Check to see if they're sending me a private message
		if channel == self.nickname:
			self.private.action(user, channel, msg)
			return
		else:
			self.channel.action(user, channel, msg)

		# Otherwise check to see if it is a message directed at me
		#if msg.startswith(self.nickname + ":"):
		#    msg = self.channel.action(user, channel, msg)



	def action(self, user, channel, msg):
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
		self.channel.nickchange(old_nick, new_nick)

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
		
	def userKicked(self, prefix, params):
		"""Saw someone kicked from the channel"""
		print "Saw a kick: %s %s" % (prefix, params)
		nickname = prefix.split('!')[0]
		self.channel.leave('kick', nickname, params)
		pass
		


class LampstandFactory(protocol.ClientFactory):
	"""We make Lampstands

	A new protocol instance will be created each time we connect to the server.
	"""

	# the class of the protocol to build when new connection is made
	protocol = LampstandLoop

	def __init__(self, channel, filename):
		self.channel = channel
		self.filename = filename

	def clientConnectionLost(self, connector, reason):
		"""If we get disconnected, reconnect to server."""
		#connector.connect()
		sms.send('Lampstand: HAZ NO CONEXON')

	def clientConnectionFailed(self, connector, reason):
		print "connection failed:", reason
		reactor.stop()


if __name__ == '__main__':
	# initialize logging
	log.startLogging(sys.stdout)

	if len(sys.argv) < 3:
		print "Not enough arguments. Try %s #channel logfile [server]" % sys.argv[0]
		sys.exit(1)

	server = "cosmos.esper.net"

	if len(sys.argv) == 4:
		server = sys.argv[3]

	# create factory protocol and application
	f = LampstandFactory(sys.argv[1], sys.argv[2])

	# connect factory to this host and port
	reactor.connectTCP(server, 6667, f)

	# run bot
	reactor.run()
