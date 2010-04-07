from lampstand.tools import splitAt
import lampstand.reactions.base
from lampstand import tools
import os.path
import re, time

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Quote This'

	admin = ("aquarion")

	cooldown_number   = 5
	cooldown_time     = 120
	uses              = []
	
	
	def __init__(self, connection):
		self.channelMatch = (re.compile('%s: quote (.*?) (.*)\s*$' % connection.nickname, re.IGNORECASE),
					re.compile('%s: quote (.*?)$' % connection.nickname, re.IGNORECASE))
		self.dbconnection = connection.dbconnection

	def channelAction(self, connection, user, channel, message, matchIndex = False):
		
		print 'Looking at <<%s>>' % message


                #if self.overUsed(self.uses):
                #        connection.msg(channel, self.overuseReactions[matchIndex])
                #        return True


                ## Overuse Detectection ##
                #self.uses.append(int(time.time()))
                #if len(self.uses) > self.cooldown_number:
                #        self.uses = self.uses[0:self.cooldown_number-1]
                ## Overuse Detectection ##

		matches = self.channelMatch[matchIndex].findall(message)[0]

		
		memory = False

		for module in connection.channelModules:
			if module.__name == "Memory":
				memory = module;
		


		memory.dump(connection, user, False, False)

		if matchIndex == 1:
			result = memory.search(channel, matches);
			quotedUser = matches
		elif matchIndex == 0:	
			result = memory.search(channel, matches[0], matches[1]);
			quotedUser = matches[0]

		if quotedUser.lower() == user.lower():
			connection.msg(channel, "%s: Don't do that, you'll go blind" % user);
			return


		if len(result) == 0:
			connection.msg(channel, "%s: Sorry, I've no idea what you're talking about" % user)
			return False
		else:
			print result
			line = result[-1]
			connection.msg(channel, "%s: Okay, quoting \"%s: %s\"" % (user, line['user'], line['message']))
			# Full Texts  	id 	body 	notes 	rating 	votes 	submitted 	approved 	flagged 	score
			quote = "%s: %s" % (line['user'], line['message'])
			sub = "Submitted by %s" % user
			
	                cursor = self.dbconnection.cursor()
	                cursor.execute('insert into chirpy.mf_quotes values (0, %s, %s, 0, 0, NOW(), 0, 0, 0)', (quote, sub) )
	                self.dbconnection.commit()
	
		return True
