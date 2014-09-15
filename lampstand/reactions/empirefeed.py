import lampstand.reactions.base

import feedparser

from lampstand.tools import splitAt
import re, time, random, sys


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):

    __name = 'EmpireFeed'

    cooldown_number = 3
    cooldown_time = 360  # So if 3 requests are made in 360 seconds, it will trigger overuse.
    uses = []

    schedule_count = 0

    last_empire_seen = False
    last_odyssey_seen = False

    def __init__(self, connection):
        #self.channelMatch = re.compile('^%s. Empire Feed Check' % connection.nickname, re.IGNORECASE)
        # self.privateMatch = re.compile('^%s. ???' % connection.nickname, re.IGNORECASE))

        # def channelAction(self, connection, user, channel, message, index = 0):

        #     self.checkEmpireFeed(connection)
        #     self.checkOdysseyFeed(connection)

        # def everyLine(self, connection, user, channel, message)
        # def leaveAction(self, connection, user, reason, parameters)
        # def nickChangeAction(self, connection, old_nick, new_nick)
        # def privateAction(self, connection, user, channel, message, index)
        # def scheduleAction(self, connection)

    def scheduleAction(self, connection):

        # Runs every 5 seconds, remember

        seconds_between_runs = 3000  # Half an hour

        ticks_between_runs = seconds_between_runs / 5

        self.schedule_count = self.schedule_count + 1

        if self.schedule_count >= ticks_between_runs:
            self.schedule_count = 0

        if not self.schedule_count == 0:
            return

        self.checkEmpireFeed(connection)
        self.checkOdysseyFeed(connection)

    def checkEmpireFeed(self, connection):
        empire_feed = 'https://www.facebook.com/feeds/page.php?format=rss20&id=136575943105061'
        print '[EmpireFeed] Fetching feed'
        feed = feedparser.parse(empire_feed)
        last_entry = feed['entries'][0]

        if self.last_empire_seen == last_entry['id']:
            print '[EmpireFeed] Same as last ID: %s' % last_entry['title']
            return

        if not self.last_empire_seen:
            print '[EmpireFeed] No previous ID, setting, leaving: %s' % last_entry['title']
            self.last_empire_seen = last_entry['id']
            return

        self.last_empire_seen = last_entry['id']

        text = "New Empire Facebook announcement: %s <%s>" % (last_entry['title'], last_entry['link'])
        print '[EmpireFeed] Announcing %s' % text
        connection.message("#empirefroth", text)

    def checkOdysseyFeed(self, connection):
        empire_feed = 'https://www.facebook.com/feeds/page.php?format=rss20&id=319644741567'
        print '[OdysseyFeed] Fetching feed'
        feed = feedparser.parse(empire_feed)
        last_entry = feed['entries'][0]

        if self.last_odyssey_seen == last_entry['id']:
            print '[OdysseyFeed] Same as last ID: %s' % last_entry['title']
            return

        if not self.last_odyssey_seen:
            print '[OdysseyFeed] No previous ID, setting, leaving: %s' % last_entry['title']
            self.last_odyssey_seen = last_entry['id']
            return

        self.last_odyssey_seen = last_entry['id']

        text = "New Odyssey Facebook announcement: %s <%s>" % (last_entry['title'], last_entry['link'])
        print '[OdysseyFeed] Announcing %s' % text
        connection.message("#odcfroth", text)
