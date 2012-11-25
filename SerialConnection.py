import serial
import sys
import time
	
class SerialConnection:

	connection = None
	
	def connect(self, device, baudrate=115200):
		while True:
			try:
				self.connection=serial.Serial(device,baudrate)
				return True
			except:
				pass
	
	def removeInitialNulls(self):
		char = self.read(1)
		while(char != '*'):
			char = self.read(1)
			print char,
		print ""
	
	def read(self, numBytes=32):
		try:
			return self.connection.read(numBytes)
		except:
			return "Exception: " + str(sys.exc_info()[0])
	
	def readline(self):
		try:
			return self.connection.readline()
		except:
			return "Exception: " + str(sys.exc_info()[0])
			
	def write(self,data):
		try:
			self.connection.write(data)
		except:
			print "Exception: " + str(sys.exc_info()[0])
	
	def flush(self):
		try:
			self.flush()
		except:
			print "Exception: " + str(sys.exc_info()[0])
	
	def close(self):
		print "Closing connection..."
		self.connection.close()
		print "Connetion closed"

