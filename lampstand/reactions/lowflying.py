from lampstand.tools import splitAt
import lampstand.reactions.base
from lampstand import tools
import os.path
import re
import time
import datetime

import dateutil.parser
import pytz

import sys
import os

from datetime import datetime

from twitter import Twitter

from twitter.oauth import OAuth, write_token_file, read_token_file
from twitter.oauth_dance import oauth_dance


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):
    __name = 'Low Flying Rocks'

    admin = ("aquarion")

    cooldown_number = 5
    cooldown_time = 120
    uses = []

    last_lfr_seen = False
    schedule_count = 30

    def __init__(self, connection):
        self.dbconnection = connection.dbconnection

        self.output_channel = "#%s" % connection.config.get(
            "lowflyingrocks",
            "channel")

        OAUTH_FILENAME = os.environ.get(
            'HOME',
            '') + os.sep + '.lampstand_oauth'
        CONSUMER_KEY = connection.config.get("twitter", "consumer_key")
        CONSUMER_SECRET = connection.config.get("twitter", "consumer_secret")

        if not os.path.exists(OAUTH_FILENAME):
            oauth_dance(
                "Lampstand", CONSUMER_KEY, CONSUMER_SECRET,
                OAUTH_FILENAME)

        self.oauth_token, self.oauth_token_secret = read_token_file(
            OAUTH_FILENAME)

        self.twitter = Twitter(
            auth=OAuth(
                self.oauth_token,
                self.oauth_token_secret,
                CONSUMER_KEY,
                CONSUMER_SECRET),
            secure=True,
            domain='api.twitter.com')

    def scheduleAction(self, connection):

        # Runs every 5 seconds, remember

        seconds_between_runs = 3000  # Half an hour

        ticks_between_runs = seconds_between_runs / 5

        self.schedule_count = self.schedule_count + 1

        # print "[LFR] %s/%s" % (self.schedule_count, ticks_between_runs)

        if self.schedule_count >= ticks_between_runs:
            self.schedule_count = 0

        if not self.schedule_count == 0:
            return

        channel = self.output_channel

        print "[LFR] Checking for Low Flying Rocks"

        if not self.last_lfr_seen:
            print "[LFR] First Run"
            statuses = self.twitter.statuses.user_timeline(
                screen_name="lowflyingrocks")
            last = statuses[0]
            #text = "Space object %s" % last['text']
            #connection.message(channel, text)
            self.last_lfr_seen = last['id']
        else:
            print "[LFR] Future Run (from %d)" % self.last_lfr_seen
            statuses = self.twitter.statuses.user_timeline(
                screen_name="lowflyingrocks",
                since_id=self.last_lfr_seen)
            if(len(statuses)):
                print "[LFR] Rocken! :("
                self.last_lfr_seen = statuses[0]['id']
                for status in statuses:
                    text = "Space object %s" % status['text']
                    connection.message(channel, text)
                    print "[LFR] %s" % text
            else:
                print "[LFR] ... No rocks :("
