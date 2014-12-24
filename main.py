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
from google.appengine.api import urlfetch

api_key = '887bbc50dcce4a987a6ea96172cfe698'
base_url = 'http://ws.audioscrobbler.com/2.0/?format=json'
get_recent_tracks = 'user.getrecenttracks'

class MainHandler(webapp2.RequestHandler):
    
    def get(self):
        #TODO: add a form to enter this in the page
        user = 'colinmgibbs'
        num_tracks = '200'
        full_url = base_url + '&api_key=' + api_key + '&user=' + user + \
            '&method=' + get_recent_tracks + '&limit=' + num_tracks
        
        try:
            response = urlfetch.fetch(
            url = full_url,
            method = urlfetch.GET
        )
        except urlfetch.SSLCertificateError:
            pass
        
        full_json = json.loads(response.content)
        track_list = full_json['recenttracks']['track']
        
        self.response.write('Last 200 songs played by: ' + user + '<br><br>')
        
        for x in track_list:
            title = x['name']
            artist = x['artist']['#text']
            
            self.response.write(artist + ' - ' + title + '<br>')

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
