
import time

def splitAt(string, number):
	if len(string) > number:
		index = number
		whitespace =  re.compile('\s')
		while not whitespace.match(string[index]) and index != 0:
			#print "%d: %s" % (index, string[index])
			index = index -1

		return index
	else:
		return number

def overUsed(uses, number, cooldown):

		if len(uses) >= number:
			first_use = int(uses[0])
			use_allowed_again = first_use + cooldown
			if time.time() < use_allowed_again:
				print "Use Blocked. Try again in %s" % (int(use_allowed_again) - time.time());
				return True

		return False