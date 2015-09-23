# Mostly by Aquarion, modifiers (openended/lowest/best) code by ccooke.

from lampstand.tools import splitAt
import re
import time
import random
import sys
import string
import lampstand.reactions.base
import logging
import traceback

def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):
    __name = 'Dice'

    cooldown_number = 6
    cooldown_time = 120

    def __init__(self, connection):
        self.logger = logging.getLogger(self.__name)
        self.logger = logging.getLogger(self.__name)
        self.channelMatch = (
            re.compile(
                '%s. roll +((?:\w+ +)*)(\d*d\d*)(.*)' %
                connection.nickname,
                re.IGNORECASE),
            re.compile(
                '%s. roll (.*)' %
                connection.nickname,
                re.IGNORECASE))
        self.privateMatch = re.compile(
            'roll +((?:\w+ +)*)(\d*d\d*)(.*)',
            re.IGNORECASE)

    def channelAction(self, connection, user, channel, message, index):

        item = self.channelMatch[index].findall(message)
        result = self.rollDice(item)
        connection.message(channel, "%s: %s" % (user, result))
        return True

    def privateAction(self, connection, user, channel, message, matchindex=0):
        item = self.privateMatch.findall(message)
        result = self.rollDice(item)
        connection.message(user, result)

    def rollDice(self, item):

        if self.overUsed():
            return "The dice are too hot to touch. Give them a couple of minutes to cool down."

        #item = self.channelMatch.findall(message);

        if random.randint(0, 100) == 66:
            self.logger.info("[ROLLING DICE] Rickroll!")
            return "You rolled %s. You get Rick Astley." % item[0][0]

        modifiers = {
            'openended': False,
            'bestN': False,
            'lowestN': False
        }

        if item[0] == "fate" or item[0] == "fudge":
            fate = [0, 0, 0, 0]
            total = 0
            for n in (0, 1, 2, 3):
                roll = random.randint(-1, 1)
                self.logger.info(roll)
                if roll == -1:
                    fate[n] = "-"
                elif roll == 1:
                    fate[n] = "+"
                else:
                    fate[n] = ' '
                total = total + roll
            return "You rolled [%s] [%s] [%s] [%s], totalling %s" % (
                fate[0], fate[1], fate[2], fate[3], total)

        if item[0][0]:
            # We have some keywords.
            keywords = item[0][0].lower()

            self.logger.info(keywords)
            if "open" in keywords:
                self.logger.info("[DIE KEYWORD] openended")
                modifiers['openended'] = True

            match = re.search("lowest(\d+)", keywords)
            if match:
                self.logger.info("[DIE KEYWORD] lowestN = %s" % match.group(1))
                modifiers['lowestN'] = int(match.group(1))

            match = re.search("best(\d+)", keywords)
            if match:
                self.logger.info("[DIE KEYWORD] bestN = %s" % match.group(1))
                modifiers['bestN'] = int(match.group(1))

        self.logger.info("[ROLLING DICE] %s" % item)
        try:
            result = self.roll(item[0][1], modifiers)
        except Exception as e:
            self.logger.error("[DIE KEYWORD] Exception: %s" % e)
            self.logger.error(traceback.format_exc())
            return "The dice blew up."
            return True

        self.logger.info("[ROLLING DICE] got %s" % result)

        if not result:
            return "I don't understand that format yet, sorry :("

        total = 0.0
        for elem in result[0]:
            total = total + elem

        originaltotal = total

        roll = map(lambda x: "%.6g" % x, result[0])

        if len(result) == 3 and len(result[2]) > 0:
            original = map(lambda x: "%.6g" % x, result[2])
            if original == roll:
                message = "you rolled [ %s ], Total: %.6g" % (
                    ", ".join(original), total)
            else:
                message = "you rolled [ %s ], We kept [ %s ] Total %.6g" % (
                    ", ".join(original),
                    ", ".join(roll),
                    total
                )
        elif len(roll) == 1:
            message = "you rolled [ %s ]" % roll[0]

        else:
            message = "you rolled [ %s ] Total %.6g " % (
                ', '.join(roll),
                total
            )

        self.logger.info("Item: %s " % item)

        if len(item[0]) > 1 and item[0][2] != '':
            oldtotal = total
            modifier = ''.join(item[0][2].split(' '))
            self.logger.info("Modifier is %s" % modifier)
            self.logger.info("Modifier is %s -- %s" % (modifier[0], modifier[1:]))

            if modifier[0] == "+":
                total = total + string.atof(modifier[1:])
            if modifier[0] == "-":
                total = total - string.atof(modifier[1:])
            if modifier[0] == "*":
                total = total * string.atof(modifier[1:])
            if modifier[0] == "/":
                total = total / string.atof(modifier[1:])

            message = "%s %s = %d " % (message, modifier, total)

        self.updateOveruse()
        return message

    def roll(self, dice, modifiers):
        '''dice is a string of form idj, e.g. 2d6, and rolls i j-sided dice, and returns the result as an array'''
        data = dice.split('d')
        # data validation
        if(len(data) != 2):
            return False

        try:
            type = int(data[1])
            if data[0] == '':
                # defaults to 1
                howmany = 1
            else:
                howmany = int(data[0])
        except:
            return False

        if(howmany > 128):
            return False

        if(howmany < 1 or type < 1):
            return False

        results = []
        for i in range(0, howmany):
            overrun = False
            scale = 1.0
            value = 0
            while True:
                roll = random.randrange(1, type + 1)
                self.logger.info("[DICE] Rolled a %s " % roll)
                if modifiers['openended'] and (roll == 1 or roll == type):
                    if roll == 1:
                        self.logger.info("[DICE] Rerolling that 1....")
                        value = 0
                    elif roll == type:
                        value = type - (1 / scale)
                    scale *= type
                    overrun = roll
                else:
                    value += (roll / scale)
                    break
            if not overrun:
                results.append(value)
            else:
                results.append(value)

        self.logger.info(modifiers)
        original = results[:]
        changed = False
        if modifiers['bestN']:
            self.logger.info("Length: %d" % modifiers['bestN'])

            while len(results) > modifiers['bestN']:
                self.logger.info("Length: %d" % len(results))
                results.remove(min(results))
                self.logger.info("Changed")
                changed = True

        if modifiers['lowestN']:
            while len(results) > modifiers['lowestN']:
                results.remove(max(results))
                self.logger.info("Changed")
                changed = True

        # if not changed:
        #	self.logger.info("No change!")
        #	original = []

        return [results, str(howmany) + 'd' + str(type), original]
