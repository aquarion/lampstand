import lampstand.reactions.base

from lampstand.tools import splitAt
import re
import time
import random
import sys
import logging


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):

    __name = 'Choose'

    cooldown_number = 6
    cooldown_time = 360
    uses = []

    def __init__(self, connection):
        self.logger = logging.getLogger(self.__name)
        self.channelMatch = re.compile(
            '^%s. (choose|should I) (.* or .*)' %
            connection.nickname,
            re.IGNORECASE)
        self.privateMatch = re.compile(
            '(choose|should I) (.* or .*)\??$',
            re.IGNORECASE)

    def channelAction(self, connection, user, channel, message):
        self.logger.info("[Choose] called")

        if self.overUsed(self.uses, self.cooldown_number, self.cooldown_time):
            connection.message(
                channel,
                "I'm not running your life for you, go away.")
            return True

        self.updateOveruse()

        match = self.channelMatch.findall(message)

        if random.randint(0, 100) == 69:
            self.logger.info("Yes")
            connection.message(channel, "%s: Yes" % user)
            return True

        if random.randint(0, 100) == 67:
            self.logger.info("Edge")
            connection.message(channel, "%s: edge" % user)
            return True

        self.logger.info(match)
        reaction = self.choose(match[0][1])
        if reaction.lower() == "death" and user.lower() != "aquarion":
            connection.kick(channel, user, "Death.")
        elif reaction.lower() == "boom" and user.lower():
            connection.kick(channel, user, "BOOM")
        else:
            connection.message(channel, "%s: %s" % (user, reaction))

        return True

    def privateAction(self, connection, user, channel, message):
        self.logger.info("[Choose] called")

        if self.overUsed(self.uses, self.cooldown_number, self.cooldown_time):
            connection.message(
                user,
                "I'm not running your life for you, go away.")
            return

        self.updateOveruse()

        match = self.privateMatch.findall(message)
        self.logger.info("Match: %s" % match)

        reaction = self.choose(match[0][1])
        connection.message(user, "%s: %s" % (user, reaction))

    def choose(self, message):
        if message[-1:] == "?":
            message = message[:-1]

        self.logger.info(message)

        # new regex by ccooke - 2010-05-28
        #regex = re.compile("(?:\s*(?:\s*(?:,|x?or)\s*)+\s*)+", re.IGNORECASE);
        #regex = re.compile("(?:\s+(?:\s*(?:x?or)\s*)+\s*|,)+", re.IGNORECASE);
        regex = re.compile(
            "(?:\s+(?:\s*(?:x?or(?=\W))\s*)+\s*|,)+\s*",
            re.IGNORECASE)
        choose = regex.split(message)

        #choose = []

        #orsplit = message.split(" or ")
        # for thing in orsplit:
        #	lst = thing.split(", ")
        #	for x in lst:
        #        choose.append(x)
        # self.logger.info(choose)

        self.logger.info(choose)

        for thing in choose:
            if thing.lower() == "glados":
                self.logger.info("Chosen Glados")
                return "GLaDOS. Obviously"

            if thing.lower() == "hal":
                self.logger.info("Removed a Hal")
                choose.remove(thing)

        self.logger.info(choose)
        return random.choice(choose)
