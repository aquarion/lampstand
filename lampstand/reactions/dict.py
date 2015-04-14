import dictclient
from lampstand.tools import splitAt
import lampstand.reactions.base
import re
import time
import socket
import dns.resolver

import logging

def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):

    __name = 'Dictionary'

    cooldown_number = 5
    cooldown_time = 420

    def __init__(self, connection):
        self.logger = logging.getLogger(self.__name)
        self.channelMatch = re.compile(
            '%s. look up (\w*)\s*$' %
            connection.nickname,
            re.IGNORECASE)
        self.privateMatch = re.compile('look up (\w*)\s*$', re.IGNORECASE)

    def getDefinition(self, query):

        specialDict = {
            'foip': 'FOIP (\'Find Out In Play\') is any information you have that another character in the system does not have. Therefore, it is anything not on the website, in the almanac or in the rules books. Broadcasting this is a kickable offence on #maelfroth. If someone claims what you are talking about is FOIP, you need to stop talking about it as you may be damaging the game of others.',
            'herring': 'Type of fish. There is nothing between it and Marmalade it in my dictionary. My dictionary is not in alphabetical order, which is why it still has "kelp"',
            'marmalade': 'A type of citrus-based conserve. There is nothing before it in my dictionary until "herring". My dictionary is oddly ordered, however, so it still contains "Lemur"',
            'catbus': 'You don\'t want to know.',
            'glados': '*happy sigh*',
            'lampstand': "That's me. Hi there",
            'hal': 'grrrrr.',
            'inconceivable': 'adj. Not what you think it means.',
            'tenant': 'n. An opinion, doctrine, or principle held as being true by a person or especially by an organization',
            'tenet': 'n. One that pays rent to use or occupy land, a building, or other property owned by another.'}

        if query.lower() in specialDict:
            return specialDict[query.lower()]

        src = False

        try:
            dictcxn = dictclient.Connection("dict.org")
            dfn = dictcxn.define("*", query)
            if dfn:
                dfn = dfn[0].getdefstr()

            src = "Dictionary"
        except socket.error:
            self.logger.info("[Define] Argh. Dictionary server's offline")
            connection.message(
                channel,
                "Sorry, but my dictionary server's not working.")
            dfn = None

        # if not dfn:
        #    self.logger.info("Nothing in Dictionary, looking up on wikipedia")
        #    try:
        #        dfn = dns.resolver.query('%s.wp.dg.cx' % query, 'TXT')
        #        if dfn:
        #            dfn = str(dfn[0])
        #            dfn = re.sub(r'\\(.)', r'\1', dfn)
        #            src = "Wikipedia"
        #    except dns.resolver.NXDOMAIN:
        #        dfn = False

        if not dfn:
            return None

        result = ' '.join(dfn.split('\n'))

        return (result, src)

    def splitDefinition(self, result):

        string = []

        if len(result) > 880:
            whereToSplit = splitAt(result, 860)
            result = "%s [Cut for length]" % result[0:whereToSplit]

        string.append("%s" % result)

        self.logger.info(string)

        return string

    def channelAction(self, connection, user, channel, message):
        matches = self.channelMatch.findall(message)

        self.logger.info("[Define] %s" % matches)

        if self.overUsed():
            connection.message(
                user,
                "The dictionary is on fire. Leave it alone. (Overuse triggered)")
            return

        self.updateOveruse()
        try:
            result, src = self.getDefinition(matches[0])
        except:
            connection.message(
                channel,
                "%s: There is no such word as '%s' in my dictionary. In fact, everything between 'herring' and 'marmalade' appears to be completely missing." %
                (user,
                 matches[0]))
            return True

        self.logger.info("[Define] %s" % result)

        messages = self.splitDefinition(result)
        for message in messages:
            connection.message(channel, "%s: %s" % (user, message))

        return True

    def privateAction(self, connection, user, channel, message):
        matches = self.privateMatch.findall(message)

        self.logger.info("[Define] %s" % matches)
        try:
            result, src = self.getDefinition(matches[0])

        except:
            connection.message(
                user,
                "%s: There is no such word as '%s' in my dictionary. In fact, everything between 'herring' and 'marmalade' appears to be completely missing." %
                (user,
                 matches[0]))
            return True

        self.logger.info("[Define] %s" % result)

        if len(result) > 880:

            whereToSplit = splitAt(result, 860)
            result = "%s [Cut for length]" % result[0:whereToSplit]

        if len(result) > 440:
            whereToSplit = splitAt(result, 440)
            stringOne = result[0:whereToSplit]
            stringTwo = result[whereToSplit:]

            connection.message(user, "%s... " % stringOne)
            connection.message(user, "... %s" % stringTwo)
        else:
            connection.message(user, "%s" % result)

        return True
