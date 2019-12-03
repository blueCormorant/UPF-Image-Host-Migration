
class MessageLogger(object):

	def __init__(self, logName="photos.log"):
		self.file = open(logName, "w")
		
	def log(self, msg):
		self.file.write(msg + "\n")
		self.file.flush()
		print(msg, flush=True)

	def endLog(self):
		self.file.close()

