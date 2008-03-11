import random

def roll(dice):
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
