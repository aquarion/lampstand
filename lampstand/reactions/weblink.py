import re
import time
import os
import lampstand.reactions.base
from lampstand import tools
import bitly_api
import urlparse
import sys
import logging

from lampstand.titlefetcher import *


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):
    __name = 'Weblink'

    youtube = False

    def __init__(self, connection):
        self.logger = logging.getLogger(self.__name)
        self.channelMatch = [
            re.compile(
                '%s: Shorten that( URL)?' %
                connection.nickname,
                re.IGNORECASE),
            # 0
            re.compile(
                '%s: Shorten (.*?)\'s? (link|url)' %
                connection.nickname,
                re.IGNORECASE),
            # 1
            re.compile(
                '%s: Shorten this (link|url): (.*)$' %
                connection.nickname,
                re.IGNORECASE),
            # 2
            re.compile('.*https?\:\/\/', re.IGNORECASE)]  # 3
        self.dbconnection = connection.dbconnection
        self.bitly = bitly_api.Connection(
            connection.config.get(
                "bitly", "username"), connection.config.get(
                "bitly", "apikey"))

        self.lastlink = {}

        self.connection = connection

        self.tf_twitter = False
        self.tf_youtube = False

        reload(sys.modules['lampstand.titlefetcher'])

    def channelAction(self, connection, user, channel, message, matchindex):

        self.logger.info("[WEBLINK] Activated, matchindex is %d" % matchindex)

        if matchindex == 3:  # Weblink
            self.logger.info(
                "[WEBLINK] That looks like a weblink : %s" % message)

            links = self.grabUrls(message)

            self.logger.info(links)
            now = time.time()

            for url in links:
                title = self.getTitle(url)

                if(title):
                    connection.message(channel, "[ %s ]" % title)

                cursor = self.dbconnection.cursor()
                cursor.execute(
                    'insert into urllist (time, username, message, channel, url, title) values (%s, %s, %s, %s, %s, %s)',
                    (now,
                     user,
                     message,
                     channel,
                     url,
                     title))

            self.lastlink[channel] = {'id': cursor.lastrowid, 'url': links[0]}

            self.dbconnection.commit()

        elif matchindex == 0:  # Shorten That
            self.logger.info("[WEBLINK] Shortening URL")

            self.logger.info(self.lastlink)
            surl = self.bitly.shorten(self.lastlink[channel]['url'])

            url_split = urlparse.urlparse(self.lastlink[channel]['url'])
            output = "%s: %s link shortened to %s" % (
                user, url_split[1], surl['url'])
            connection.message(channel, output)

            cursor = self.dbconnection.cursor()
            cursor.execute(
                'update urllist set shorturl = %s where id = %s',
                (surl['url'],
                 self.lastlink[channel]['id']))
            self.dbconnection.commit()

        elif matchindex == 1:  # SHorten user's url
            for module in connection.channelModules:
                if module.__name == "Memory":
                    memory = module

            matches = self.channelMatch[matchindex].findall(message)[0]
            self.logger.info(matches)
            result = memory.search(channel, matches[0], "http")
            self.logger.info(result)

            if len(result) == 0:
                output = "%s: I've no idea which link you mean" % user
                connection.message(channel, output)
            else:
                links = self.grabUrls(result[-1]['message'])

                for link in links:
                    surl = self.bitly.shorten(link)
                    url_split = urlparse.urlparse(link)
                    output = "%s: %s link shortened to %s" % (
                        user, url_split[1], surl['url'])
                    connection.message(channel, output.encode("utf-8"))

        elif matchindex == 2:  # Shorten this URL
            self.logger.info(
                "[WEBLINK] Shortening requested URL : %s" % message)
            links = self.grabUrls(message)

            if len(links) == 0:
                self.logger.info("[WEBLINK] No links found")
                connection.message(
                    channel,
                    "%s: I see no links in that" %
                    user)
                return

            self.logger.info(links)

            cursor = self.dbconnection.cursor()
            for link in links:
                self.logger.info(link)
                now = time.time()
                surl = self.bitly.shorten(link)
                cursor.execute(
                    'insert into urllist (time, username, message, channel, shorturl) values (%s, %s, %s, %s, %s)',
                    (now,
                     user,
                     message,
                     channel,
                     surl['url']))
                url_split = urlparse.urlparse(link)
                output = "%s: %s link shortened to %s" % (
                    user, url_split[1], surl['url'])
                connection.message(channel, output)

    def grabUrls(self, text):
        """Given a text string, returns all the urls we can find in it."""

        urls = '(?: %s)' % '|'.join(
            """http https telnet gopher file wais ftp""".split())
        ltrs = r'\w'
        gunk = r'/#~:.?+=&%@!\-'
        punc = r'.:?\-,\''
        any = "%(ltrs)s%(gunk)s%(punc)s" % {'ltrs': ltrs,
                                            'gunk': gunk,
                                            'punc': punc}

        url = r"""
            \b                            # start at word boundary
        	%(urls)s    :             # need resource and a colon
        	[%(any)s]  +?             # followed by one or more
                          #  of any valid character, but
                          #  be conservative and take only
                          #  what you need to....
            (?=                           # look-ahead non-consumptive assertion
        	    [%(punc)s]*           # either 0 or more punctuation
        	    (?:   [^%(any)s]      #  followed by a non-url char
                |                 #   or end of the string
                  $
        	    )
            )
            """ % {'urls' : urls,
                   'any': any,
                   'punc': punc}

        url_re = re.compile(url, re.VERBOSE | re.MULTILINE)

        return url_re.findall(text)

    def getTitle(self, url):
        title = False

        urlp = urlparse.urlparse(url)
        self.logger.info(url)

        if "twitter" in urlp.netloc.split("."):
            self.logger.info("That's a Twitter Link")

            if not self.tf_twitter:
                self.tf_twitter = TwitterTitleFetcher(self.connection)

            title = self.tf_twitter.fetch_title(url)

        elif "youtube" in urlp.netloc.split("."):
            self.logger.info("That's a Youtube Link")

            if not self.tf_youtube:
                self.tf_youtube = YoutubeTitleFetcher(self.connection)

            title = self.tf_youtube.fetch_title(url)

        else:
            titler = TitleFetcher(self.connection)
            title = titler.fetch_title(url)

        return title.strip()
