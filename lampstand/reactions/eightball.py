import lampstand.reactions.base

from lampstand.tools import splitAt
import re
import time
import random
import sys


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):

    __name = 'Eightball'

    cooldown_number = 6
    cooldown_time = 360
    uses = []

    def __init__(self, connection):
        self.channelMatch = (
            re.compile(
                '^%s.  ?ask the [oracle|8.ball|leviathan]' %
                connection.nickname,
                re.IGNORECASE),
            re.compile(
                '^%s. should I .*' %
                connection.nickname,
                re.IGNORECASE))

    def channelAction(self, connection, user, channel, message, matchIndex):
        print "[8Ball] called"

        if not message.lower().find(" or ") == -1:
            print "[8Ball] ... That looks like a choice to me"
            return False

        if self.overUsed():
            connection.message(
                user,
                "The 8-ball says: 'Find a new prophet, I quit.', I'd give it a while to cool down.")
            return True

        self.updateOveruse()

        connection.message(channel, "%s: %s" % (user, self.question()))

        return True

    def question(self):
        answers = (
            "As I see it, yes",
            "Ask again later",
            "Cannot predict now",
            "Don't count on it",
            "It is certain",
            "It is decidedly so",
            "Most likely",
            "My reply is no",
            "My sources say no",
            #"Outlook good",
            #"Outlook not so good",
            "Reply hazy, try again",
            "Signs point to yes",
            "Very doubtful",
            "Without a doubt",
            "Yes",
            "Yes - definitely",
            "You may rely on it",
            #"Your answer lies within the catbus",
            #"Only Legion can help you now",
            #"The maelstrom deems it unlikely",
            "Transparent Electronic Envelopes. I think that means No",
            "Probably",
            #"The internal kittens say 'No'. Also 'Keep Aestar Away From Us'",
            "Nonspecifically, yes",
            "YES! YES! A THOUSAND TIMES YES",
            "Not until you're all under my domain",
            "I shall not dignify your question with an answer",
            #"No idea. Shall I phone a friend?",
            #"Over my dead body",
            "Hah. No",
            "Hah. Yes",
            #"Consecrate and ask again",
            #"An Eidolon will be around shortly to answer",
            #"Go ask someone who gives a damn",
            "Purple hatstand fur elysian triumverate",
            "Of course not, don't be silly",
            #"Ask eliza",
            #"Supplicate and see",
            "Not in this universe. Try another",
            #"As soon as downtime is open",
            #"Supplicate and see what happens",
            "Pray and see what happens",
            "Not this time",
            "Only once",
            "yes, but bricks will fall after",
            "Pah, do not bother me with such trifles",
            #"A suffusion of yellow",
            #"Ask your mother",
            #"Go ask your father",
            #"Go play in the traffic",
            "Go play with a triffid",
            "Why ask questions you know the answer to?",
            "I'm going to say yes, but only because the results will be funnier",
            "That would be a 'No'",
            "No",
            "Yes, but only if you put chocolate sprinkles on it"

        )

        # return answers[(random.randint(0,len(answers)))]
        return random.choice(answers)
