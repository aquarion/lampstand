

from googleapiclient.discovery import build
import isodate

from lampstand import tools

import os
from twitter import Twitter

from twitter.oauth import OAuth, write_token_file, read_token_file
from twitter.oauth_dance import oauth_dance

import requests
import BeautifulSoup

import Image

import logging
import urlparse
import StringIO


class TitleFetcher():

    def __init__(self, connection):
        self.logger = logging.getLogger(__name__)
        self.connection = connection
        self.localinit()

    def localinit(self):
        pass

    def fetch_title(self, url):
        headers = {
            'User-agent': 'Lampstand IRC Bot (contact aquarion@maelfroth.org)'}
        try:
            req = requests.get(url, headers=headers, timeout=30)
        except requests.exceptions.Timeout:
            return "That link timed out"
        except requests.exceptions.SSLError as e:
            return "Something's up with the security on %s. Tread carefully. (%s)" % (
                urlp.netloc, e)

        k = len(req.content) / 1024
        if req.status_code != 200:
            title = "That link returned an error %s" % (req.status_code)
        elif req.headers['content-type'].find("text/html") != -1 or req.headers['content-type'].find("application/xhtml+xml") != -1:
            soup = BeautifulSoup.BeautifulSoup(
                req.text,
                convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES)
            title = soup.title.string
        else:
            if req.headers['content-type'].find("image/") == 0:
                image_file = StringIO.StringIO(req.content)

                api_url = "http://api.imagga.com/v1/tagging"

                querystring = {"url": url, "version": "2"}

                auth_key = self.connection.config.get("imagga", "auth_key")

                headers = {
                    'accept': "application/json",
                    'authorization': "Basic %s==" % auth_key
                }

                response = requests.request(
                    "GET", api_url, headers=headers, params=querystring)

                prefix = "An %s - %dx%d (%dk)"

                print response.text

                if "results" in response.json():
                    tags = response.json()['results'][0]['tags']
                    first_tag = tags[0]
                    if first_tag['confidence'] > 60:
                        prefix = "An %%s of a %s %%dx%%d (%%dk)" % first_tag[
                            'tag']

                #color = most_colour.most_colour(image_file)

                print prefix

                image_file.seek(0)
                im = Image.open(image_file)
                try:
                    im.seek(1)
                    title = prefix % (
                        "animation", im.size[0], im.size[1], k)
                except:
                    title = prefix % (
                        "image", im.size[0], im.size[1], k)
            else:
                title = "A %s file (%dk)" % (
                    req.headers['content-type'], k)

        return title


class YoutubeTitleFetcher(TitleFetcher):
    youtube = False

    def localinit(self):
        GOOGLE_KEY = self.connection.config.get("google", "api_key")
        self.logger.info("Creating new youtube object")
        self.youtube = build('youtube', 'v3', developerKey=GOOGLE_KEY)

    def fetch_title(self, url):
        parsedurl = urlparse.urlparse(url)
        [yt_type, yt_id] = self.url_to_ID(parsedurl)

        if yt_type == 'video':

            item = self.youtube.videos().list(part="snippet,contentDetails", id=yt_id).execute()
            self.logger.info(item)

            video = item['items'][0]

            duration = isodate.parse_duration(
                video['contentDetails']['duration'])
            title = video['snippet']['title']
            description = video['snippet']['description']

            self.logger.info(title)
            deltastring = tools.niceTimeDelta(duration.total_seconds())
            #deltastring = entry.media.duration.seconds
            self.logger.info(title)
            return "Youtube video: %s (%s)" % (
                title, deltastring)
            # connection.message(channel,title)

    def url_to_ID(self, parsedurl):
        query = urlparse.parse_qs(parsedurl.query)
        if "v" in query.keys():
            self.logger.info(
                "That's a Youtube Link with a v! %s " % query['v'][0])
            return ['video', query['v'][0]]


class TwitterTitleFetcher(TitleFetcher):

    def localinit(self):
        OAUTH_FILENAME = self.connection.config.get("twitter", "oauth_cache")
        CONSUMER_KEY = self.connection.config.get("twitter", "consumer_key")
        CONSUMER_SECRET = self.connection.config.get(
            "twitter", "consumer_secret")

        try:
            if not os.path.exists(OAUTH_FILENAME):
                oauth_dance(
                    "Lampstand", CONSUMER_KEY, CONSUMER_SECRET,
                    OAUTH_FILENAME)

            self.oauth_token, self.oauth_token_secret = read_token_file(
                OAUTH_FILENAME)

            self.twitter = Twitter(
                auth=OAuth(
                    self.oauth_token,
                    self.oauth_token_secret,
                    CONSUMER_KEY,
                    CONSUMER_SECRET),
                secure=True,
                domain='api.twitter.com')
        except:
            pass

    def fetch_title(self, url):
        parsedurl = urlparse.urlparse(url)
        path = parsedurl.path.split("/")
        id = path[-1]
        tweet = self.twitter.statuses.show(id=id)
        self.logger.info(tweet)

        if 'entities' in tweet and 'media' in tweet['entities']:
            photo_url = tweet['entities']['media'][0]['media_url']
            return "@%s (%s): %s - %s" % (
                tweet['user']['name'], tweet['user']['screen_name'], tweet['text'], photo_url)
        else:
            return "@%s (%s): %s" % (
                tweet['user']['name'], tweet['user']['screen_name'], tweet['text'])
