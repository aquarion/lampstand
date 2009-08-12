
import time,re

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
		
def niceTimeDelta(timedelta):

		days = int(timedelta / (60*60*24));
		remainder = timedelta % (60*60*24);
		hours = remainder / (60*60)
		remainder = timedelta % (60*60);
		minutes = remainder / 60

		if (days < 5):
			hours = hours + (24*days)
			days = 0;

		if int(days) == 1:
			days_message = "1 day, "
		elif days > 1:
			days_message = "%d days, " % days
		else:
			days_message = ''

		if int(hours) == 1:
			hours_message = "1 hour, "
		elif hours > 1:
			hours_message = "%d hours, " % hours
		else:
			hours_message = ''


		if int(minutes) == 1:
			minutes_message = "1 minute"
		elif minutes > 1:
			minutes_message = "%d minutes" % minutes
		else:
			minutes_message = ''
			
		return days_message+hours_message+minutes_message
