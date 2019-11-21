
import flickrapi
import json
import xmltodict
import os
from os.path import expanduser
import xml.etree.ElementTree as ET
import inspect

api_key = u'958d89b45e9a9a8147eacaa58fd7fba8'
api_secret = u'f6fb0a89f6c79b28'

flickr = flickrapi.FlickrAPI(api_key, api_secret)
#flickr.authenticate_via_browser(perms='write')

if not flickr.token_valid(perms='write'):

	# Get a request token
	flickr.get_request_token(oauth_callback='oob')

	# Open a browser at the authentication URL. Do this however
	# you want, as long as the user visits that URL.
	authorize_url = flickr.auth_url(perms='write')
	webbrowser.open_new_tab(authorize_url)

	# Get the verifier code from the user. Do this however you
	# want, as long as the user gives the application the code.
	verifier = str(input('Verifier code: '))

	# Trade the request token for an access token
	flickr.get_access_token(verifier)

homeDir = expanduser("~")
topLevelDir = homeDir + "\\Desktop\\UpfPhotoAlbums"

fileName = "5DM48204.jpg"
photoName = fileName
#albumName = "WS 2017 Staff-Group Posed Photos"
albumName = "Argentina-2015-10-10-UPF Principles of Peace Presented in Buenos Aires Seminar"

filePath = "C:\\Users\\lucav\\Desktop\\UpfPhotoAlbums\\WS 2017 Staff-Group Posed Photos\\5DM48204.jpg"

class FileWithCallback(object):
	def __init__(self, filename, callback):
		self.file = open(filename, 'rb')
		self.callback = callback
		# the following attributes and methods are required
		self.len = os.path.getsize(filename)
		self.fileno = self.file.fileno
		self.tell = self.file.tell
		self.format = "etree"

	def read(self, size):
		if self.callback:
			self.callback(self.tell() * 100 // self.len)
		return self.file.read(size)

def callback(progress):
	pass

def uploadPhoto(albumName, photoName, coverPhoto=False):
	if coverPhoto:
		filePath = topLevelDir + "\\" + albumName + "\\Cover Photo\\" + photoName
	else:
		filePath = topLevelDir + "\\" + albumName + "\\" + photoName
	try:
		res = flickr.upload(filePath, FileWithCallback(filePath, callback))	
		print("Uploaded " + photoName)
		return res
	except IOError as e:
		#print(e)
		raise IOError
		return None

# Add a try block in this function to handle the exception
# of trying to use an invalid filename
def uploadAlbum(albumName, api_key):
	albumPath = topLevelDir + "\\" + albumName
	coverPath = albumPath + "\\Cover Photo"
	tagsPath = albumPath + "\\Tags\\tags.txt"

	with open(tagsPath, "r") as _file:
		tags = _file.readlines()
		tags = [tag.strip() for tag in tags]
		tags = " ".join(tags)
		print(tags)

	_dir = os.listdir(coverPath)
	
	if len(_dir) > 1:
		print ("There can only be one photo in the \"Cover Photo\" directory")
		return

	fileName = _dir[0]
	res = uploadPhoto(albumName, fileName, coverPhoto=True)
	if res is None:
		return

	coverPhotoId = getPhotoId(res)
	setPhotoTags(coverPhotoId, tags, api_key)
	res = createAlbum(albumName, api_key, coverPhotoId)	
	if res is None:
		return

	albumId = getPhotosetId(res)

	_dir = os.listdir(albumPath)
	for _file in _dir:
		try:
			res = uploadPhoto(albumName, _file)
			photoId = getPhotoId(res)
			setPhotoTags(photoId, tags, api_key)
			addToAlbum(albumId, photoId, api_key)
		except Exception as e:
			print(e)
			continue


def createAlbum(albumName, api_key, primary_photo_id):
	return flickr._flickr_call(method='flickr.photosets.create',
							   api_key=api_key,
							   title=albumName,
							   primary_photo_id=primary_photo_id)

def addToAlbum(albumId, photoId, api_key):	
	return flickr._flickr_call(method='flickr.photosets.addPhoto',
							   api_key=api_key,
							   photoset_id=albumId,
							   photo_id=photoId)

def setPhotoTags(photoId, tags, api_key):
	return flickr._flickr_call(method='flickr.photos.setTags',
							   api_key=api_key,
							   photo_id=photoId,
							   tags=tags)

def getPhotoId(res):
	return res[0].text

def getPhotosetId(res):
	et = ET.fromstring(res.decode("utf-8"))
	return et[0].attrib['id']


def getAlbums():
	with open("albumList.txt") as _file:
		albums = _file.readlines()
		albums = [album.rstrip('\n') for album in albums]
		albums = [album.split(' :: ')[0] for album in albums]
		return albums

def uploadAlbums(api_key):
	for albumName in getAlbums():
		uploadAlbum(albumName, api_key)
		print("Uploaded ", albumName)


uploadAlbums(api_key)


