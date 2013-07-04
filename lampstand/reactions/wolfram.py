import lampstand.reactions.base
import re, time, random, sys
import requests
import urllib
from lxml import etree


def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):

	__name = 'Wolfram'
	
	cooldown_number = 3
	cooldown_time   = 360 # So if 3 requests are made in 360 seconds, it will trigger overuse.
	uses = []

	def __init__(self, connection):
		self.channelMatch = re.compile('^%s. (Ask Wolfram|Calculate|Wolfram) (.*)' % connection.nickname, re.IGNORECASE)
		self.privateMatch = re.compile('^(Ask Wolfram|Calculate|Wolfram) (.*)', re.IGNORECASE)

		self.apikey = connection.config.get("wolfram","apikey")

	def channelAction(self, connection, user, channel, message, index=0):
		
		print "[Wolfram] Hello"
		
		matches = self.channelMatch.findall(message);
		
		if self.overUsed():
			connection.message(user, "Overuse Triggered" )
			return True

		connection.message(channel, "%s: %s" % (user, self.wolfram(matches[0][1])))
		
		return True


	def privateAction(self, connection, user, channel, message, index=0):
		print "[Wolfram] Hello privately"
		matches = self.privateMatch.findall(message);
		connection.message(user, self.wolfram(matches[0][1]))
		return True

		
	def wolfram(self, question):
		## Uses code from https://github.com/londonhackspace/irccat-commands
		
		query = question
		query = urllib.quote(query)

		response = requests.get('http://api.wolframalpha.com/v2/query?appid=%s&input=%s&format=plaintext' % (self.apikey, query))
		root = etree.fromstring(response.content)
		
		print response.content

		if root.xpath("/queryresult")[0].attrib['success'] == 'true':
			possible_questions = ('Input interpretation', 'Input')
			question = self.find_node(root, possible_questions)

			possible_answers = ('Current result', 'Response', 'Result', 'Results')
			answer = self.find_node(root, possible_answers)
			
			if answer == None:
				node = root.xpath("/queryresult/pod/subpod/plaintext")
				if node:
					print node
					return "(As %s): %s" % (node[0].text, node[1].text.replace('\n', ' // '))
				else:
					return "You're going to need to be more specific"

			return answer
		else:
			return "Sorry, Wolfram Alpha doesn't understand the question"
			

	def find_node(self,root, possible_attribs):
		for attr in possible_attribs:
			node = root.xpath("/queryresult/pod[@title='%s']/subpod/plaintext" % attr)
			if node:
				return node[0].text

		return None
			
	#def everyLine(self, connection, user, channel, message)
	#def leaveAction(self, connection, user, reason, parameters)
	#def nickChangeAction(self, connection, old_nick, new_nick)
	#def scheduleAction(self, connection)
