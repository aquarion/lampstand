import re
import lampstand.reactions.base
from lampstand import calendar_facts

import logging


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):
    __name = 'Calendar Facts'

    cooldown_number = 3
    cooldown_time = 60
    uses = []

    def __init__(self, connection):
        self.logger = logging.getLogger(self.__name)
        self.channelMatch = re.compile(
            '%s. (give me a )?calendar fact' %
            connection.nickname,
            re.IGNORECASE)

    def channelAction(self, connection, user, channel, message):

        self.logger.info("[CALENDARFACT] called")

        if self.overUsed():
            connection.message(
                user,
                "Tomorrow is cancelled (Overuse triggered)")
            return

        fact = calendar_facts.fact()

        self.updateOveruse()

        connection.message(channel, "%s, %s" % (user, fact))
        return True
