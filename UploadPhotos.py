
import flickrapi
import json
import xmltodict
#import flickrapi.FlickrAPI
import os
from os.path import expanduser
import inspect


api_key = u'958d89b45e9a9a8147eacaa58fd7fba8'
api_secret = u'f6fb0a89f6c79b28'

flickr = flickrapi.FlickrAPI(api_key, api_secret)
#flickr.authenticate_via_browser(perms='write')

if not flickr.token_valid(perms='write'):

	print("TESTA")
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

print('Step 2: use Flickr')

homeDir = expanduser("~")
topLevelDir = homeDir + "\\Desktop\\UpfPhotoAlbums"

fileName = "5DM48204.jpg"
photoName = fileName
albumName = "WS 2017 Staff-Group Posed Photos"

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

def uploadPhoto(albumName, photoName):
	filePath = topLevelDir + "\\" + albumName + "\\" + photoName
	try:
		res = flickr.upload(filePath, FileWithCallback(filePath, callback))	
		print("Uploaded " + photoName)
		return res
	except Exception as e:
		print("Could not upload " + photoName)
		print(e)
		return None

# Add a try block in this function to handle the exception
# of trying to use an invalid filename
def uploadAlbum(albumName, coverPhotoId):
	albumPath = topLevelDir + "\\" + albumName
	_dir = os.listdir(albumPath)
	for _file in _dir:
		uploadPhoto(albumName, _file)

def createAlbum(albumName, api_key, primary_photo_id):
	params = {}
	params['method'] = 'flickr.photosets.create'
	params['api_key'] = api_key
	params['title'] = albumName
	params['primary_photo_id'] = primary_photo_id
	FlickrAPI._flickr_call(params)

def getPhotoId(res):
	return res[0].text


