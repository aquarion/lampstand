import re, time
import lampstand.reactions.base

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Weblink'

	def __init__(self, connection):
		self.channelMatch = re.compile('.*https?\:\/\/')
		self.dbconnection = connection.dbconnection

	def channelAction(self, connection, user, channel, message):
		print "[WEBLINK] That looks like a weblink : %s" % message

		cursor = self.dbconnection.cursor()
		cursor.execute('insert into urllist (time, username, message) values (%s, %s, %s)', (time.time(), user, message) )
		self.dbconnection.commit()
