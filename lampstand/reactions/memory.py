from lampstand.tools import splitAt
import re
import time
import random
import sys
import datetime
import lampstand.reactions.base
from lampstand import tools


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):
    __name = 'Memory'

    def __init__(self, connection):
        self.dbconnection = connection.dbconnection
        self.memory = {}
        self.channelMatch = ()

        self.memorysize = 1000

    def everyLine(self, connection, user, channel, message):
        if channel not in self.memory:
            print "New memorybank for %s channel" % channel
            self.memory[channel] = []

        line = {
            "timestamp": time.localtime(
                time.time()),
            "user": user,
            "message": message}
        self.memory[channel].append(line)
        if len(self.memory[channel]) > self.memorysize:
            limit = 0 - self.memorysize
            self.memory[channel] = self.memory[channel][limit:]

    def search(self, channel, user=False, filter=False):
        if channel not in self.memory:
            return []
        lines = self.memory[channel][:]
        if user:
            print "looking for user %s " % user
            for line in lines[:]:
                if not line['user'].lower() == user.lower():
                    lines.remove(line)
                    print "Dropping %s: %s" % (line['user'], line['message'])

        if filter:
            filter = filter.lower()
            print "looking for filter %s " % filter
            for line in lines[:]:
                if line['message'].lower().find(filter) == -1:
                    lines.remove(line)
                    print "Dropping %s: %s" % (line['user'], line['message'])

        for line in lines:
            print "Kept %s: %s" % (line['user'], line['message'])

        return lines

        pass

    def dump(self, connection, user, reason, params):
        print self.memory
