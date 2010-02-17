from twisted.internet import reactor
import re, time, random, sys
import lampstand.reactions.base

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Admin'

	canSay = ("Aquarion")
	
	def __init__(self, connection):
		self.privateMatch = (
			re.compile('say (.*)', re.IGNORECASE),
			re.compile('do (.*)', re.IGNORECASE),
			re.compile('quit (.*)', re.IGNORECASE),
			re.compile('status', re.IGNORECASE),
			re.compile('reload (.*)', re.IGNORECASE),
			re.compile('kick (\w*) (.*)', re.IGNORECASE),
			re.compile('join (\w*)', re.IGNORECASE),
			re.compile('leave (\w*)', re.IGNORECASE))


	def privateAction(self, connection, user, channel, message, matchindex = 0):
		print "[Admin] called"

		if user not in self.canSay:
			return

		matches = self.privateMatch[matchindex].findall(message)

		if matchindex == 0:
			print "[Say] %s %s" % (sys.argv[1], matches[0])
			connection.msg("#%s" % sys.argv[1], matches[0])
		elif matchindex == 1:
			print "[Do] %s %s" % (sys.argv[1], matches[0])
			connection.me("#%s" % sys.argv[1], matches[0])
		elif matchindex == 2:
			print "[Quit] %s %s" % (sys.argv[1], matches[0])
			connection.quit(matches[0])
			reactor.stop()
		elif matchindex == 3: # status
			connection.msg(user, 'State of the union is awesome')
			connection.msg(user, 'Channel: %s' % connection.channelModules)
			connection.msg(user, 'Private: %s' % connection.privateModules)
			connection.msg(user, 'Nick Change: %s' % connection.nickChangeModules)
			connection.msg(user, 'Leave: %s' % connection.leaveModules)
			connection.msg(user, 'Join: %s' % connection.joinModules)
		elif matchindex == 4: # reload
			result = connection.installModule(matches[0]);
			connection.msg(user, result)
		elif matchindex == 5: # kick
			print matches
			print "Kicking %s from %s with the message %s" % (matches[0][0], channel, matches[0][1])
			connection.kick('#maelfroth', matches[0][0], matches[0][1])
		elif matchindex == 6: # join
			print matches
			print "Joining %s " % (matches[0])
			connection.join('#'+matches[0])
		elif matchindex == 7: # leave
			print matches
			print "Leaving %s " % (matches[0])
			connection.leave('#'+matches[0])
