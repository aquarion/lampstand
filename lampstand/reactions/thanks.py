import re
import time
import random
import sys
import lampstand.reactions.base

import logging


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):

    __name = 'Thanks'

    cooldown_number = 2
    cooldown_time = 360
    uses = []

    def __init__(self, connection):
        self.logger = logging.getLogger(self.__name)

        self.channelMatch = re.compile(
            ".*Thanks,? (\S+)\s*\.?$",
            re.IGNORECASE)
        self.privateMatch = []

    def channelAction(self, connection, user, channel, message):
        self.logger.info("[Thanks] called")

        word = self.channelMatch.findall(message)[0]

        if not word:
            return False

        number = random.randint(0, 5)

        if number == 3:
            thanks = self.thanks(word)
            self.logger.info("[THANKS] Thanks, %s: %s" % (word, thanks))
            connection.message(channel, thanks)
            return True
        # elif word in connection.people:
        #	self.logger.info("[Thanks] Found, but not random")
        else:
            self.logger.info("[thanks] Random was %d" % number)

        return False

    def thanks(self, word):

        word = word.lower().strip()
        if not word:
            return false

        self.logger.info("Thanks, %s" % word)

        if word[0] in ("a", "e", "i", "o", "u"):

            self.logger.info("That starts with a vowel, using the whole word")

            thanks = word

        else:

            scrugg = re.split(r'[aeiouy]', word, 1)

            #scrugg = re.split(r'[^aeiouy]+', word)

            self.logger.info(scrugg)

            if len(scrugg) < 2:
                self.logger.info("Failed to split on vowels")
                return false

            if(len(scrugg) > 1):
                self.logger.info("Using second element")
                thanks = scrugg[1]
            else:
                self.logger.info("Using whole word")
                thanks = word

        if not thanks or len(thanks) < 1:
            self.logger.info("Thanks isn't good enough: %s" % thanks)
            return false

        self.logger.info(thanks)

        if(thanks[0] == "a"):
            thanks = "Th%s" % thanks
        elif(thanks[0] == "o"):
            thanks = "Th%s" % thanks
        else:
            thanks = "Tha%s" % thanks

        return thanks
