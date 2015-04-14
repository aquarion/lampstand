import re
import time
import random
import sys
import urllib
import os
import datetime
import lampstand.reactions.base

from xml.dom.minidom import parse, parseString

import logging

def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):
    __name = 'Steam Play'

    cooldown_number = 5
    cooldown_time = 120
    uses = []

    def __init__(self, connection):
        self.logger = logging.getLogger(self.__name)

        self.channelMatch = (
            re.compile(
                '%s: wh(at|ich) (game |)should I play\?' %
                connection.nickname,
                re.IGNORECASE),
            re.compile(
                '%s: my steam profile is (\S*)' %
                connection.nickname,
                re.IGNORECASE),
            re.compile(
                '%s: wh(at|ich) steam game should I play\?' %
                connection.nickname,
                re.IGNORECASE),
            re.compile(
                '%s: wh(at|ich) of my recent steam games should I play\?' %
                connection.nickname,
                re.IGNORECASE))

        self.privateMatch = (
            re.compile(
                'wh(at|ich) (game | )should I play\?',
                re.IGNORECASE),
            re.compile(
                'my steam profile is (\S*)',
                re.IGNORECASE),
            re.compile(
                'wh(at|ich) steam game should I play\?',
                re.IGNORECASE),
            re.compile(
                'wh(at|ich) of my recent steam games should I play\?',
                re.IGNORECASE))

        self.dbconnection = connection.dbconnection

    def respond(self, user, matchIndex, matches):
        if matchIndex == 0 or matchIndex == 2:
            output = self.playWhat(user)
        elif matchIndex == 3:
            output = self.playWhat(user, limitToRecent=True)
        elif matchIndex == 1:
            result = matches
            output = self.setSteam(user, result)

        return output

    def channelAction(
            self,
            connection,
            user,
            channel,
            message,
            matchIndex=False):
        self.logger.info("[PLAY] Reacting...")
        if self.overUsed(self.uses):
            connection.message(channel, self.overuseReactions[matchIndex])
            return True

        ## Overuse Detectection ##
        self.uses.append(int(time.time()))
        if len(self.uses) > self.cooldown_number:
            self.uses = self.uses[0:self.cooldown_number - 1]
        ## Overuse Detectection ##

        matches = self.channelMatch[matchIndex].findall(message)

        output = self.respond(user, matchIndex, matches)

        if output:
            output = "%s: %s" % (user, output)
        else:
            output = "%s: Settlers of Catan? Monopoly? Steam's not talking to me right now, sorry." % user

        connection.message(channel, output)

    def privateAction(
            self,
            connection,
            user,
            channel,
            message,
            matchIndex=False):

        matches = self.privateMatch[matchIndex].findall(message)
        output = self.respond(user, matchIndex, matches)

        connection.message(user, output)

    def playWhat(self, username, limitToRecent=False):

        self.logger.info("[PLAY] Looking up games for %s" % username)
        cursor = self.dbconnection.cursor()
        cursor.execute(
            'SELECT steamname from gameaccounts where username = %s',
            username)
        result = cursor.fetchone()

        if result is None:
            return self.helptext()

        try:
            steam = self.getSteamXML(result[0])
        except:
            return False

        self.logger.info(steam)

        if hasattr(steam, '__getitem__'):
            return steam[1]

        return self.pickAGame(steam, limitToRecent=limitToRecent)

    def helptext(self):

        return """I don't have a steam account for you, sorry. Set this by saying "my steam profile is [SOMETHING]" to me. To find what '[SOMETHING]' should be log in to steamcommunity.com and it's the word after "/id/" or the numbers after "/profile/" in the URL of your home page."""

    def setSteam(self, username, result):

        steamname = result[0]

        try:
            steam = self.getSteamXML(steamname)
        except:
            return False

        if hasattr(steam, '__getitem__'):
            return steam[1]

        nameElement = steam.getElementsByTagName('steamID')[0]
        accountName = nameElement.childNodes[0].data

        cursor = self.dbconnection.cursor()
        cursor.execute(
            'REPLACE into gameaccounts (username, steamname) values (%s, %s)',
            (username,
             steamname))
        self.dbconnection.commit()

        return "Okay, remembering that %s's steam name is %s, aka '%s'" % (
            username, steamname, accountName)

        return "Stub %s" % result

    def pickAGame(self, steam, limitToRecent=False):

        if random.randint(0, 100) == 25:
            return "Odyssey, obviously"

        if not limitToRecent and random.randint(0, 2) == 1:
            limitToRecent = True

        if limitToRecent:
            recentGames = steam.getElementsByTagName('hoursLast2Weeks')
            if not len(recentGames):
                limitToRecent = False

        if not limitToRecent:
            games = steam.getElementsByTagName('game')
            game = random.choice(games)
        else:
            game = random.choice(recentGames).parentNode

        gamename = game.getElementsByTagName('name')[0].childNodes[0].data

        return gamename

    def getSteamXML(self, username):

        username = username.lower()

        try:
            i = int(username)
        except ValueError as TypeError:
            profiletype = 'id'
        else:
            profiletype = 'profiles'

        steamurl = "http://steamcommunity.com/%s/%s/games?tab=all&xml=1" % (
            profiletype, username)

        self.logger.info(steamurl)

        cachename = "/tmp/steam.lampstand.%s.xml" % username

        (fileopen, fileheaders) = urllib.urlretrieve(steamurl, cachename)

        self.logger.info("Examining %s" % cachename)

        stat = os.stat(fileopen)
        delta = datetime.datetime.now() - \
            datetime.datetime.fromtimestamp(stat.st_mtime)
        if delta.seconds > 60 * 60 * 12:
            self.logger.info(" ... Redownloading, cache expired %s" % (delta.seconds / 60 * 60))
            os.remove(fileopen)
            (fileopen, fileheaders) = urllib.urlretrieve(steamurl, cachename)

        try:
            steam = parse(fileopen)
        except ParseError:
            return (16, "Error getting the response from steam")
        except:
            return (128, "Something crazy happened: <%s>" % sys.exc_info()[0])

        steamerror = steam.getElementsByTagName('error')
        if len(steamerror) > 0:
            return (
                32,
                "Sorry, Steam said: %s" %
                steamerror[0].childNodes[0].data)

        return steam
