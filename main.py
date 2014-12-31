#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import json
import logging
from google.appengine.api import urlfetch
from datetime import datetime

api_key = '887bbc50dcce4a987a6ea96172cfe698'
base_url = 'http://ws.audioscrobbler.com/2.0/?format=json'
get_recent_tracks = 'user.getrecenttracks'

class MainHandler(webapp2.RequestHandler):
    
    def get(self):
        #TODO: add a form to enter this in the page
        user = 'colinmgibbs'
        num_tracks = '200'
        page = 1
        track_count = 1
        retries = 0
        
        self.response.write('All songs played by: ' + user + '<br><br>')
        
        end_date = datetime(2014, 12, 1)
        track_date = datetime(2020, 12, 31)
        
        while (track_date >= end_date and retries <= 10):
            logging.debug('Requestiog page %s of tracks', str(page))
            full_url = base_url + '&api_key=' + api_key + '&user=' + user + \
            '&method=' + get_recent_tracks + '&limit=' + num_tracks + '&page=' + \
            str(page)
            
            try:
                response = urlfetch.fetch(url=full_url, method=urlfetch.GET, deadline=60)
            except urlfetch.DeadlineExceededError:
                self.response.write('<br><br>Deadline Exceeded error<br><br>')
                return
            except urlfetch.DownloadError:
                retries += 1
                logging.debug('Got a Download error. Number of retries: ' + str(retries))
                continue
			
            if response.status_code == 503:
                retries += 1
                logging.debug('Got a 503. Number of retries: ' + str(retries))
                continue
			
            try:
                full_json = json.loads(response.content)
                track_list = full_json['recenttracks']['track']
            except ValueError:
                self.response.write('<br><br>Value error<br><br>')
                self.response.write(response.content)
                return
            
            for x in track_list:
                title = x['name']
                artist = x['artist']['#text']
                album = x['album']['#text']
                track_date = datetime.utcfromtimestamp(float(x['date']['uts']))
                
                self.response.write(str(track_count) + '. ' + artist + ' - ' + title + \
                ' - ' + str(track_date.month) + '/' + str(track_date.day) + '/' + \
                str(track_date.year) + '<br>')
                track_count += 1
            page += 1
            retries = 0

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
