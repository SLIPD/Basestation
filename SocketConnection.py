from socket import *      #import the socket library

class SocketConnection:

	HOST = None
	PORT = None
	ADDR = None
	BUFSIZE = 32
	
	databuffer = []
	
	serv = None  
	conn = None
	
	def __init__(self, host='', port=29876, buffersize=32):
		self.HOST = host
		self.PORT = port
		self.ADDR = (self.HOST,self.PORT)
		self.BUFSIZE = buffersize
		self.serv = socket( AF_INET,SOCK_STREAM)
	
	
	def connectAsSender(self):
		try:
			self.serv.bind((self.ADDR))
			self.serv.listen(5)
			print 'listening...',
			self.conn,addr = self.serv.accept()
			print 'connected!'
			return True
		except Exception as e:
			print 'Failed to connect as sender: ' + e.strerror
			return False
			
	
	def connectAsReceiver(self):
		try:
			self.serv.connect((self.ADDR))
			print 'Connected!'
			return True
		except Exception as e:
			print 'Failed to connect as receiver: ' + e.strerror
			return False
	
	def receiveData(self, buffersize=None):
		b = buffersize or self.BUFSIZE
		return self.serv.recv(b)
		
	def receiveLine(self):
		line = ''
		while(True):
			char = self.serv.recv(1)
			line += char
			if(char == '\r'):
				return line
	
	def sendData(self, data):
		self.conn.send(data)
		
	
	def close(self):
		if(self.conn != None):
			self.conn.close()
