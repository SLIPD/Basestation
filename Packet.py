from struct import *
from payload import *
import cPickle as pickle

'''Packet is the base communication unit between the specks and the server'''
class Packet(object):
	
	originId = None
	destinationId = None
	ttl = None
	msgType = None
	timestamp = None
	payload = None
	
	
	@staticmethod
	def deserialize(data):
		return pickle.loads(data)
	
	def __init__(self, data=None):
		if data != None:
			print "<DATA>",
			for i in range(0,len(data)):
				print int(data[0]),
				print ",",
			print "</DATA>"
			header = data[:6]
			print "<PACKET>",
			print header.encode('hex_codec'),
			print "</PACKET>"
			payload = data[6:]
			self.originId,self.destinationId,self.ttl,self.msgType,self.timestamp = unpack('BBBBH',header)
			if self.msgType == 0:
				self.payload = PayloadIdentification(payload)
			elif self.msgType == 1:
				self.payload = PayloadNodePosition(payload)
			elif self.msgType == 2:
				self.payload = PayloadWaypoint(payload)
			elif self.msgType == 3:
				self.payload = PayloadMessage(payload)
				
	def serialize(self):
		return pickle.dumps(self)
	
	def initialise(self,originId,destinationId,ttl,msgType,timestamp,payload):
		self.originId = originId
		self.destinationId = destinationId
		self.ttl = ttl
		self.msgType = msgType
		self.timestamp = timestamp
		self.payload = payload
		
	def isMessage(self):
		return isinstance(self.payload,PayloadMessage)
		
	def isIdentification(self):
		return isinstance(self.payload,PayloadIdentification)
	
	def getOriginId(self):
		return self.originId
	
	def getDestinationId(self):
		return self.destinationId
	
	def getTtl(self):
		return self.ttl
		
	def getMsgType(self):
		return self.msgType
	
	def getTimestamp(self):
		return self.timestamp
	
	def getPayload(self):
		return self.payload
	
	def getBytes(self):
		bytes = pack('BBBBH', self.originId, self.destinationId, self.ttl, self.msgType, self.timestamp)
		bytes += self.payload.getPaddedBytes()
		return bytes
		
	def __str__(self):
		return "(originId,destinationId,ttl,msgType,timestamp,payload) = (%s,%s,%s,%s,%s,%s)" \
			% (self.originId,self.destinationId,self.ttl,self.msgType,self.timestamp,self.payload)