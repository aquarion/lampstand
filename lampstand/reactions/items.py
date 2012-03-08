from lampstand.tools import splitAt
import re, time, random, sys, datetime
import lampstand.reactions.base
from lampstand import tools
import cPickle  as pickle
import os.path

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Items & Inventory'

	admin = ("aquarion")

	cooldown_number   = 5
	cooldown_time     = 300
	uses              = []
	
	items = []
	defaultItems = ["a lantern", "a baseball bat"]
	inventorysize = 10
	
	def __init__(self, connection):
		self.channelMatch = (
			re.compile('(%s: take|gives %s) ([\w\s\d\'\-\(\),]*?\S)\s*\.?$' % (connection.nickname, connection.nickname), re.IGNORECASE), #0
			re.compile('%s. inventory' % connection.nickname, re.IGNORECASE), #1
			re.compile('%s. (attack|smite) (\S*)' % connection.nickname, re.IGNORECASE), #2
			re.compile('%s. do science\!?' % connection.nickname, re.IGNORECASE), #3
			re.compile('%s. drop (.*).?' % connection.nickname, re.IGNORECASE), #4
			re.compile('%s. (mis|)quote ben(|jamin) franklin' % connection.nickname, re.IGNORECASE), #5
			re.compile('%s. what have I forgotten(| to pack)\??' % connection.nickname, re.IGNORECASE), #6
			re.compile('%s. what has (\w*) forgotten(| to pack)\??' % connection.nickname, re.IGNORECASE), #7
			re.compile('%s. are you pondering what I\'m pondering\?' % connection.nickname, re.IGNORECASE), #8
			re.compile('%s. examine (.*?)\W*$' % connection.nickname, re.IGNORECASE), #9
			re.compile("(gives) ([\w\s\d\'\-\(\)]*?\S) to %s\.?" % connection.nickname, re.IGNORECASE) #10
			)
		self.dbconnection = connection.dbconnection

		self.overuseReactions = ("I am not a bag of holding, leave me alone.",
			"Stuff. Go away.",
			"No. Get some men at arms.",
			"Do your own weird experiments",
			"But it's *mine*",
			"He that falls in love with himself will have no rivals.",
			"The kitchen sink. Leave me alone.",
			"The kitchen sink. Leave me alone.",
			"No. LEAVE ME ALONE.",
			"It looks like one of those things that it is. GO AWAY.",
			"I am not a bag of holding, leave me alone.")
		
		
		self.load()
			
	def save(self):
		print "[ITEMS] Saving database..."
		output = open("inventory.pkl.db", 'wb')
		pickle.dump(self.items, output)
		output.close()
		
	def load(self):
		print "[ITEMS] Loading database..."
		try:
			input = open("inventory.pkl.db", 'rb')
			self.items = pickle.load(input)
			input.close()
		except:
			self.items = self.defaultItems

	def drop(self, item):
		if item.lower() in map(str.lower, self.items):
			i = map(str.lower, self.items).index(item.lower())
			print "Dropped %s" % self.items[i]
			del self.items[i]
			return True
		else:
			return False


	def channelAction(self, connection, user, channel, message, matchIndex = False):
		
		print 'Looking at <<%s>>' % message


                if self.overUsed(self.uses):
                        connection.msg(channel, self.overuseReactions[matchIndex])
                        return True


                ## Overuse Detectection ##
                self.uses.append(int(time.time()))
                if len(self.uses) > self.cooldown_number:
                        self.uses = self.uses[0:self.cooldown_number-1]
                ## Overuse Detectection ##


		if (matchIndex == 0 or matchIndex == 10):

			if (channel == "#lampstand" and user.lower() != "aquarion"):
				print "Not allowing %s on %s to do that" % (user, channel)
				connection.msg(channel, "%s: You can't give me things on #lampstand" % user)
				return
				

			item = self.channelMatch[matchIndex].findall(message)[0][1];

			if item.lower() == "a hug":
				hug = lampstand.reactions.hug.Reaction(connection);
				connection.me(channel, hug.hug(user))
				return

			if item.lower() == "a botsnack":
				connection.msg(channel, "Nom")
				return 

			if item.lower() == "a suspicious package" or item.lower() == "the suspicious package":
				connection.msg(channel, "Aha. Ah ha ha ha. Ah ha ha *ha* ha ha ha ha. ... No.")
				return

			if item.lower() in map(str.lower, connection.people):
				connection.msg(channel, "I'm not a fucking transit system, either.")
				return
				
			if item in map(str.lower, self.items):
				connection.msg(channel, "I already have one, thanks")
				return
			
			if len(self.items) >= self.inventorysize:
				drop = "a lantern"
				while drop == "a lantern":
					drop = random.choice(self.items)
				#drop = random.choice(self.items)
				dropi = self.items.index(drop);
				## Drop the lantern over my cold, dead, grue bitten corpse
				#if self.items[dropi] == "a lantern":
				#	dropi += 1
				#	if dropi > (len(self.items)-1):
				#		dropi = dropi - 2
				del self.items[dropi]
				self.items.append(item)
				result = "gives %s %s in return for %s" % (user, drop, item)
			else:
				result = "takes \"%s\"" % item;
				self.items.append(item)
			
			
			cursor = self.dbconnection.cursor()
			cursor.execute('insert into item (item, author) values (%s, %s)', (item, user) )
			self.dbconnection.commit()
			self.save()
			connection.me(channel, result.encode('utf8'))
			#connection.notice(channel, "I have %d items" % self.items.count(True))
		elif (matchIndex == 1):
			
			print self.items;
			
			if len(self.items) == 0:
				connection.msg(channel, "I have nothing.")
				return True
			elif len(self.items) == 1:
				connection.msg(channel, "I currently have %s" % self.items[0])
				return True
				
			last = self.items[-1:][0]

			if ("," in "".join(self.items)):
				seperator = "; "
			else:
				seperator = ", "
			
			message = seperator.join(self.items[:-1]);
			
			connection.msg(channel, "I currently have %s%sand %s" % (message, seperator, last))
		elif (matchIndex == 2): # attack

			person = self.channelMatch[2].findall(message)[0][1];
			
			print "Searching %s for <<%s>>" % (connection.people, person)
			print "for %s" % person;
			
			
			if person.lower() == 'me':
				person = user
	
			if person.lower() == 'glados':
				print "Kicking %s for taking the name of my lady in vain" % user
				connection.kick(channel, user, 'Taking the name of my lady in vain')
				return
	
			if person.lower() == connection.nickname.lower():
				connection.msg(channel, "%s: No." % user )
				return
	
			if person.lower() == 'aquarion':
				connection.msg(channel, "%s: Do I look suicidal? No." % user )
				return
	
			if person.lower() == 'hal':
				connection.msg(channel, "%s: With great pleasure" % user )
				return

			if person.lower() == 'someone':
				person = random.choice(connection.people);

			elif not person in connection.people:
				connection.msg(channel, "%s: Not going to attack someone I can't see." % user)
				return
			
			
			if len(self.items) == 0:
				connection.msg(channel, "%s: With what, dear liza? I have nothing to attack them with." % user)
				return True
			
			item = random.choice(self.items)

			attacks = ("smites", "beats", "wallops", "gently taps", "murderises", "waps")
			attack = random.choice(attacks)

			bodypart = ("head", "body", "arms", "legs", "soul", "brain", "elbow")
			
			part = random.choice(bodypart)
			
			connection.me(channel, "%s %s around the %s with %s" % (attack, person, part, item))
			
			return True
			
		elif (matchIndex == 3): # science
			
			actions = ("reverses", "enhances", "cross-references", "standardizes", "capitalises", "extends", "embiggens", "ensmallificates", "transmogrifies", "deliquesces", "discombobulates", "reticulates")
			
			attributes = ("neutron flow", "positrons", "third aspect", "cangrip", "buckelfier-subsystem", "pseudodancer", "electron river", "Danson", "neurotoxin flow", "contraits", "buckminster routine", "reverse cowgirl", "complexigon", "oxygen depriver", "elysia simulation routine", "splines")
			
			# Lampstand $actions the $attribute on $item and $actions $item to create $hugresponse

			if len(self.items) <= 2:
				connection.msg(channel, "I don't have enough things on which to do SCIENCE!")
				return			

			item = random.choice(self.items)
			item2 = item
			while item2 == item:
				item2 = random.choice(self.items)

			action = random.choice(actions)
			action2 = action
			while action2 == action:
				action2 = random.choice(actions)
			
			attribute = random.choice(attributes)
			
			cursor = self.dbconnection.cursor()
			cursor.execute('SELECT item from hugReaction order by rand() limit 1')
			result = cursor.fetchone()
			
			hugresponse = result[0]
			
			connection.me(channel, "%s the %s on %s and %s %s to create %s" % (action, attribute, item, action2, item2, hugresponse))
			
			#if len(self.items) >= self.inventorysize:
			#	drop = random.choice(self.items)
			#	dropi = self.items.index(drop);
			#	del self.items[dropi]
			#	result = "Dropped \"%s\" in order to take \"%s\"" % (drop, hugresponse)
			
			self.drop(item)
			self.drop(item2)
			self.items.append(hugresponse)

			creator = "%s's science experiment" % user
			cursor = self.dbconnection.cursor()
			cursor.execute('insert into item (item, author) values (%s, %s)', (hugresponse, creator) )
			self.dbconnection.commit()
			self.save()
		
		elif (matchIndex == 4): # drop
			item = self.channelMatch[4].findall(message)[0];
			
			if (channel == "#lampstand" and not user.lower() in self.admin):
				print "Not allowing %s on %s to do that" % (user, channel)
				connection.msg(channel, "%s: Shan't, and you can't make me. :-P " % user)
				return

			if item.lower() == "everything":
				if user.lower() in self.admin:
					connection.me(channel, 'drops everything except the lantern, then manifests a baseball bat and dashes all the items to their component atoms')
					self.items = self.defaultItems
					self.save()
				else:
					connection.msg(channel, "I don't have to listen to you. So neh.")
			elif item.lower() == "a lantern":
				connection.msg(channel, '%s: Nuh-uh. This is grue country.' % user)
				return;
			elif item.lower() in map(str.lower, self.items):
				result = self.drop(item)
				if result:
					connection.msg(channel, '%s: Dropped "%s"' % (user, item))
				
				self.save()
				
			else:
				connection.msg(channel, '%s: I don\'t have one.' % user)
				print item
				print map(str.lower, self.items)

		elif (matchIndex == 5): # franklin
                        cursor = self.dbconnection.cursor()
                        cursor.execute('select item from item ORDER BY RAND() limit 2');
			itemone = cursor.fetchone()[0];
			itemtwo = cursor.fetchone()[0];

			connection.msg(channel, "They who can give up %s to obtain %s, deserve neither %s or %s" % (itemone, itemtwo, itemone, itemtwo))
			return 1
		elif (matchIndex == 6): # Packing
                        cursor = self.dbconnection.cursor()
                        cursor.execute('select item from item ORDER BY RAND() limit 1');
			itemone = cursor.fetchone()[0];

			connection.msg(channel, "%s: You have forgotten %s" % (user, itemone))
			return 1
		elif (matchIndex == 7): # Packing
			person = self.channelMatch[7].findall(message)[0][0];
                        cursor = self.dbconnection.cursor()
                        cursor.execute('select item from item ORDER BY RAND() limit 1');
			itemone = cursor.fetchone()[0];

			connection.msg(channel, "%s: %s has forgotten %s" % (user, person, itemone))
			return 1
				
		elif (matchIndex ==8 ): #Pinky
			cursor = self.dbconnection.cursor()
			cursor.execute('select item from item ORDER BY RAND() limit 5');
			itemone = cursor.fetchone()[0];
			itemtwo = cursor.fetchone()[0];
			itemthree = cursor.fetchone()[0];

			person = user

			while person == user or person == connection.nickname:
				person = random.choice(connection.people);

			#Good gravy I hope not.
			#Yes
			#No.

			out = "I think so %s, but " % user

			options = ("We'll never find %s at this hour" % itemone,
				"I'm pretty sure you can't combine %s and %s safely" % (itemone, itemtwo),
				"I don't think you could make out with %s realistically" % person,
				"I don't think you could mold a %s to look like %s" % (itemone, person),
				"I don't think pants made out of %s would work" % itemone,
				"you and %s? What would the children look like?" % person,
				"I'm pretty sure %s won't like it" % person,
				"nothing good ever comes of eating %s" % itemone,
				"%s isn't very good rocket fuel" % itemone,
				"first you'd have to insert %s, and that sounds painful" % itemone,
				"\"apply %s\" to what?" % itemone,
				"snort* no, no, it's too stupid!",
				"why would %s do a musical?" % person,
				"what if %s won't wear %s?" % (person, itemone),
				"isn't that why they invented %s?" % itemone,
				"if Jimmy cracks corn, and no one cares, why does he keep doing it?",
				"are you sure we can trust %s?" % person,
				"%s is not a valid pie filling" % itemone,
				"we'll never know."
				"... *poit* ... were we saying something?"
			)

			
			

			connection.msg(channel, out + random.choice(options) )
			return 1

		elif (matchIndex == 9): # examine
	                cursor = self.dbconnection.cursor()
			item = self.channelMatch[9].findall(message)[0];
			
			if item == "a lantern":
				connection.msg(channel, '%s: It is a battery powered brass lantern' % user)
			elif item.lower() == user.lower():
				connection.msg(channel, '%s: I see a meatsack with a propensity for stupid questions' % user)
			elif item.lower() == connection.nickname.lower():
				connection.msg(channel, '%s: I am he as you are he as you are me and we are all together.' % user)
			elif item in self.items:
				define = lampstand.reactions.whatis.Reaction(connection);
				definition = define.define(item)

				cursor.execute('select item, date_created, author from item where item = %s ORDER BY date_created desc limit 1', item);
	                        itemone = cursor.fetchone();

				if definition:
					connection.msg(channel, '%s: %s is %s. It was given to me by %s on %s.' % (user, itemone[0], definition[1], itemone[2], itemone[1]))
				else:
					connection.msg(channel, '%s: %s was given to me by %s on %s.' % (user, itemone[0], itemone[2], itemone[1]))
				return True

			elif item in connection.people:
				connection.msg(channel, '%s: look at them yourself, meatsack' % user)
					
				
			else:
				connection.msg(channel, '%s: I don\'t have one.' % user)

