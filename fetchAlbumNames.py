
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from urllib import request
import base64
import os
from os.path import expanduser

class AlbumFetcher(object):

	def __init__(self):
		self.googlePhotos = self.getPhotosService() 

	def getPhotosService(self):
		creds = None
		# The file token.pickle stores the user's access and refresh tokens, and is
		# created automatically when the authorization flow completes for the first
		# time.
		if os.path.exists('token.pickle'):
			with open('token.pickle', 'rb') as token:
				creds = pickle.load(token)
		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
					'credentials.json', SCOPES)
				creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open('token.pickle', 'wb') as token:
				pickle.dump(creds, token)

		service = build('photoslibrary', 'v1', credentials=creds)
		return service


	def listAllAlbums(self, pageSize=50):
		albumsList = []
		nextPageToken = 'Dummy'
		while nextPageToken != '':
			nextPageToken = '' if nextPageToken == 'Dummy' else nextPageToken
			results = self.googlePhotos.albums().list(pageSize=pageSize, pageToken=nextPageToken).execute()
			albums = results.get('albums', [])
			nextPageToken = results.get('nextPageToken', '')
			for album in albums:
				albumsList.append(album)

		with open("albumList.txt", "w") as _file:
			for album in albumsList:
				line = album['title'] + " :: " + album['id'] + "\n"
				_file.write(line)


# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]
homeDir = expanduser("~")
topLevelDir = homeDir + "\\Desktop\\UpfPhotoAlbums"

#googlePhotos = getPhotosService()

fetcher = AlbumFetcher()
fetcher.listAllAlbums()



