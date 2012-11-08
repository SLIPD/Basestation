from struct import *

def padTo26(data):
    nulls = ''.join(['\0']*26)
    return (str(data) + nulls)[:26]

PayloadIdentificationType = 0x00
PayloadNodePositionType =     0x01
PayloadWaypointType =         0x02
PayloadMessageType =         0x03


'''PayloadNodePosition holds the position of nodes'''
class PayloadNodePosition(object):
    
    lat = None
    lon = None
    ele = None
    hexaseconds = None
    
    def __init__(self,data=None):
        if(data != None):
            payload = data[:12]
            self.lat,self.lon,self.ele,self.hexaseconds = unpack('IIHH',payload)
            
    def initialise(self, latitude, longitude, elevation, hexaseconds):
        self.lat = latitude
        self.lon = longitude
        self.ele = elevation
        self.hexaseconds = hexaseconds
    
    def getType():
        return 0x01
    
    def getBytes(self):
        return pack('IIHH', self.lat, self.lon, self.ele, self.hexaseconds)
        
    def getPaddedBytes(self):
        return padTo26(self.getBytes())
    
    def getLat(self):
        return self.lat
        
    def getLon(self):
        return self.lon
        
    def getEle(self):
        return self.ele
    
    def getHexaseconds(self):
        return self.hexaseconds
        
    def __str__(self):
        return "(lat,long,elevation,hexaseconds) = (" + str(self.lat) + "," +
str(self.lon) + "," + str(self.ele) + "," + str(self.hexaseconds) + ")"


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
        
    def getType():
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
    nodeId = None
    
    def __init__(self,data=None):
        if(data != None):
            payload = data[:9]
            self.id, self.nodeId = unpack('QB',payload)
            
    def initialise(self, id, nodeId):
        self.id = id
        self.nodeId = nodeId
        
    def getType():
        return 0x00
        
    def getBytes(self):
        return pack('QB', self.id, self.nodeId)
    
    def getPaddedBytes(self):
        return padTo26(self.getBytes())
    
    def getId(self):
        return self.id
        
    def getNodeId(self):
        return self.nodeId
        
    def __str__(self):
        return "(id,nodeId) = (0x%X,%s)" % (self.id, self.nodeId)


'''PayloadMessage is used for sending messages back and forth'''
class PayloadMessage(object):
    
    message = None
    
    def __init__(self,data=None):
        if(data != None):
            (self.message,) = unpack('26s',data)
            
    def initialise(self, message):
        self.message = message
    
    def getType():
        return 0x03
    
    def getBytes(self):
        return pack('26s', self.message)
    
    def getPaddedBytes(self):
        return padTo26(self.getBytes())
    
    def getMessage(self):
        return self.message
        
    def __str__(self):
        return "(message) = (" + str(self.message) + ")"