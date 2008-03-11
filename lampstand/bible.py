import urllib

class ESVSession:
    def __init__(self, key = 'IP'):
        options = ['include-short-copyright=0',
                   'output-format=plain-text',
                   'include-passage-horizontal-lines=0',
                   'include-heading-horizontal-lines=0']
        self.options = '&'.join(options)
        self.baseUrl = 'http://www.esvapi.org/v2/rest/passageQuery?key=%s' % (key)

    def doPassageQuery(self, passage):
        passage = passage.split()
        passage = '+'.join(passage)
        url = self.baseUrl + '&passage=%s&%s' % (passage, self.options)
	print '[Bible] %s' % url
        page = urllib.urlopen(url)
        return page.read()


#bible = ESVSession(key)

#passage = raw_input('Enter Passage: ')
#while passage != 'quit':
#    print bible.doPassageQuery(passage)
#    passage = raw_input('Enter Passage: ')
