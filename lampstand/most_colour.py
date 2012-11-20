## This was adapted from various StackOverflow scripts 
import ColorDB

import struct
import Image
import scipy
import scipy.misc
import scipy.cluster

import sys

def most_colour(filename):
	colordb = ColorDB.get_colordb('rgb.txt')
	#r, g, b = (255, 251, 250)
	#nearest = colordb.nearest(r, g, b)

	NUM_CLUSTERS = 30

	print 'reading image'
	im = Image.open(filename)
	im = im.resize((50, 50))      # optional, to reduce time
	ar = scipy.misc.fromimage(im)
	shape = ar.shape
	ar = ar.reshape(scipy.product(shape[:2]), shape[2])

	print 'finding clusters'
	codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
	print 'cluster centres:\n', codes

	vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
	counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences

	index_max = scipy.argmax(counts)                    # find most frequent
	peak = codes[index_max]
	colour = ''.join(chr(c) for c in peak).encode('hex')
	print 'most frequent is %s (#%s)' % (peak, colour)
	
	return colordb.nearest(peak[0],peak[1],peak[2])

if __name__ == '__main__':
	most_colour(sys.argv[1])
