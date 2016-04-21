#!/usr/bin/python

#


"""
I am Lampstand. Beware.

"""

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, threads, defer
from twisted.python import log

from datetime import datetime
from twisted.internet.task import LoopingCall

# system imports
import time
import sys
import re
import os
import string
import exceptions
import os.path

import random

random.seed()

# Other Imports:

import cymysql

import lampstand.reactions

import ConfigParser

from BeautifulSoup import UnicodeDammit

from lampstand import sms
import logging
from logging.handlers import TimedRotatingFileHandler


class ChannelActions:
    peopleToIgnore = ('ChanServ')

    def __init__(self, connection):
        self.connection = connection
        self.logger = connection.logger

    def action(self, user, channel, message):
        for channelModule in self.connection.channelModules:
            if hasattr(channelModule, "channelMatch"):
                if isinstance(
                        channelModule.channelMatch,
                        tuple) or isinstance(
                        channelModule.channelMatch,
                        list):
                    indx = 0
                    for channelSubMatch in channelModule.channelMatch:
                        if channelSubMatch.match(message):
                            result = channelModule.channelAction(
                                self.connection,
                                user,
                                channel,
                                message,
                                indx)
                            if result:
                                return True
                        indx = indx + 1
                elif channelModule.channelMatch.match(message):
                    self.logger.info('Channel Matched on %s' % channelModule)
                    result = channelModule.channelAction(
                        self.connection,
                        user,
                        channel,
                        message)
                    if result:
                        self.logger.info(
                            "ChannelAction successfully replied, returning to loop")
                        return True
                    else:
                        self.logger.info(
                            "ChannelAction declined, returning to loop")

            if hasattr(channelModule, "everyLine"):
                result = False
                result = channelModule.everyLine(
                    self.connection,
                    user,
                    channel,
                    message)
                if result:
                    return True

        # self.logger.info("< %s/%s: %s" % (user, channel, message))

    def leave(self, reason, user, parameters):

        if user == self.connection.original_nickname and self.connection.nickname != self.connection.original_nickname:
            self.connection.register(self.connection.original_nickname)

        for leaveModule in self.connection.leaveModules:
            leaveModule.leaveAction(self.connection, user, reason, parameters)

    def join(self, user, parameters):

        for joinModule in self.connection.joinModules:
            joinModule.joinAction(self.connection, user, reason, parameters)

        # self.logger.info("< %s/%s: %s" % (user, channel, message))

    def nickChange(self, old_nick, new_nick):

        if new_nick not in self.connection.people:
            self.connection.people.append(new_nick)
            self.logger.info("Added %s to user list" % new_nick)

        if (old_nick in self.connection.people):
            self.connection.people.remove(old_nick)
            self.logger.info("Removed %s from user list" % old_nick)

        if old_nick == self.connection.original_nickname and self.connection.nickname != self.connection.original_nickname:
            self.connection.register(self.connection.original_nickname)

        if old_nick in self.peopleToIgnore or new_nick in self.peopleToIgnore:
            self.logger.info("(Ignoring)")
        else:
            matched = 0
            for nickChangeModule in self.connection.nickChangeModules:
                nickChangeModule.nickChangeAction(
                    self.connection,
                    old_nick,
                    new_nick)


class PrivateActions:

    peopleToIgnore = ('ChanServ')

    def __init__(self, connection):
        self.connection = connection
        self.logger = connection.logger

    def action(self, user, channel, message):

        if user in self.peopleToIgnore or user == self.connection.nickname:
            self.logger.info("(Ignoring %s on principle)" % user)
        else:

            matched = 0

            for privateModule in self.connection.privateModules:
                if isinstance(
                        privateModule.privateMatch,
                        tuple) or isinstance(
                        privateModule.privateMatch,
                        list):
                    indx = 0
                    for privateSubMatch in privateModule.privateMatch:
                        if privateSubMatch.match(message):
                            matched = matched + 1
                            privateModule.privateAction(
                                self.connection,
                                user,
                                channel,
                                message,
                                indx)
                        indx = indx + 1
                elif privateModule.privateMatch.match(message):
                    matched = matched + 1
                    self.logger.info('private Matched on %s' % privateModule)
                    privateModule.privateAction(
                        self.connection,
                        user,
                        channel,
                        message)

            if matched == 0:
                peopleToIgnore = ('NickServ', 'MemoServ', 'ChanServ')
                if user in peopleToIgnore:
                    self.logger.info("(Ignoring %s for not matching)" % user)
                else:
                    self.connection.msg(
                        user,
                        "I didn't understand that, sorry. Docs: http://www.maelfroth.org/lampstand.php")
                    self.logger.info("Sending Sorry to %s" % user)


