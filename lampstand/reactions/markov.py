import lampstand.reactions.base

import lampstand.markov as markov

from lampstand.tools import splitAt
import re, time, random, sys


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):

    __name = 'Markov'

    cooldown_number = 3
    cooldown_time = 360  # So if 3 requests are made in 360 seconds, it will trigger overuse.
    uses = []

    def __init__(self, connection):
        self.channelMatch = re.compile('^%s. contribute' % connection.nickname, re.IGNORECASE)
        # self.privateMatch = re.compile('^%s. ???' % connection.nickname, re.IGNORECASE))

    def channelAction(self, connection, user, channel, message, index=0):

        if self.overUsed():
            connection.message(user, "Overuse Triggered")
            return True

        for module in connection.channelModules:
            if module.__name == "Memory":
                memory = module;

        words = ""
        for line in memory.memory[channel]:
            words = words + " " + line['message']

        mark = markov.Markov(words)

        print words
        print mark.words

        text = mark.generate_markov_text(50)

        print text

        connection.msg(channel, text);

    # def everyLine(self, connection, user, channel, message)
    # def leaveAction(self, connection, user, reason, parameters)
    # def nickChangeAction(self, connection, old_nick, new_nick)
    # def privateAction(self, connection, user, channel, message, index)
    # def scheduleAction(self, connection)
