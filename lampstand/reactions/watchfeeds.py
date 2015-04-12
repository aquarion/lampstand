import lampstand.reactions.base

import feedparser

from lampstand.tools import splitAt
import re
import time
import random
import sys


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):

    __name = 'watchFeeds'

    cooldown_number = 3
    # So if 3 requests are made in 360 seconds, it will trigger overuse.
    cooldown_time = 360
    uses = []

    schedule_count = 0

    feeds = {
        'odyssey' : {
            'url' : "https://www.facebook.com/feeds/page.php?format=rss20&id=319644741567",
            'plural': "Odyssey Updates",
            'singular': "Odyssey update",
            'channels': ['#odcfroth', ],
            'last_seen': False
        },
        'empire' : {
            'url' : "https://www.facebook.com/feeds/page.php?format=rss20&id=136575943105061",
            'plural': "Empire Updates",
            'singular': "Empire update",
            'channels': ['#empirefroth', ],
            'last_seen': False
        },
        'larphacks' : {
            'url' : "http://larphacks.tumblr.com/rss",
            'plural': "Larp Hacks",
            'singular': "Larp Hack",
            'channels': ['#maelfroth', ],
            'last_seen': False
        }

    }

    def __init__(self, connection):
        self.channelMatch = re.compile('^%s. Feed Check' % connection.nickname, re.IGNORECASE)
        # self.privateMatch = re.compile('^%s. ???' % connection.nickname,
        # re.IGNORECASE))

        # def channelAction(self, connection, user, channel, message, index =
        # 0):

        for feed in self.feeds.keys():
            self.checkFeed(feed, connection)

        # def everyLine(self, connection, user, channel, message)
        # def leaveAction(self, connection, user, reason, parameters)
        # def nickChangeAction(self, connection, old_nick, new_nick)
        # def privateAction(self, connection, user, channel, message, index)
        # def scheduleAction(self, connection)

    def channelAction(self, connection, user, channel, message, index=0):
        for feed in self.feeds.keys():
            self.checkFeed(feed, connection)

    def scheduleAction(self, connection):

        # Runs every 5 seconds, remember

        seconds_between_runs = 3000  # Half an hour

        ticks_between_runs = seconds_between_runs / 5

        self.schedule_count = self.schedule_count + 1

        if self.schedule_count >= ticks_between_runs:
            self.schedule_count = 0

        if not self.schedule_count == 0:
            return

        for feed in self.feeds.keys():
            self.checkFeed(feed, connection)

    def checkFeed(self, feedname, connection):
        feed_settings = self.feeds[feedname]
    
        print '[FeedWatch] Fetching feed ' + feed_settings['url']
        feed = feedparser.parse(feed_settings['url'])
        last_entry = feed['entries'][0]

        if self.feeds[feedname]['last_seen'] == last_entry['id']:
            print '[FeedWatch] Same as last ID: %s' % last_entry['title']
            return

        if not self.feeds[feedname]['last_seen']:
            print '[FeedWatch] No previous ID, setting, leaving: %s' % last_entry['title']
            self.feeds[feedname]['last_seen'] = last_entry['id']
            return

        self.feeds[feedname]['last_seen'] = last_entry['id']

        text = "New %s announcement: %s <%s>" % (
            self.feeds[feedname]['singular'], last_entry['title'], last_entry['link'])
        print '[FeedWatch] Announcing %s' % text
        for channel in self.feeds[feedname]['channels']:
	    print "[FeedWatch] (%s) %s" % (channel, text)
            connection.message(channel, text)

