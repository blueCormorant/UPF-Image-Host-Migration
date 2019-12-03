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
from MessageLogger import MessageLogger


# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]
homeDir = expanduser("~")
topLevelDir = homeDir + "\\Desktop\\UpfPhotoAlbums"


class Downloader(object):

	def __init__(self):
		self.googlePhotos = self.getPhotosService()
		self.logger = MessageLogger(logName="download.log")

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
		return albumsList		

	def getAlbum(self, albumId):
		return self.googlePhotos.albums().get(albumId=albumId).execute()
		
	def listAlbumPhotos(self, albumId, pageSize=50):
		photoList = []
		nextPageToken = 'Dummy'
		while nextPageToken != '':
			nextPageToken = '' if nextPageToken == 'Dummy' else nextPageToken
			results = self.googlePhotos.mediaItems().search(
				body={"albumId": albumId, "pageSize": pageSize, "pageToken": nextPageToken}).execute()
			photos = results.get('mediaItems', [])
			nextPageToken = results.get('nextPageToken', '')
			for photo in photos:
				photoList.append(photo)
			return photoList

	def getPhoto(self, photoId):
		return self.googlePhotos.mediaItems().get(mediaItemId=photoId).execute()

	def getPhotoBinary(self, photo):
		return self.getPhotoBinaryFromBaseUrl(photo['baseUrl'])

	def getPhotoBinaryFromBaseUrl(self, baseUrl):
		baseUrl = baseUrl + "=d"
		res = request.urlopen(baseUrl)
		return res.read()

	def saveToFile(self, data, albumName, fileName, coverPhoto = False):
		if coverPhoto:
			filePath = topLevelDir + "\\" + albumName + "\\" + "Cover Photo\\" + fileName
		else:
			filePath = topLevelDir + "\\" + albumName + "\\" + fileName
		with open(filePath, "wb") as _file:
			_file.write(data)

	def makeAlbumDir(self, albumName):
		newDirName = topLevelDir + '\\' + albumName
		os.mkdir(newDirName)

	def makeCoverPhotoDir(self, albumName):
		newDirName = topLevelDir + '\\' + albumName + '\\' + "Cover Photo"
		os.mkdir(newDirName)

	def makeTagsDir(self, albumName):
		newDirName = topLevelDir + '\\' + albumName + '\\' + "Tags"
		os.mkdir(newDirName)
		
	def downloadAlbum(self, albumId):
		album = self.getAlbum(albumId)
		albumName = album['title']
		msg = "\tDownloading " + albumName + "..."
		self.logger.log(msg)

		coverPhotoBaseUrl = album['coverPhotoBaseUrl']
		coverPhotoMediaItemId = album['coverPhotoMediaItemId']

		self.makeAlbumDir(albumName)
		self.makeCoverPhotoDir(albumName)
		self.makeTagsDir(albumName)

		tags = self.getAlbumTags(albumName)
		self.writeTagsToFile(albumName, tags)


		coverPhoto = self.getPhoto(coverPhotoMediaItemId)
		data = self.getPhotoBinary(coverPhoto)
		self.saveToFile(data, albumName, coverPhoto['filename'], coverPhoto=True)

		photos = self.listAlbumPhotos(albumId)

		for photo in photos:
			if photo['id'] != coverPhoto['id']:
				fileName = photo['filename']
				data = self.getPhotoBinary(photo)
				self.saveToFile(data, albumName, fileName)

		return albumName

	def getAlbumTags(self, albumName):
		tags = []
		with open("tags.pickle", "rb") as _file:
			tagCandidates = pickle.load(_file)
			for key in tagCandidates:
				if tagCandidates[key].lower() in albumName.lower():
					if tagCandidates[key] not in tags:
						tags.append(tagCandidates[key])
		return tags

	def writeTagsToFile(self, albumName, tags):
		tagsDir = topLevelDir + '\\' + albumName + '\\' + "Tags\\"
		tagsFile = tagsDir + "tags.txt"
		with open(tagsFile, "w") as _file:
			for tag in tags:
				_file.write(tag + "\n")

	def getAlbums(self):
		with open("albumList.txt") as _file:
			albums = _file.readlines()
			albums = [album.rstrip('\n') for album in albums]
			albums = [album.split(' :: ') for album in albums]
			return albums


	def downloadAlbums(self):


		numAlbums = len(self.getAlbums())
		failCount = 0
		failList = []
		
		msg = "Downloading " + str(numAlbums) + " albums..."
		self.logger.log(msg)

		for album in self.getAlbums():
			albumName = album[0]
			albumId = album[1]
			try:
				self.downloadAlbum(albumId)
				msg = "\tSuccess downloading " + albumName + "\n"
				self.logger.log(msg)
			except Exception as e:
				msg = "\t" + str(e) + "\n"
				self.logger.log(msg)
				failCount = failCount + 1
				failList.append(albumName)
		
		if failCount > 0:
			msg = "Failed to download " + str(failCount) + " albums"
			self.logger.log(msg)
			for name in failList:
				self.logger.log(name)
		else:
			msg = "All albums downloaded successfully"
			self.logger.log(msg)

		self.logger.endLog()


downloader = Downloader()

downloader.downloadAlbums()
	
