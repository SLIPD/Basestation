from struct import *

class PayloadNodePosition:
	
	lat = None
	long = None
	elevation = None
	hexaseconds = None
	
	def __init__(self,data=None):
		if(data != None):
			global lat
			global long
			global elevation
			global octoseconds
			lat = ((data[0] << 24)) & 0xFF000000 | ((data[1] << 16) & 0x00FF0000) | ((data[2] << 8) & 0x0000FF00) | (data[3] & 0x000000FF)
			long = ((data[4] << 24)) & 0xFF000000 | ((data[5] << 16) & 0x00FF0000) | ((data[6] << 8) & 0x0000FF00) | (data[7] & 0x000000FF)
			elevation = ((data[8] << 8)) & 0xFF00 | (data[9] & 0x00FF)
			hexaseconds = data[10] & 0xFF
			
	def initialise(self, newLatitude, newLongitude, newElevation, newHexaseconds):
		global lat
		global long
		global elevation
		global hexaseconds
		lat = newLatitude
		long = newLongitude
		elevation = newElevation
		hexaseconds = newHexaseconds
		
	def getBytes(self):
		global lat
		global long
		global elevation
		global hexaseconds
		return pack('IIHH', lat, long, elevation, hexaseconds)
	
	
	def getLat(self):
		global lat
		return lat
		
	def getLong(self):
		global long
		return long
		
	def getElevation(self):
		global elevation
		return elevation
	
	def getHexaseconds(self):
		global hexaseconds
		return hexaseconds
		
	