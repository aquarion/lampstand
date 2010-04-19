#!/usr/bin/python

import urllib
import sys

def strip_html_tags(it):
 	left = it[:(len(it)/2)]
 	right = it[(len(it)/2):]
 	final = left[left.rfind('>')+1:] + right[:right.find('<')]
 	return final

def send(text, number = '447909547990'):

	username = "aquarion"
	password = "[INSERT PASSWORD]"

	message = urllib.quote(text)
	url = "http://www.bulksms.co.uk:5567/eapi/submission/send_sms/1/current?username=%s&password=%s&message=%s&msisdn=%s&msg_class=2" % (username, password, message, number)
	fp = urllib.urlopen(url)
	response = fp.read(1024)
	fp.close()
	
	logp = open('/tmp/smsthis.txt', 'a')
	logp.write('Response: %s Message %s' % (response, message))
	logp.close()
