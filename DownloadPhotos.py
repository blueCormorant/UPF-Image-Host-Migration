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

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]
homeDir = expanduser("~")
topLevelDir = homeDir + "\\Desktop\\UpfPhotoAlbums"

def getPhotosService():
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


def listAllAlbums(googlePhotos, pageSize=50):
	albumsList = []
	nextPageToken = 'Dummy'
	while nextPageToken != '':
		nextPageToken = '' if nextPageToken == 'Dummy' else nextPageToken
		results = googlePhotos.albums().list(pageSize=pageSize, pageToken=nextPageToken).execute()
		albums = results.get('albums', [])
		nextPageToken = results.get('nextPageToken', '')
		for album in albums:
			albumsList.append(album)
	return albumsList		

def getAlbum(googlePhotos, albumId):
	return googlePhotos.albums().get(albumId=albumId).execute()
	
def listAlbumPhotos(googlePhotos, albumId, pageSize=50):
	photoList = []
	nextPageToken = 'Dummy'
	while nextPageToken != '':
		nextPageToken = '' if nextPageToken == 'Dummy' else nextPageToken
		results = googlePhotos.mediaItems().search(
			body={"pageSize": pageSize, "pageToken": nextPageToken}).execute()
		photos = results.get('mediaItems', [])
		nextPageToken = results.get('nextPageToken', '')
		for photo in photos:
			photoList.append(photo)
		return photoList

def getPhoto(googlePhotos, photoId):
	return googlePhotos.mediaItems().get(mediaItemId=photoId).execute()

def getPhotoBinary(photo):
	baseUrl = photo['baseUrl'] + "=d"
	res = request.urlopen(baseUrl)
	return res.read()

def saveToFile(data, albumName, fileName):
	filePath = topLevelDir + "\\" + albumName + "\\" + fileName
	with open(filePath, "wb") as _file:
		_file.write(data)

def makeAlbumDir(albumName):
	newDirName = topLevelDir + '\\' + albumName
	os.mkdir(newDirName)


def downloadAlbum(googlePhotos, albumId):
	album = getAlbum(googlePhotos, albumId)
	albumName = album['title']
	photos = listAlbumPhotos(googlePhotos, albumId)
	try:
		makeAlbumDir(albumName)
	except FileExistsError as e:
		print(e)
	for photo in photos:
		fileName = photo['filename']
		data = getPhotoBinary(photo)
		saveToFile(data, albumName, fileName)

albumId = "AM4Ir-I7FCAKh6JMzG6DJ6lfDGQMDXFvqz9LS-lzey85T1KiUnOp-oWZIr__TOPTOXmu6mKmGbbl"
photoId = "AM4Ir-KSR_sciwARpwUtwsgmUOQXrFIX_4BP1fc19iv6If2Hx4CgzFztLBPEhZ45cr2L76qnKdoFLzIdRRMXSoP0mw9PScZx9A"
googlePhotos = getPhotosService()


downloadAlbum(googlePhotos, albumId)

'''
photo = getPhoto(googlePhotos, photoId)
data = getPhotoBinary(photo)
saveToFile(data, "test.png")
'''


