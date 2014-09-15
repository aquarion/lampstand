import lampstand.reactions.base


from lampstand import tools
import re
import time
import random
import sys
from datetime import datetime, date, time


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):

    __name = 'Statistics'

    cooldown_number = 3
    # So if 3 requests are made in 360 seconds, it will trigger overuse.
    cooldown_time = 360
    uses = []

    def __init__(self, connection):

        self.dbconnection = connection.dbconnection

        self.channelMatch = (
            re.compile(
                '^%s. statistics' %
                connection.nickname,
                re.IGNORECASE))
        self.privateMatch = (re.compile('^statistics', re.IGNORECASE))

    def channelAction(self, connection, user, channel, message):

        if self.overUsed():
            connection.message(user, "Overuse Triggered")
            return True

        self.stats(connection, channel)

    def privateAction(self, connection, user, message, index):
        self.stats(connection, user)

    def stats(self, connection, user):
        cursor = self.dbconnection.cursor()
        # I am Lampstand.

        # I have been given questionable definitions of x things, mostly by x

        cursor.execute('select count(*) as `total` from `define`')
        total = cursor.fetchone()

        cursor.execute(
            'select count(*), author from define group by author order by count(*) DESC limit 3')
        topuser = ["A", "B", "C"]
        topuser[0] = cursor.fetchone()[1]
        topuser[1] = cursor.fetchone()[1]
        topuser[2] = cursor.fetchone()[1]

        connection.message(
            user,
            "I have been given questionable definitions of %s things, mostly by %s, %s & %s" %
            (total[0],
             topuser[0],
             topuser[1],
             topuser[2]))

        for module in connection.channelModules:
            if module.__name == "Items & Inventory":
                items = module

        inventory = len(items.items)

        cursor.execute('select count(*) as `total` from `item`')
        itemone = cursor.fetchone()

        connection.message(
            user, "I am holding %s things, and know about %s items in total" %
            (inventory, itemone[0]))

        # There are X events in the future (X in the past), totaling X hours of
        # things happening.

        # I was created X, and I've been up since X, which was X

        created = datetime(2008, 3, 7, 14, 00)
        now = datetime.now()

        creatediff = tools.nicedelta(now - created)
        launchdiff = tools.nicedelta(now - connection.date_started)

        connection.message(
            user, "I was created %s ago, and I've been up since %s, which was %s ago" %
            (creatediff, connection.date_started, launchdiff))

        # I'm listening out for X different public channel responses, X private

        channeltriggers = 0
        for mod in connection.channelModules:
            print "Chan %s" % mod
            if hasattr(mod, "channelMatch"):
                if (isinstance(mod.channelMatch,
                               tuple) or isinstance(mod.channelMatch,
                                                    list)):
                    channeltriggers += len(mod.channelMatch)
                else:
                    channeltriggers += 1

        privatetriggers = 0
        for mod in connection.privateModules:
            if hasattr(mod, "privateMatch"):
                if isinstance(
                        mod.privateMatch,
                        tuple) or isinstance(
                        mod.privateMatch,
                        list):
                    privatetriggers += len(mod.privateMatch)
                else:
                    privatetriggers += 1

        connection.message(
            user, "I'm listening out for %d different public channel phrases, %d in query" %
            (channeltriggers, privatetriggers))

        # I am 77% of the way to world domination.

    # def everyLine(self, connection, user, channel, message)
    # def leaveAction(self, connection, user, reason, parameters)
    # def nickChangeAction(self, connection, old_nick, new_nick)
    # def scheduleAction(self, connection)
