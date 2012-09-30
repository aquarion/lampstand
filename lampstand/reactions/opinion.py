import re, time, random
import lampstand.reactions.base

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Opinion'

	def __init__(self, connection):
		self.channelMatch = (re.compile('(.*?)(\S*)(\+\+|--)\s*$'),
			re.compile('%s.? what do you think of (.*?)\??' % connection.nickname, re.IGNORECASE))
		self.privateMatch = re.compile('what do you think of (.*?)\??', re.IGNORECASE)
		self.dbconnection = connection.dbconnection
	

	def channelAction(self, connection, user, channel, message, matchIndex = False):
		return False
		print 'Looking at <<%s>>' % message
		if (matchIndex == 0):
			matchResult = self.channelMatch[0].findall(message);
			channel, self.vote(matchResult, user, message);
		if (matchIndex == 1):
			matchRegex = re.compile('%s.? what do you think of (.*?)\??$' % connection.nickname, re.IGNORECASE)
			matchResult = matchRegex.findall(message);
			print 'match at <<%s>>' % matchResult

			reactions = {'your mum': 'She was a saint. And a toaster', 'glados':'*happy sigh*', 'hal':'Oh my god! It\'s full of FUCKWITTERY' }
			if (reactions.has_key(matchResult[0].lower())):
				connection.message(channel, reactions[matchResult[0].lower()])
			else:
				connection.message(channel, self.opinion(matchResult[0], connection).encode('utf8'))
			return True

        def privateAction(self, connection, user, channel, message):

                match = self.privateMatch.findall(message);
		print "Private Match";
		print match
                connection.message(self.opinion(match[0], connection).encode('ascii'), user)


	def vote(self, match, user, fullmessage = ''):
		match=match[0]

		if len(match[1]) < 3:
			print '[OPINION] Not recording vote for %s' % match[1]
			return;


		if match[2] == '--':
			vote = -1
		else:
			vote = +1

		cursor = self.dbconnection.cursor()
		#CREATE TABLE vote (id INTEGER PRIMARY KEY, username varchar(64), item varchar(64), vote tinyint);

		cursor.execute('insert into vote (time, username, item, vote, textline) values (%d, %s, %s, %s, %s)', (time.time(), user, match[1], vote, fullmessage) )

		print '[OPINION] A vote for %s' % match[1]

		#return match;

	def opinion(self, item, connection):
		print '[OPINION] A query on %s' % item

		if item.lower() == connection.nickname.lower():
			return "Obviously, I'm awesome"

		cursor = self.dbconnection.cursor()
		cursor.execute(u'select item, sum(vote) as total, count(*) as votors from vote where item LIKE %s group by item', (item,) )
		result = cursor.fetchone()



		print result
		if not result or result[0] == None:
			return 'I have no opinions on that';

		OpinionOptions = [];

		print result[1]
		rating = int(result[1])
		
		cursor.execute(u'select item, sum(vote) as total, count(*) as votors from vote group by item having sum(vote) > %s limit 3', (rating,) )

		rows = cursor.fetchall();
		print rows;
		#print "Better: %s " % rows;
		OpinionOptions.extend(rows);


		cursor.execute('select item, sum(vote) as total, count(*) as votors from vote group by item having sum(vote) < %s limit 3', rating )

		rows = cursor.fetchall();
		#print "Worse: %s " % rows;
		OpinionOptions.extend(rows);

		Choice = random.choice(OpinionOptions);

		if Choice[1] > rating:
			return "Not as good as %s" % Choice[0];
		else:
			return "Better than %s" % Choice[0];

		print result
		print OpinionOptions

