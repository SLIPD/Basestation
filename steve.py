from zmq.core import context, socket
from zmq.eventloop import zmqstream
from zmq.utils import jsonapi
from sys import argv, exit

if (len(argv) != 3):
	print "Invalid number of arguments. Usage: steve.py host port"
	exit()

# ** PI to Server **
ctx = context.Context.instance()
command_socket = ctx.socket(socket.REQ)
command_socket.connect("tcp://{0}:{1}".format(argv[1], argv[2]))

command_stream = zmqstream.ZMQStream(command_socket)
pair_socket = None
pair_stream = None

# Info to be filled in by server
n_players = 0
left_corner_of_area = (0.0,0.0)

# Initialisation info for server
base_location = None
device_ids = None

# ** PI to Mesh **



def pair_recv(msg):
    print jsonapi.loads(''.join(msg))

# Creates the paired port to the game server.
def setup_pair(msg):
    global pair_socket, pair_stream, left_corner_of_area, n_players
    [new_port, n_devices, zx, zy] = msg
    print "Reply Received. Port: " + str(new_port)
   
    n_players = n_devices
    left_corner_of_area = (zx, zy)
    
    # Create a paired socket to communicate with server
    pair_socket = ctx.socket(socket.PAIR)
    pair_socket.connect("tcp://{0}:{1}".format(argv[1], new_port))
    pair_stream = zmqstream.ZMQStream(pair_socket, command_stream.io_loop)
    pair_stream.on_recv(pair_recv)
    
    # Send the reply
	send_init()
   
def send_init():
    # Send initialisation information from mesh
    
    while not ready:
		try:
			get_dev_ids()
		finally:
			ready = True
    
    initMessage = {"state": "init", "dimensions": [50, 50], "base_location":
[25, 25, 0], "device_ids": ["1", "2", "3", "4", "5", "6"]}
    pair_stream.send_json(initMessage)


command_stream.send_multipart(["PI"])
command_stream.on_recv(setup_pair)

command_stream.io_loop.start()
