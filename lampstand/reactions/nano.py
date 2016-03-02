import re
import time
import random
import sys
import math
import lampstand.reactions.base
from lampstand import tools
import datetime

import logging


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):

    __name = 'Nano'

    cooldown_number = 2
    cooldown_time = 360
    uses = []

    def __init__(self, connection):
        self.logger = logging.getLogger(self.__name)
        self.channelMatch = re.compile(
            "^%s. how many words" %
            connection.nickname,
            re.IGNORECASE)
        self.privateMatch = re.compile("^how many words", re.IGNORECASE)

    def channelAction(self, connection, user, channel, message):
        connection.message(channel, "%s: %s" % (user, self.nano()))

    def privateAction(self, connection, user, channel, message):
        connection.message(user, self.nano())

    def nano(self):
        self.logger.info("[Nano] called")

        now = time.time()

        then = time.mktime(
            datetime.datetime(
                datetime.datetime.now().year,
                11,
                1,
                00,
                00).timetuple())

        delta = now - then

        target = 50000.0
        month = 2592000.0

        end = then + month

        if now > then + month:
            return "You should have finished by now"

        if delta < 0:
            delta = math.fabs(delta)
            return "You should start Nanowrimo in %s" % tools.niceTimeDelta(
                delta,
                "decimal")

        persec = target / month

        current = delta * persec

        return "You should be at %d words by now, %s left" % (
            current, tools.niceTimeDelta(month - delta))
