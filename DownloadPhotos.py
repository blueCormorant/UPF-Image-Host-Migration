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
			body={"albumId": albumId, "pageSize": pageSize, "pageToken": nextPageToken}).execute()
		photos = results.get('mediaItems', [])
		nextPageToken = results.get('nextPageToken', '')
		for photo in photos:
			photoList.append(photo)
		return photoList

def getPhoto(googlePhotos, photoId):
	return googlePhotos.mediaItems().get(mediaItemId=photoId).execute()

def getPhotoBinary(photo):
	return getPhotoBinaryFromBaseUrl(photo['baseUrl'])

def getPhotoBinaryFromBaseUrl(baseUrl):
	baseUrl = baseUrl + "=d"
	res = request.urlopen(baseUrl)
	return res.read()

def saveToFile(data, albumName, fileName, coverPhoto = False):
	if coverPhoto:
		filePath = topLevelDir + "\\" + albumName + "\\" + "Cover Photo\\" + fileName
	else:
		filePath = topLevelDir + "\\" + albumName + "\\" + fileName
	with open(filePath, "wb") as _file:
		_file.write(data)

def makeAlbumDir(albumName):
	newDirName = topLevelDir + '\\' + albumName
	os.mkdir(newDirName)

def makeCoverPhotoDir(albumName):
	newDirName = topLevelDir + '\\' + albumName + '\\' + "Cover Photo"
	os.mkdir(newDirName)

def makeTagsDir(albumName):
	newDirName = topLevelDir + '\\' + albumName + '\\' + "Tags"
	os.mkdir(newDirName)
	
def downloadAlbum(googlePhotos, albumId):
	album = getAlbum(googlePhotos, albumId)
	albumName = album['title']
	coverPhotoBaseUrl = album['coverPhotoBaseUrl']
	coverPhotoMediaItemId = album['coverPhotoMediaItemId']


	try:
		makeAlbumDir(albumName)
		makeCoverPhotoDir(albumName)
		makeTagsDir(albumName)
	except FileExistsError as e:
		print(e)
		return

	tags = getAlbumTags(albumName)
	writeTagsToFile(albumName, tags)


	coverPhoto = getPhoto(googlePhotos, coverPhotoMediaItemId)
	data = getPhotoBinary(coverPhoto)
	saveToFile(data, albumName, coverPhoto['filename'], coverPhoto=True)

	photos = listAlbumPhotos(googlePhotos, albumId)

	for photo in photos:
		if photo['id'] != coverPhoto['id']:
			fileName = photo['filename']
			data = getPhotoBinary(photo)
			saveToFile(data, albumName, fileName)
		else:
			print("Got cover photo")

def getAlbumTags(albumName):
	tags = []
	with open("tags.pickle", "rb") as _file:
		tagCandidates = pickle.load(_file)
		for key in tagCandidates:
			if tagCandidates[key].lower() in albumName.lower():
				if tagCandidates[key] not in tags:
					tags.append(tagCandidates[key])
	return tags

def writeTagsToFile(albumName, tags):
	tagsDir = topLevelDir + '\\' + albumName + '\\' + "Tags\\"
	tagsFile = tagsDir + "tags.txt"
	with open(tagsFile, "w") as _file:
		for tag in tags:
			_file.write(tag + "\n")


albumId = "AM4Ir-I7FCAKh6JMzG6DJ6lfDGQMDXFvqz9LS-lzey85T1KiUnOp-oWZIr__TOPTOXmu6mKmGbbl"
#photoId = "AM4Ir-KSR_sciwARpwUtwsgmUOQXrFIX_4BP1fc19iv6If2Hx4CgzFztLBPEhZ45cr2L76qnKdoFLzIdRRMXSoP0mw9PScZx9A"

#albumId = "AM4Ir-LgYgoS-JXdwMRp3s5ICyDbbehLApAPJWldevR2UWFpcoKRyyzwAL80Dnu2LoQPCAnlaKgh"
googlePhotos = getPhotosService()

downloadAlbum(googlePhotos, albumId)

'''
photo = getPhoto(googlePhotos, photoId)
data = getPhotoBinary(photo)
saveToFile(data, "test.png")
'''


