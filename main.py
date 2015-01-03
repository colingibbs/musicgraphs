import webapp2
import json
import logging
import calendar
import cgi
from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext.db import GqlQuery
from datetime import datetime

api_key = '887bbc50dcce4a987a6ea96172cfe698'
base_url = 'http://ws.audioscrobbler.com/2.0/?format=json'
get_recent_tracks = 'user.getrecenttracks'

class GenerateStats(webapp2.RequestHandler):
    
    def post(self):
        #TODO: add comments
        user = cgi.escape(self.request.get('username'))
        q = GqlQuery("SELECT * FROM Listen WHERE user = '" + user + "'")
        
        if q.count() == 0:
            logging.info('Fetching data for user: %s', user)
            self.get_listens_from_last_fm(user=user)
        else:
            logging.info('Already have data for user %s in datastore. Not' + \
            ' fetching any new data from Last.fm', user)
        
        for y in range(1, 13):
            plays = 0
            artists = dict()
            
            for x in q:
                if x.time.month == y:
                    plays += 1
                    if x.artist not in artists:
                        artists[x.artist] = 1
                    else:
                       artists[x.artist] += 1

            self.response.write('<b>' + calendar.month_name[y] + '</b>')
            self.response.write('<br>Total plays: ' + str(plays))
            self.response.write('<br>Total artists: ' + str(len(artists)))
            self.response.write('<br><br>Top artists:<br>')
            
            sorted_artists = sorted(artists, key=artists.get, reverse=True)
            for z in range(0, 10):
                self.response.write(str(z+1) + '. ' + sorted_artists[z].encode('utf-8') + ': ' + \
                str(artists[sorted_artists[z]]) + '<br>')
            self.response.write('<br><br>')
        
    def get_listens_from_last_fm(self, user):
        num_tracks = '200'
        page = 1
        retries = 0
        
        #list to store all the track listens before writing to the datastore
        listens = []
        
        end_date = datetime(2014, 1, 1)
        track_date = datetime(2020, 12, 31)
        
        while (track_date >= end_date and retries <= 10):
            logging.info('Requestiog page %s of tracks', str(page))
            full_url = base_url + '&api_key=' + api_key + '&user=' + user + \
            '&method=' + get_recent_tracks + '&limit=' + num_tracks + '&page=' + \
            str(page)
            
            try:
                response = urlfetch.fetch(url=full_url, method=urlfetch.GET, deadline=30)
            except urlfetch.DeadlineExceededError:
                self.response.write('<br><br>Deadline Exceeded error<br><br>')
                return
            except urlfetch.DownloadError:
                retries += 1
                logging.info('Got a Download error. Number of retries: ' + str(retries))
                continue
			
            if response.status_code == 503:
                retries += 1
                logging.info('Got a 503. Number of retries: ' + str(retries))
                continue
			
            try:
                full_json = json.loads(response.content)
                track_list = full_json['recenttracks']['track']
            except ValueError:
                self.response.write('<br><br>Value error<br><br>')
                self.response.write(response.content)
                return
            
            for x in track_list:
                track = x['name']
                mbid = x['mbid']
                artist = x['artist']['#text']
                artist_mbid = x['artist']['mbid']
                album = x['album']['#text']
                album_mbid = x['album']['mbid']
                track_date = datetime.utcfromtimestamp(float(x['date']['uts']))
                
                #only save listens from 2014
                if track_date.year == 2014:
                    l = Listen(user = user, track=track, artist=artist, album=album, \
                    time=track_date, mbid=mbid, artist_mbid=artist_mbid, album_mbid=album_mbid)
                
                    listens.append(l)
            page += 1
            retries = 0    
        
        logging.info('Finished fetching from Last.fm. Writing all listens to the datastore')
        db.put(listens)

class GetUser(webapp2.RequestHandler):
    def get(self):
        self.response.write(""" \
        Enter Last.fm username
        <form action="/stats" method="post">
          <div><input type="text" name="username"></div>
          <div><input type="submit" value="Submit"></div>
        </form>
        """)

app = webapp2.WSGIApplication([
    ('/', GetUser),
    ('/stats', GenerateStats)
], debug=True)

class Listen(db.Model):
  user = db.StringProperty(required=True)
  mbid = db.StringProperty()
  track = db.StringProperty(required=True)
  artist = db.StringProperty(required=True)
  artist_mbid = db.StringProperty()
  album = db.StringProperty(required=True)
  album_mbid = db.StringProperty()
  time = db.DateTimeProperty(required=True)
