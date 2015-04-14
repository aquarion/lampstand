import re
import lampstand.reactions.base
from lampstand import shakeinsult

import logging

def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):
    __name = 'Insulter'

    cooldown_number = 3
    cooldown_time = 60
    uses = []

    def __init__(self, connection):
        self.logger = logging.getLogger(self.__name)
        self.channelMatch = re.compile(
            '%s. insult (.*)(\W?)' %
            connection.nickname,
            re.IGNORECASE)

    def channelAction(self, connection, user, channel, message):

        self.logger.info("[INSULT] called")

        if self.overUsed():
            connection.message(
                user,
                "I'm bored of this, insult them yourself. (Overuse triggered)")
            return

        item = self.channelMatch.findall(message)

        orig_insultee = item[0][0]
        insultee = re.sub(r'\W', '', item[0][0])

        if insultee.lower() == 'me':
            insultee = user
            orig_insultee = user

        self.logger.info("[INSULT] Insulting %s" % insultee)

        if insultee.lower() == 'glados':
            self.logger.info("Kicking %s for taking the name of my lady in vain" % user)
            connection.kick(channel, user, 'No')
            return

        if insultee.lower() == connection.nickname.lower():
            connection.message(channel, "%s: No." % user)
            return

        if insultee.lower() == 'aquarion':
            connection.message(channel, "%s: Do I look suicidal? No." % user)
            return

        ownerMatch = re.compile('.*aquarion.*', re.IGNORECASE)
        myNameMatch = re.compile('.*%s.*' % connection.nickname, re.IGNORECASE)
        if ownerMatch.match(item[0][0]) or myNameMatch.match(insultee):
            connection.message(
                channel,
                "%s: Hah. Very clever. Still no." %
                user)
            return

        ownerMatch = re.compile('.*your m.m.*', re.IGNORECASE)
        myNameMatch = re.compile('.*%s.*' % connection.nickname, re.IGNORECASE)
        if ownerMatch.match(item[0][0]) or myNameMatch.match(insultee):
            connection.message(
                channel,
                "%s: She was a saint. And a toaster." %
                user)
            return

        self.logger.info("%s" % item)
        insult = shakeinsult.shakeinsult(1)

        self.updateOveruse()

        connection.message(channel, "%s, %s" % (orig_insultee, insult))
        return True
