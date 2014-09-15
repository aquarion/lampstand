import lampstand.reactions.base

from lampstand.tools import splitAt
import re
import time
import random
import sys


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):

    __name = 'Package'

    cooldown_number = 2
    # So if 1 requests is made in 360 seconds, it will trigger overuse.
    cooldown_time = 360
    uses = []

    package_in_play = False
    package_owner = False
    package_player = False
    package_message = False
    its_a_bomb = False
    sticky_bomb = False
    this_channel = False

    messages = [
        "Do you hear that, %s? The package appears to be ticking!",  # 0
        "Tick, tick it goes, %s, Tick, tick, tick",  # 5
        "",  # 10
        "Is it speeding up, %s? Tick, Tick, Tickity tick tick tick",  # 15
        "",  # 20
        "%s: tickTickTickTick"  # 25
    ]

    def __init__(self, connection):
        self.channelMatch = (
            re.compile(
                '(hands|gives) (.*) (a|the) (suspicious|) package',
                re.IGNORECASE),
        )
        # self.privateMatch = re.compile('^%s. ???' % connection.nickname,
        # re.IGNORECASE))

        self.reset()

    def reset(self):
        self.package_in_play = False
        self.package_owner = False
        self.message_number = False
        self.package_player = False
        self.its_a_bomb = False
        self.sticky_bomb = False
        self.this_channel = False

    def channelAction(self, connection, user, channel, message, index):

        if not user.lower() == "aquarion":
            print "Bomb disabled"
            connection.message(
                user,
                "The packages function has been disabled.")
            return False

        if self.overUsed():
            connection.message(user, "Overuse Triggered")
            return True

        print "[PACKAGE]"

        matchwork = self.channelMatch[0].findall(message)

        print matchwork

        hands = matchwork[0][0]
        player = matchwork[0][1]

        non_players = [connection.nickname.lower(), ]

        # if self.package_in_play:
        #	non_players.append(self.package_player.lower())

        if not self.package_in_play:
            self.updateOveruse()

            if player.lower() in non_players:
                connection.message(channel, "%s: No." % user)
                return False

            if player.lower() not in map(str.lower, connection.people):
                connection.message(channel, "%s: Who?" % user)
                return False

            self.package_in_play = True
            self.package_owner = user
            self.package_player = player
            self.message_number = 0
            self.its_a_bomb = (user.lower() == "aquarion" and hands == "hands")
            self.sticky_bomb = (
                user.lower() == "aquarion" and hands == "hands")
            self.this_channel = channel

            sticky_txt = ""

            if self.sticky_bomb:
                sticky_txt = "slightly sticky "

            connection.message(
                channel, "Hey look, a %spackage for %s" %
                (sticky_txt, player))

        elif user == self.package_player and not player in non_players and not self.sticky_bomb:
            connection.message(channel, "%s: Noted" % user)
            self.package_player = player
        elif user == self.package_player and (player in non_players or self.sticky_bomb):
            connection.message(channel, "%s: No" % user)
        elif not user == self.package_player:
            connection.message(channel, "%s: You don't have it" % user)

        print "[/PACKAGE]"
        return True

    # def everyLine(self, connection, user, channel, message)
    # def leaveAction(self, connection, user, reason, parameters)
    # def nickChangeAction(self, connection, old_nick, new_nick)
    # def privateAction(self, connection, user, channel, message, index)

    def scheduleAction(self, connection):

        channel = self.this_channel

        if self.package_in_play:
            print self.message_number, '/', len(self.messages)
            if self.message_number < len(self.messages):
                print "Send message"

                print self.message_number, self.messages[self.message_number]

                if self.messages[self.message_number]:
                    message = self.messages[
                        self.message_number] % self.package_player
                    connection.message(channel, message)
                self.message_number += 1
            else:
                print "Go Boom"
                if self.its_a_bomb and not self.package_player.lower(
                ) == "aquarion":
                    connection.kick(
                        self.this_channel,
                        self.package_player,
                        "*BOOM*")
                else:
                    connection.message(channel, "*BOOM*")

                self.reset()

    def nickChangeAction(self, connection, old_nick, new_nick):
        if old_nick == self.package_player:
            self.package_player = new_nick

        if old_nick == self.package_owner:
            self.package_owner = new_nick
