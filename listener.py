from SocketConnection import SocketConnection
  

socket = SocketConnection('localhost')

if(socket.connectAsReceiver()):
	while(True):
		data = socket.receiveData()
		if(data == 'quit'):
			break
		else:
			if(data != ''):
				print data,
	
	socket.close()
