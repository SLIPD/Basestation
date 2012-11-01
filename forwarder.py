from socket import *
import zmq
import time

def getInput():
    while True:
        try:
            print "connecting"
            cli.connect(input)
            print "connected"
            break
        except:
            print "no input...  waiting"
            time.sleep(1)


def getClient(receive=True):
    print "binding to socket"
    sendSocket.bind("tcp://*:9999")
    if(receive):
        print "receiving from socket"
        request = sendSocket.recv()
        print "Received request: " + str(request)

cli = socket(AF_INET, SOCK_STREAM)
input = ('localhost', 29876)
BUFSIZE = 4096

context = zmq.Context()
sendSocket = context.socket(zmq.PUB)
channel = 1
print "Setting up connections"
getInput()
print "getting client"
getClient(False)    

print "Set up complete. Sending data."

while(True):
    time.sleep(0.5)
    data = cli.recv(BUFSIZE)
    if data == 'quit':
        sys.exit()
    else:
        if data != '':
            print data
            sendSocket.send("{0} {1}".format(channel, data))
