
import flickrapi
import json
import xmltodict
import os
from os.path import expanduser
import xml.etree.ElementTree as ET
import inspect
from MessageLogger import MessageLogger

api_key = u'958d89b45e9a9a8147eacaa58fd7fba8'
api_secret = u'f6fb0a89f6c79b28'

homeDir = expanduser("~")
topLevelDir = homeDir + "\\Desktop\\UpfPhotoAlbums"

def callback(progress):
	pass

class FileWithCallback(object):
	def __init__(self, filename, callback):
		self.file = open(filename, 'rb')
		self.callback = callback
		self.len = os.path.getsize(filename)
		self.fileno = self.file.fileno
		self.tell = self.file.tell
		self.format = "etree"

	def read(self, size):
		if self.callback:
			self.callback(self.tell() * 100 // self.len)
		return self.file.read(size)

class Uploader(object):

	def __init__(self, api_key, api_secret):
		self.flickr = flickrapi.FlickrAPI(api_key, api_secret)
		self.authenticateFlickr()
		self.api_key = api_key
		self.logger = MessageLogger(logName="upload.log")

	def authenticateFlickr(self):
		if not self.flickr.token_valid(perms='write'):

			# Get a request token
			self.flickr.get_request_token(oauth_callback='oob')

			# Open a browser at the authentication URL. Do this however
			# you want, as long as the user visits that URL.
			authorize_url = self.flickr.auth_url(perms='write')
			webbrowser.open_new_tab(authorize_url)

			# Get the verifier code from the user. Do this however you
			# want, as long as the user gives the application the code.
			verifier = str(input('Verifier code: '))

			# Trade the request token for an access token
			self.flickr.get_access_token(verifier)

	def uploadPhoto(self, albumName, photoName, coverPhoto=False):
		if coverPhoto:
			filePath = topLevelDir + "\\" + albumName + "\\Cover Photo\\" + photoName
		else:
			filePath = topLevelDir + "\\" + albumName + "\\" + photoName
		
		return self.flickr.upload(filePath, FileWithCallback(filePath, callback))	

	# Add a try block in this function to handle the exception
	# of trying to use an invalid filename
	def uploadAlbum(self, albumName):
		
		msg = "\tUploading " + albumName + "..."
		self.logger.log(msg)

		albumPath = topLevelDir + "\\" + albumName
		coverPath = albumPath + "\\Cover Photo"
		tagsPath = albumPath + "\\Tags\\tags.txt"

		with open(tagsPath, "r") as _file:
			tags = _file.readlines()
			tags = [tag.strip() for tag in tags]
			tags = " ".join(tags)

		_dir = os.listdir(coverPath)

		if len(_dir) == 0:
			raise Exception("The \"Cover Photo\" directory is empty")

		if len(_dir) > 1:
			raise Exception("There can only be one photo in the \"Cover Photo\" directory")

		fileName = _dir[0]
		res = self.uploadPhoto(albumName, fileName, coverPhoto=True)
		if res is None:
			raise Exception("Failed to upload cover photo")

		coverPhotoId = self.getPhotoId(res)
		self.setPhotoTags(coverPhotoId, tags)
		res = self.createAlbum(albumName, coverPhotoId)	
		if res is None:
			raise Exception("Failed to create album on Flickr")

		albumId = self.getPhotosetId(res)

		_dir = os.listdir(albumPath)
		for _file in _dir:
			if _file != "Cover Photo" and _file != "Tags":
				res = self.uploadPhoto(albumName, _file)
				photoId = self.getPhotoId(res)
				self.setPhotoTags(photoId, tags)
				self.addToAlbum(albumId, photoId)


	def createAlbum(self, albumName, primary_photo_id):
		return self.flickr._flickr_call(method='flickr.photosets.create',
								   api_key=self.api_key,
								   title=albumName,
								   primary_photo_id=primary_photo_id)

	def addToAlbum(self, albumId, photoId):	
		return self.flickr._flickr_call(method='flickr.photosets.addPhoto',
								   api_key=self.api_key,
								   photoset_id=albumId,
								   photo_id=photoId)

	def setPhotoTags(self, photoId, tags):
		return self.flickr._flickr_call(method='flickr.photos.setTags',
								   api_key=self.api_key,
								   photo_id=photoId,
								   tags=tags)

	def getPhotoId(self, res):
		return res[0].text

	def getPhotosetId(self, res):
		et = ET.fromstring(res.decode("utf-8"))
		return et[0].attrib['id']


	def getAlbums(self):
		with open("albumList.txt") as _file:
			albums = _file.readlines()
			albums = [album.rstrip('\n') for album in albums]
			albums = [album.split(' :: ')[0] for album in albums]
			return albums

	def uploadAlbums(self):
		
		numAlbums = len(self.getAlbums())	
		failCount = 0
		failList = []

		msg = "Uploading " + str(numAlbums) + " albums..."
		self.logger.log(msg)

		for albumName in self.getAlbums():
			try:
				self.uploadAlbum(albumName)
				msg = "\tSuccess uploading " + albumName + "\n"
				self.logger.log(msg)
			except Exception as e:
				msg = "\t" + str(e) + "\n"
				self.logger.log(msg)
				failCount = failCount + 1
				failList.append(albumName)
		
		if failCount > 0:
			msg = "Failed to upload " + str(failCount) + " albums"
			self.logger.log(msg)
			for name in failList:
				self.logger.log(name)
		else:
			msg = "All albums uploaded successfully"
			self.logger.log(msg)

		self.logger.endLog()


uploader = Uploader(api_key, api_secret)

uploader.uploadAlbums()

