import lampstand.reactions.base


from lampstand.tools import splitAt
import re
import time
import random
import sys


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):

    __name = 'Cutout'

    def everyLine(self, connection, user, channel, message):

        if len(message) > 450 or (len(message) > 357 and len(message) <= 362):
            print "[CUTOUT] Message length: %s" % len(message)
            index = len(message) - 1
            words = 0
            maxword = 5
            whitespace = re.compile('\s')

            while words < maxword and index > 400:
                if whitespace.match(message[index]):
                    words = words + 1
                index = index - 1

            index = index + 2

            cutout = message[index:]

            if len(cutout) > 0:
                connection.message(
                    channel, "%s: I think that cut out at \"%s\"" %
                    (user, cutout))

            return True