class LampstandLoop(irc.IRCClient):

    """An IRC Bot for #maelfroth."""

    nickname = "Lampstand"
    original_nickname = "Lampstand"
    #nickname = "Newstand"
    #original_nickname = "Newstand"
    alt_nickname = "Catbus"
    password = False
    log = False

    dbconnection = False
    config = False

    date_started = False

    def scheduledTasks(self):
        for scheduledTaskModule in self.scheduledTaskModules:
            try:
                scheduledTaskModule.scheduleAction(self)
            except:
                pass

    def setupMysql(self):
        user = self.config.get("database", "user")
        passwd = self.config.get("database", "password")
        db = self.config.get("database", "database")

        self.dbconnection = cymysql.connect(
            user=user,
            passwd=passwd,
            db=db,
            charset='utf8')

    def setupLogging(self):
        LOG_DIR = os.path.dirname(os.path.abspath(sys.argv[0]."/log"))
        logfile = self.config.get("logging", "logfile")
        print "logging to %s/lampstand.log" % LOG_DIR

        self.logger = logging.getLogger('lampstand')
        logging.getLogger('').setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s [%(name)s] %(message)s')

        #console = logging.StreamHandler()
        console = logging.getLogger('').handlers[0]
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        filename = "%s/lampstand.log" % LOG_DIR
        logfile = TimedRotatingFileHandler(
            filename, when='W0', interval=1, utc=True)
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)
        logging.getLogger('').addHandler(logfile)

        self.logger.debug("Hello Debug")
        self.logger.info("Hello Info")
        self.logger.warn("Hello Warn")
        self.logger.error("Hello Error")

    def connectionMade(self):

        self.date_started = datetime.now()

        self.config = self.factory.config

        self.setupMysql()
        self.setupLogging()

        # threads.deferToThread(self.scheduledTasks)
        # reactor.callInThread(self.scheduledTask);

        self.nickname = self.config.get("irc", "nickname")
        self.password = self.config.get("irc", "password")
        self.original_nickname = self.nickname
        self.alt_nickname = self.config.get("irc", "altnickname")

        self.realname = "Lampstand L. Lampstand."
        self.userinfo = "I'm a bot! http://wiki.maelfroth.org/lampstandDocs"

        irc.IRCClient.connectionMade(self)

        self.channel = ChannelActions(self)
        self.private = PrivateActions(self)

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

        self.logger.info("[connected at %s]" %
                         time.asctime(time.localtime(time.time())))

        self.loopy = LoopingCall(self.scheduledTasks)
        self.loopy.start(5)

    def installModule(self, moduleName):

        self.removeModuleActions(moduleName)

        module = 'lampstand.reactions.%s' % moduleName

        rtn = ''

        self.logger.info("Installing %s" % moduleName)

        if (module in sys.modules):
            self.removeModuleActions(moduleName)
            self.logger.info('Reloading %s' % module)
            reload(sys.modules[module])
            rtn = 'Reloaded %s' % module
            self.logger.info(rtn)
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

        # self.logger.info(sys.modules;)

        module = sys.modules['lampstand.reactions.%s' % moduleName]

        reaction = module.Reaction(self)

        if hasattr(reaction, 'channelMatch') or hasattr(reaction, 'everyLine'):
            self.logger.info(
                '[%s] Installing channel text reaction' % (moduleName))
            self.channelModules.append(reaction)

        if hasattr(reaction, 'privateMatch'):
            self.logger.info(
                '[%s] Installing private text reaction' % moduleName)
            self.privateModules.append(reaction)

        if hasattr(reaction, 'nickChangeAction'):
            self.logger.info(
                '[%s] Installing nick change reaction' % moduleName)
            self.nickChangeModules.append(reaction)

        if hasattr(reaction, 'leaveAction'):
            self.logger.info(
                '[%s] Installing channel leave reaction' % moduleName)
            self.leaveModules.append(reaction)

        if hasattr(reaction, 'joinAction'):
            self.logger.info(
                '[%s] Installing channel join reaction' % moduleName)
            self.joinModules.append(reaction)

        if hasattr(reaction, 'scheduleAction'):
            self.logger.info('[%s] Installing schedule reaction' % moduleName)
            self.scheduledTaskModules.append(reaction)

    def connectionLost(self, reason):
        if self.logger:
            self.logger.info("Connection lost for reason %s" % reason)
        irc.IRCClient.connectionLost(self, reason)

    def nickservGhost(self):
        if self.password:
            self.logger.info('[IDENTIFY] Recovering my nickname ')
            self.msg(
                'nickserv', "Ghost %s %s" %
                (self.original_nickname, self.password.encode('utf8')))

    # callbacks for events

    def signedOn(self):

        if (self.nickname != self.original_nickname):
            self.nickservGhost()

        """Called when bot has succesfully signed on to server."""

        for item in config.items("channels"):
            self.join("#%s" % item[0])

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.logger.info("[I have joined %s]" % channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.logger.info("<%s> %s" % (user, msg))

        self.logger.info("%s/%s: %s" % (channel, user, msg))
        #self.logger.info("<%s> %s" % (self.nickname, msg))

        if (msg[0:3] == '***'):
            return

        # Check to see if they're sending me a private message
        if channel.lower() == self.nickname.lower():
            self.private.action(user, channel, msg)
            return
        else:
            self.channel.action(user, channel, msg)

        # Otherwise check to see if it is a message directed at me
        # if msg.startswith(self.nickname + ":"):
        #    msg = self.channel.action(user, channel, msg)

    def action(self, user, channel, msg):
        self.logger.info("* %s/%s: %s" % (user, channel, msg))
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.channel.action(user, channel, msg)
        self.logger.info("* %s %s" % (user, msg))

    def message(self, user, message, length=380):
        message = message.replace('\n', '').replace('\r', '')
        message = UnicodeDammit(message)
        return self.msg(user, message.unicode.encode("utf-8"), length)

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.info("%s is now known as %s" % (old_nick, new_nick))
        self.channel.nickChange(old_nick, new_nick)
        for channel, people in self.population.items():
            if old_nick in people:
                self.population[channel].remove(old_nick)

            if new_nick not in people:
                self.population[channel].append(new_nick)

        if not new_nick in self.people:
            self.people.append(new_nick)

        if old_nick in self.people:
            self.people.remove(old_nick)

        self.logger.info(self.people)
        self.logger.info(self.population)

    def irc_PART(self, prefix, params):
        """Saw someone part from the channel"""
        self.logger.info("Saw a part: %s %s" % (prefix, params))
        nickname = prefix.split('!')[0]
        self.channel.leave('part', nickname, params)

        self.logger.info(params)

        self.leave(nickname, params[0])
        pass

    def irc_QUIT(self, prefix, params):
        """Saw someone Quit from the channel"""
        self.logger.info("Saw a quit: %s %s" % (prefix, params))
        nickname = prefix.split('!')[0]
        self.channel.leave('quit', nickname, params)

        for channel, people in self.population.items():
            self.leave(nickname, channel)

        pass

    def irc_TOPIC(self, prefix, params):
        """Saw someone change the topic"""
        self.logger.info("Saw a topic change: %s %s" % (prefix, params))
        pass

    def irc_JOIN(self, prefix, params):
        """Saw someone Join the channel"""
        self.logger.info("Saw a join: %s %s" % (prefix, params))
        nickname = prefix.split('!')[0]
        channel = params[0]

        if nickname not in self.people:
            self.people.append(nickname)
            self.logger.info("Added %s to user list" % nickname)
        else:
            self.logger.info("%s is in %s" % (nickname, self.people))

        if channel not in self.population:
            self.population[channel] = []

        if nickname not in self.population[channel]:
            self.population[channel].append(nickname)
            self.logger.info("Added %s to %s user list" % (nickname, channel))
        else:
            self.logger.info("%s is in %s already" % (nickname, channel))

        self.logger.info(self.population)

        self.channel.join(nickname, params)
        pass

    def irc_RPL_TOPIC(self, prefix, params):
        """??????????"""
        self.logger.info("Saw a RPL_TOPIC (!!): %s %s" % (prefix, params))
        pass

    def irc_ERR_NICKNAMEINUSE(self, prefix, params):
        """??????????"""
        self.logger.info(
            "Saw a irc_ERR_NICKNAMEINUSE (!!): %s %s" % (prefix, params))
        if (self.nickname == self.original_nickname):
            self.logger.info('[IDENTIFY] Downgrading to  ' + self.alt_nickname)
            self.register(self.alt_nickname)
            self.nickname = self.alt_nickname
        elif (self.nickname == self.alt_nickname):
            self.logger.info('[IDENTIFY] Downgrading to  ' +
                             self.original_nickname + '_')
            self.register(self.original_nickname + '_')
            self.nickname = self.original_nickname + '_'

        pass

    def irc_RPL_NAMREPLY(self, prefix, params):
        """??????????"""
        self.logger.info("Saw a irc_RPL_NAMREPLY (!!): %s %s" %
                         (prefix, params))

        server = prefix
        myname = params[0]
        atsign = params[1]
        channel = params[2]
        names = params[3].split(' ')

        #people = []

        self.population[channel] = []

        for nickname in names:
            self.logger.info("saw %s" % nickname)
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

        # self.logger.info('People: %s' % self.people)
        # self.logger.info('Population: %s' % self.population)

        #self.people = people

        pass

    def irc_333(self, prefix, params):
        """??????????"""
        self.logger.info("Saw a 333 (!!): %s %s" % (prefix, params))
        pass

    def userKicked(self, kickee, channel, kicker, message):
        """Saw someone kicked from the channel"""
        self.logger.info("Saw a kick: %s kicked %s saying %s" %
                         (kickee, kicker, message))
        self.channel.leave('kick', kickee, message)
        self.leave(kickee, channel)

        pass

    def leave(self, nickname, channel):

        if nickname[1:] in self.population[channel]:
            self.population[channel].remove(nickname[1:])
            self.logger.info(
                "[LEAVE] Removed %s from %s user list" % (nickname, channel))

        if nickname in self.population[channel]:
            self.population[channel].remove(nickname)
            self.logger.info(
                "[LEAVE] Removed %s from %s user list" % (nickname, channel))

        found = False
        for channel, people in self.population.items():
            if nickname in people:
                found = True
                self.logger.info(
                    "[LEAVE] Found %s in %s user list, keeping in dictionary" % (nickname, channel))
                return
        if not found:
            self.logger.info("[LEAVE] Lost %s entirely" % nickname)
            self.people.remove(nickname)

    def loadConfig(self):

        basedir = os.path.dirname(os.path.abspath(sys.argv[0]))
        config = ConfigParser.ConfigParser()

        config_files = ['defaults.ini', ]
        if os.path.exists(basedir + '/config.ini'):
            config_files.append(basedir + '/config.ini')
        config.read(config_files)

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
        # Todo: Implement backoff
        # time.sleep(45)  # Our very own fourty five second claim.
        # connector.connect()
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        self.logger.info("connection failed:", reason)
        reactor.stop()


if __name__ == '__main__':
    cwd = os.getcwd()
    logging.info("Error log is %s/stderr.log" % cwd)

    basedir = os.path.dirname(os.path.abspath(sys.argv[0]))
    config = ConfigParser.ConfigParser()

    config_files = ['defaults.ini', ]
    if os.path.exists(basedir + '/config.ini'):
        config_files.append(basedir + '/config.ini')
    config.read(config_files)

    server = config.get("connection", "server")
    port = config.getint("connection", "port")

    logging.info("Connecting to %s:%s" % (server, port))

    # create factory protocol and application
    f = LampstandFactory(config)

    # connect factory to this host and port
    reactor.connectTCP(server, port, f)

    # run bot

    reactor.run()
