
from lampstand.tools import splitAt
import re, time, random, sys, string
import lampstand.reactions.base

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Dice'


	cooldown_number = 5
	cooldown_time   = 120

	def __init__(self, connection):
		self.channelMatch = re.compile('%s. roll (\d*d\d*)(.*)' % connection.nickname, re.IGNORECASE)


	def channelAction(self, connection, user, channel, message):


		if self.overUsed():
			connection.msg(user, "The dice are too hot to touch. Give them a couple of minutes to cool down." )
			return
			
		item = self.channelMatch.findall(message);
		
		if random.randint(0,100) == 66:
			connection.msg(channel, "You rolled %s. You get Rick Astley.", item[0][0] )
			print "[ROLLING DICE] Rickroll!"
			return


		print "[ROLLING DICE] %s" % item
		try:
			result = self.roll(item[0][0]);
		except:
			connection.msg(channel, "The dice blew up." )
			return

		print "[ROLLING DICE] %s, got %s" % (item[0], result)


		if result == False:
			connection.msg(channel, "%s: I don't understand that format yet, sorry :(" % user )
			return

		display = result[0]
		total = 0
	 	for elem in result[0]:
	 		total = total + elem

		originaltotal = total

		message = "%s Total %s " % (display, total)

		print "Item: %s " % item

		if len(item[0]) > 1 and item[0][1] != '':
			modifier = ''.join(item[0][1].split(' '))
			print "Modifier is %s" % modifier
			print "Modifier is %s -- %s" % (modifier[0], modifier[1:])


			if modifier[0] == "+":
				total = total + string.atof(modifier[1:])
			if modifier[0] == "-":
				total = total - string.atof(modifier[1:])
			if modifier[0] == "*":
				total = total * string.atof(modifier[1:])
			if modifier[0] == "/":
				total = total / string.atof(modifier[1:])

			message = "%s %s = %d " % (display, modifier, total)


		self.updateOveruse()

	def roll(self, dice):
	   '''dice is a string of form idj, e.g. 2d6, and rolls i j-sided dice, and returns the result as an array'''
	   data = dice.split('d')
	   #data validation
	   if(len(data) != 2):
		  return False

	   try:
		  type = int(data[1])
		  if data[0] == '':
			 #defaults to 1
			 howmany=1
		  else:
			 howmany = int(data[0])
	   except:
		  return False

	   if(howmany > 32):
		  return False

	   if(howmany <1 or type <1): return False

	   results = [];
	   for i in range(0,howmany):
		  results.append(random.randrange(1, type+1))

	   #if die type is d6, replace results with Unicode die-face glyphs
	   if type == 6:
		origres = results
		results = []
		for res in origres:
			results.append(unichr(9855+res))
		return [origres, str(howmany)+'d'+str(type), results]
	   else:
		return [results, str(howmany)+'d'+str(type)]
