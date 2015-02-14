from twisted.internet import reactor
import re
import time
import random
import sys
import lampstand.reactions.base


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):
    __name = 'Admin'

    canSay = ["Aquarion", "ccooke"]

    def __init__(self, connection):

        adminconf = connection.config.items("admin")
        if adminconf:
            canSay = []
            for admin in adminconf:
                canSay.append(admin[1])
            self.canSay = canSay
            print "Admins are: %s" % canSay

        self.privateMatch = (
            re.compile('say (\#\w*) (.*)', re.IGNORECASE),
            re.compile('do (\#\w*) (.*)', re.IGNORECASE),
            re.compile('quit (.*)', re.IGNORECASE),
            re.compile('status', re.IGNORECASE),
            re.compile('reload (.*)', re.IGNORECASE),
            re.compile('kick (\#\w*?) (.*?) (.*)', re.IGNORECASE),
            re.compile('join (\#\w*)', re.IGNORECASE),
            re.compile('leave (\#\w*)( .*)?', re.IGNORECASE),
            re.compile('unload (\w*)', re.IGNORECASE),
            re.compile('reconfigure', re.IGNORECASE),
            re.compile('sysreload (.*)', re.IGNORECASE),
            re.compile('nick (.*)', re.IGNORECASE),
            re.compile('ipdb', re.IGNORECASE))

    def privateAction(self, connection, user, channel, message, matchindex=0):
        print "[Admin] called"

        if user not in self.canSay:
            connection.message(user, "That's admin functionality, sorry")
            return

        matches = self.privateMatch[matchindex].findall(message)

        if matchindex == 0:
            print "[Say] %s %s" % (matches[0][0], matches[0][1])
            connection.message(matches[0][0], matches[0][1])
        elif matchindex == 1:
            # print "[Do] %s %s" % (sys.argv[1], matches[0])
            connection.describe(matches[0][0], matches[0][1])
            #connection.message(user, "%s" % matches)
            # connection.me("#%s" % sys.argv[1], matches[0])
        elif matchindex == 2:
            print "[Quit] %s" % (matches[0])
            connection.quit(
                "I don't believe you, I don't really need to, I won't let Victoria fall")
        elif matchindex == 3:  # status
            connection.message(user, 'State of the lampstand is awesome')
            connection.message(user, 'Channel: %s' % connection.channelModules)
            connection.message(user, 'Private: %s' % connection.privateModules)
            connection.message(
                user,
                'Nick Change: %s' %
                connection.nickChangeModules)
            connection.message(user, 'Leave: %s' % connection.leaveModules)
            connection.message(user, 'Join: %s' % connection.joinModules)
        elif matchindex == 4:  # reload
            result = connection.installModule(matches[0])
            connection.message(user, result)
        elif matchindex == 5:  # kick
            print matches
            matches = matches[0]
            print "Kicking %s from %s with the message %s" % (matches[0], channel, matches[0][1])
            connection.kick(matches[0], matches[1], matches[2])
        elif matchindex == 6:  # join
            print matches
            print "Joining %s " % (matches[0])
            connection.join(matches[0])
        elif matchindex == 7:  # leave
            print matches
            print "Leaving %s " % (matches[0][0],)
            if(matches[0][1]):
                connection.part(matches[0][0], matches[0][1])
            else:
                connection.part(matches[0][0])
        elif matchindex == 8:  # unload
            result = connection.removeModuleActions(matches[0])
            connection.message(user, result)
        elif matchindex == 9:  # reload config
            print "Reload Config"
            result = connection.loadConfig()
            for thingy in connection.config.items("modules"):
                connection.installModule(thingy[0])
            connection.message(user, "%s" % connection.config)
        elif matchindex == 10:  # sysreload
            module = matches[0]
            if (module in sys.modules):
                reload(sys.modules[module])
                rtn = 'Reloaded %s' % module
                connection.message(user, rtn)
            else:
                connection.message(user, "%s Not found" % matches[0])
        elif matchindex == 11:  # nick
            name = matches[0]
            print "Renaming to %s" % name
            connection.setNick(name)
        elif matchindex == 12:  # ipdb
            import ipdb
            ipdb.set_trace()

        return True
