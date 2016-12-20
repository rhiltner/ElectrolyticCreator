import urllib
import urllib2
import re
from collections import deque
from xml.dom.minidom import parseString
import sgmllib  #for HTML parsing
from datetime import datetime, date, timedelta
from decimal import *
import httplib2
import os
import sys
import csv
import time
import dateutil.parser
import dateutil.relativedelta

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
  message=MISSING_CLIENT_SECRETS_MESSAGE,
  scope=YOUTUBE_READ_WRITE_SCOPE)

storage = Storage("%s-oauth2.json" % sys.argv[0])
credentials = storage.get()

if credentials is None or credentials.invalid:
  flags = argparser.parse_args()
  credentials = run_flow(flow, storage, flags)

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
  http=credentials.authorize(httplib2.Http()))

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT) Channel Video Link Collector'
headers = { 'User-agent' : user_agent }

# Assign CSV to read Channel Names from
channelListCSV = "channelList.csv"
videoListCSV = "videoList.csv"
csvFile = csv.reader(open(channelListCSV,'rb'))
videocsvFile = csv.writer(open(videoListCSV,'wb'))
list_queued = deque()

today_date = time.strftime("%Y-%m-%d",time.localtime())
print "Today is: " + today_date

today_year=today_date[:4]
today_month=today_date[5:7]
today_day=today_date[-2:]
d0 = date(int(today_year),int(today_month),int(today_day))
for row in csvFile:
    row=str(row)
    row=row[2:-2]
    channels_response = youtube.channels().list(
      id=row, #"UC_oeTUudZfI-MhpdPDS0pOA",
      part="contentDetails"
    ).execute()
    
    for channel in channels_response["items"]:
      # From the API response, extract the playlist ID that identifies the list
      # of videos uploaded to the authenticated user's channel.
      uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
    
      print "Videos in list %s" % uploads_list_id
    
      # Retrieve the list of videos uploaded to the authenticated user's channel.
      playlistitems_list_request = youtube.playlistItems().list(
        playlistId=uploads_list_id,
        part="snippet",
        maxResults=20
      )
    
      #while playlistitems_list_request:
      playlistitems_list_response = playlistitems_list_request.execute()
        
        # Print information about each video.
      for playlist_item in playlistitems_list_response["items"]:
        title = playlist_item["snippet"]["title"]
        upload_date = playlist_item["snippet"]["publishedAt"]
        video_id = playlist_item["snippet"]["resourceId"]["videoId"]
        upload_date = upload_date[:10]
        #print "%s,%s,%s" % (title, upload_date, video_id)
        upload_year=upload_date[:4]
        upload_month=upload_date[5:7]
        upload_day=upload_date[-2:]
        d1 = date(int(upload_year),int(upload_month),int(upload_day))
        delta = d0 - d1
        if delta < timedelta(days=7):
            print "%s,%s,%s" % (upload_date, video_id, delta)
            videocsvFile.writerow([video_id])
    
      playlistitems_list_request = youtube.playlistItems().list_next(playlistitems_list_request, playlistitems_list_response)

  #print

# Create Channel queue
#for row in csvFile:
#    list_queued.append(row)
    
#print list_queued

#while len(list_queued) > 0:
#    top_of_list = list_queued[0]
#    print ' ** Request: ', str(top_of_list).strip('\'[]\'')
#    opener = urllib2.build_opener()
#    opener.addheaders = [('User-agent', user_agent)]
#    urllib2.install_opener(opener)
#    response = urllib2.urlopen(str(top_of_list).strip('\'[]\''))
#    s = response.read()
    # Try and process the page.
    # The class should have been defined first, remember.
#    myparser = urlparser()
#    myparser.parse(s)
    
#    for link in myparser.get_hyperlinks():
#        print link
    
#    list_queued.popleft()
    
#print list_queued