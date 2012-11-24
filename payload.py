from struct import *
from Base64Compression import Base64Compression

def padTo26(data):
    nulls = ''.join(['\0']*26)
    return (str(data) + nulls)[:26]

PayloadIdentificationType = 0x00
PayloadNodePositionType =   0x01
PayloadWaypointType =       0x02
PayloadMessageType =        0x03


'''PayloadNodePosition holds the position of nodes'''
class PayloadNodePosition(object):
    
    latitude = None
    longitude = None
    elevation = None
    hexaseconds = None
    
    def __init__(self,data=None):
        if(data != None):
            payload = data[:12]
            self.latitude,self.longitude,self.elevation,self.hexaseconds = unpack('iihH',payload)
            self.latitude = self.latitude / 10000
            self.longitude = self.longitude / 10000
            
    def initialise(self, latitude, longitude, elevation, hexaseconds):
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
        self.hexaseconds = hexaseconds
    
    def getType(self):
        return 0x01
    
    def getBytes(self):
        return pack('iihH', self.latitude*10000, self.longitude*10000, self.elevation, self.hexaseconds)
        
    def getPaddedBytes(self):
        return padTo26(self.getBytes())
    
    def getLatitude(self):
        return self.latitude
        
    def getLongitude(self):
        return self.longitude
        
    def getElevation(self):
        return self.elevation
    
    def getHexaseconds(self):
        return self.hexaseconds
        
    def __str__(self):
        return "(lat,long,elevation,hexaseconds) = (" + str(self.latitude) + "," + str(self.longitude) + "," + str(self.elevation) + "," + str(self.hexaseconds) + ")"


'''PayloadWaypoint holds a list of waypoints for the player to go to'''
class PayloadWaypoint(object):
    
    lastSeqNum = None
    points = []
    
    def __init__(self,data=None):
        if(data != None):
            self.lastSeqNum,lat1,long1,lat2,long2,lat3,long3 = unpack('=HIIIIII',data)
            self.points.append((lat1,long1))
            self.points.append((lat2,long2))
            self.points.append((lat3,long3))
            
            
    def initialise(self, lastSeqNum, points):
        self.lastSeqNum = lastSeqNum
        self.points = points
        
    def getType(self):
        return 0x02
        
    def getBytes(self):
        lat1,long1 = self.points[0]
        lat2,long2 = self.points[1]
        lat3,long3 = self.points[2]
        return pack('=HIIIIII', self.lastSeqNum, lat1, long1, lat2, long2, lat3, long3)
    
    def getPaddedBytes(self):
        return padTo26(self.getBytes())
    
    def getLastSeqNum(self):
        return self.lastSeqNum
        
    def getPoints(self):
        return self.points
        

    def __str__(self):
        return "(lastSeqNum,points) = (" + str(self.lastSeqNum) + "," + str(self.points) + ")"



'''PayloadIdentification is used in the DHCP stage'''
class PayloadIdentification(object):
    
    id = None
    tdma_gp = 500
    tdma_txp = 3000
    tdma_txp_p = 300
    nodeId = None
    nc = 8 
    c = 102
    
    def __init__(self,data=None):
        if(data != None):
            payload = data[:23]
            self.id, self.tdma_gp, self.tdma_txp, self.tdma_txp_p, self.nodeId, self.nc, self.c = unpack('QLLLBBB',payload)
            
    def initialise(self, id, nodeId):
        self.id = id
        self.nodeId = nodeId
        
    def getType(self):
        return 0x00
        
    def getBytes(self):
        return pack('QLLLBBB', self.id, self.tdma_gp, self.tdma_txp, self.tdma_txp_p, self.nodeId, self.nc, self.c)
    
    def getPaddedBytes(self):
        return padTo26(self.getBytes())
    
    def getId(self):
        return self.id
        
    def getNodeId(self):
        return self.nodeId
        
    def __str__(self):
        return "(id,tdma_gp,tdma_txp,tdma_txp_p,nodeId,nc,c) = (0x%X,%d,%d,%d,%d,%d,%d)" % (self.id, self.tdma_gp, self.tdma_txp, self.tdma_txp_p, self.nodeId, self.nc, self.c)


'''PayloadMessage is used for sending messages back and forth'''
class PayloadMessage(object):
    
    message = None
    encrypted = False
    b64 = Base64Compression()
    
    def __init__(self,data=None, encrypted=False):
        if(data != None):
            (self.message,) = unpack('26s',data)
            self.encrypted = encrypted
            
    def initialise(self, message):
        self.message = message
        self.encrypted = False
    
    def getType(self):
        return 0x03
    
    def getBytes(self):
        self.encryptMessage()
        print self
        return self.message
    
    def getPaddedBytes(self):
        return padTo26(self.getBytes())
    
    def setMessage(self,message):
        self.message = message
        self.encrypted = False
    
    def getDecryptedMessage(self):
        self.decryptMessage()
        return self.message
    
    def getMessage(self):
        self.decryptMessage()
        return self.message
    
    def encryptMessage(self):
        if(not self.encrypted):
            self.message = self.b64.encodedData(self.message)
            self.encrypted = True
    
    def decryptMessage(self):
        if(self.encrypted):
            self.message = self.b64.decodedData(self.message)
            self.encrypted = False
    
    def printEncryptedMessage(self):
        self.encryptMessage()
        self.b64.printHexString(self.message)
        
    def printDecryptedMessage(self):
        self.decryptMessage()
        print self
        
    def __str__(self):
        if(self.encrypted):
            return "HEX: " + self.b64.getHexString(self.message)
        else:
            return "(message) = (" + str(self.message) + ")"
            
    
    def appendDebugMessage(self, debug):
        self.decryptMessage()
        self.message += "$" + debug
    
    def getPingMessage(self):
        return "Ping"
    
    def getPongMessage(self):
        return "Pong"
        
    def getEnableDebugMessage(self):
        return "EDebug"
    
    def getDisableDebugMessage(self):
        return "DDebug"
        
    def getOutOfRangeMessage(self):
        return "OOR"
    
    
    
    
                
