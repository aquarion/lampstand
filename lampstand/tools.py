
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

def Denary2Binary(n):
    '''convert denary integer n to binary string bStr'''
    bStr = ''

    n = int(n)

    if n < 0:  raise ValueError, "must be a positive integer"
    if n == 0: return '0'
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    return bStr
 
def int_to_roman(input):
   """
   Convert an integer to Roman numerals.

   Examples:
   >>> int_to_roman(0)
   Traceback (most recent call last):
   ValueError: Argument must be between 1 and 3999

   >>> int_to_roman(-1)
   Traceback (most recent call last):
   ValueError: Argument must be between 1 and 3999

   >>> int_to_roman(1.5)
   Traceback (most recent call last):
   TypeError: expected integer, got <type 'float'>

   >>> for i in range(1, 21): print int_to_roman(i)
   ...
   I
   II
   III
   IV
   V
   VI
   VII
   VIII
   IX
   X
   XI
   XII
   XIII
   XIV
   XV
   XVI
   XVII
   XVIII
   XIX
   XX
   >>> print int_to_roman(2000)
   MM
   >>> print int_to_roman(1999)
   MCMXCIX
   """
   if type(input) != type(1):
      raise TypeError, "expected integer, got %s" % type(input)
   if not 0 < input < 4000:
      raise ValueError, "Argument must be between 1 and 3999"   
   ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
   nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
   result = ""
   for i in range(len(ints)):
      count = int(input / ints[i])
      result += nums[i] * count
      input -= ints[i] * count
   return result

def int2bin(n, count=24):
    """returns the binary of integer n, using count number of digits"""
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])

def convertNiceTime(number,format):
	if format == "decimal" or format == "dec":
		return int(number);

	if format == "binary" or format == "bin":
		return Denary2Binary(number);

	if format == "hex" or format == "hexadecimal":
		print "Converting %s to hex" % number
		return hex(int(number))
	

	if format == "oct" or format == "octal":
		print "Converting %s to oct" % number
		return oct(int(number))
	
	if format == "roman" or format == "roman":
		print "Converting %s to roman" % number
		return int_to_roman(int(number))

	return False;

def niceTimeDelta(timedelta, format="decimal"):

		years = int(timedelta / (60*60*24*365));
		remainder = timedelta % (60*60*24*365);
		days = int(remainder / (60*60*24));
		remainder = timedelta % (60*60*24);
		hours = remainder / (60*60)
		remainder = timedelta % (60*60);
		minutes = remainder / 60


		if int(years) == 1:
			years_message = "1 year, "
		elif years > 1:
			years_message = "%s years, " % convertNiceTime(years, format)
		else:
			years_message = ''

		if (days < 7 and years == 0):
			hours = hours + (24*days)
			days = 0;
		
		#if (hours < 48 and years == 0 and days < 3):
		#	minutes = minutes + (60*hours)
		#	hours = 0;

		if int(days) == 1:
			days_message = "1 day, "
		elif days > 1:
			days_message = "%s days, " % convertNiceTime(days,format)
		else:
			days_message = ''

		if int(hours) == 1:
			hours_message = "1 hour, "
		elif hours > 1:
			hours_message = "%s hours, " % convertNiceTime(hours, format)
		else:
			hours_message = ''


		if int(minutes) == 1:
			minutes_message = "1 minute"
		elif minutes > 1:
			minutes_message = "%s minutes" % convertNiceTime(minutes, format)
		else:
			minutes_message = ''
			
		string = years_message+days_message+hours_message+minutes_message

		if string == "":
			return "seconds"
		else:
			return string
