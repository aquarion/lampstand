import re
import lampstand.reactions.base

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Nickserv'

	def __init__(self, connection):
		self.privateMatch = (re.compile('This nickname is registered and protected(.*)', re.IGNORECASE),re.compile('Ghost with your nickname has been killed', re.IGNORECASE))



	def privateAction(self, connection, user, channel, message, matchindex = 0):
		if matchindex == 0:

			if user == 'NickServ':
				if connection.chanserv_password != False:
					print '[IDENTIFY] Identifying myself to %s ' % user
					response = "Identify %s" % connection.chanserv_password.encode('ascii')
					connection.msg('NickServ', response )
					print response
				else:
					print '[IDENTIFY] Couldn\'t Identify myself to %s, no password ' % user
			else:
				print '[IDENTIFY] I think %s is trying to scam my password'	% user
		elif matchindex == 1:
			connection.register(connection.original_nickname);

