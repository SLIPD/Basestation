from sys import argv
import math

class Base64Compression:
    characters = ['\0',    'A','B','C','D','E','F','G','H',
                            'I','J','K','L','M','N','O','P',
                            'Q','R','S','T','U','V','W','X',
                            'Y','Z','0','1','2','3','4','5',
                            '6','7','8','9',' ','.',',','<',
                            '>','/','?',';',':','|','"','!',
                            '@','#','%','&','*','(',')','-',
                            '_','=','+','\'','$'];
    
    
    def stringLength(self,inputData):
        byteNum = 0;
        bitNum = 8;
        current = 0;
        while(True):
            if(bitNum == 8):
                current = (inputData[byteNum] >> 2) & 0x3F;
                bitNum = 2;
            elif(bitNum == 6):
                current = inputData[byteNum] & 0x3F;
                byteNum += 1;
                bitNum = 8;
            elif(bitNum == 4):
                current = (inputData[byteNum] << 2) & 0x3C;
                byteNum += 1;
                current = current | ((inputData[byteNum] >> 6) & 0x03);
                bitNum = 6;
            elif(bitNum == 2):
                current = (inputData[byteNum] << 4) & 0x30;
                byteNum += 1;
                current = current | ((inputData[byteNum] >> 4) & 0x0F);
                bitNum = 4;
            
            if(current == 0):
                return byteNum;
    
    def getHexString(self,string):
        output = ""
        stringLen = len(string);
        for i in range(0,stringLen):
            output += "%s" % repr(string[i])
        return ''.join(output)
    
    def printHexString(self,string):
        stringLen = len(string);
        for i in range(0,stringLen):
            print "%.2X" % string[i],
        print ""
    
    def printIntString(self,string):
        stringLen = self.stringLength(string);
        for i in range(0,stringLen):
            print "%d " % string[i],
        print ""
    
    
    def findPosition(self,character, array):
        current = ord(character);
        if(current >=97 and current <= 123):
            current = current - 32;
        for i in range(0,len(array)):
            if(chr(current) == array[i]):
                return i;
        return 0xFF;
    
    def getCharacter(self,index, array):
        if(index > len(array)):
            return 0xFF;
        return array[index];
    
    
    def encodedData(self,string):
        stringBitLength = len(string) * 6;
        outputLength = int(math.ceil(float(stringBitLength) / 8.0));
        if(stringBitLength % 8 == 0):
            outputLength += 1;
        outputLength += 1;
        returnData = bytearray(outputLength);
        
        byteNum = 0;
        bitNum = 8;
        
        for i in range(0,outputLength):
            returnData[i] = '\x00';
    
        for i in range(0,len(string)):
            value = self.findPosition(string[i],self.characters);
            if(value == 0xFF):
                continue;
            if(bitNum == 8):
                returnData[byteNum] = (value << 2) & 0xFC;
                bitNum = 2;
            elif(bitNum == 6):
                returnData[byteNum] = (returnData[byteNum] & 0xC0) | (value & 0x3F);
                byteNum += 1;
                bitNum = 8;
            elif(bitNum == 4):
                returnData[byteNum] = (returnData[byteNum] & 0xF0) | ((value >> 2) & 0x0F);
                byteNum += 1;
                returnData[byteNum] = (returnData[byteNum] & 0x3F) | ((value << 6) & 0xC0);
                bitNum = 6;
            elif(bitNum == 2):
                returnData[byteNum] = (returnData[byteNum] & 0xFC) | ((value >> 4) & 0x03);
                byteNum += 1;
                returnData[byteNum] = (returnData[byteNum] & 0x0F) | ((value << 4) & 0xF0);
                bitNum = 4;
        
        return returnData;
        
    
    def decodedData(self,inputData):
        stringBitLength = self.stringLength(inputData) * 8;
        outputLength = int(math.ceil(float(stringBitLength) / 6.0));
        if(stringBitLength % 6 == 0):
            outputLength += 1;
        #outputLength += 1;
        
        returnData = bytearray(outputLength);
        
        byteNum = 0;
        bitNum = 8;
        current = 0;
        for i in range(0,outputLength):
            returnData[i] = '\x00';
        
        for i in range(0,outputLength):
            if(bitNum == 8):
                current = (inputData[byteNum] >> 2) & 0x3F;
                bitNum = 2;
            elif(bitNum == 6):
                current = inputData[byteNum] & 0x3F;
                byteNum += 1;
                bitNum = 8;
            elif(bitNum == 4):
                current = (inputData[byteNum] << 2) & 0x3C;
                byteNum += 1;
                current = current | ((inputData[byteNum] >> 6) & 0x03);
                bitNum = 6;
            elif(bitNum == 2):
                current = (inputData[byteNum] << 4) & 0x30;
                byteNum += 1;
                current = current | ((inputData[byteNum] >> 4) & 0x0F);
                bitNum = 4;
            
            character = self.getCharacter(current,self.characters);
            if(character == 0xFF):
                continue;
            returnData[i] = character;
        return returnData;
        
