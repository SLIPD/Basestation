from zmq.core import context, socket
from zmq.eventloop import zmqstream
from zmq.utils import jsonapi
from sys import argv, exit

from SocketConnection import SocketConnection
from Packet import Packet
from payload import *

import time

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

mesh_listening_socket = None
mesh_sending_socket = None

currentFreeAddress = 1

# Stores the ID of the specks as {speckID : assignedAddress}
id_dict = dict()


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
    print "Connecting to mesh network..."
    global mesh_listening_socket, mesh_sending_socket, id_dict, n_players
    mesh_listening_socket = SocketConnection('localhost')
    
    while True:
        if mesh_listening_socket.connectAsReceiver():
            mesh_sending_socket = SocketConnection('', 29877)
            if mesh_sending_socket.connectAsSender():
                # Start the connection to the mesh
                print "Sending init packet to mesh"
                mesh_sending_socket.sendData('*')
                # Assign addresses to the expected number of nodes
                while(len(id_dict) < n_players):
                    data = mesh_listening_socket.receiveData(32)
                    packet = Packet(data)
                    if packet.isIdentification():
                        speck_id = packet.getPayload().getId()
                        print "Id request from %s" % speck_id
                        # Try assigning again - packet may have dropped
                        assignId(speck_id)
                break
            else: 
                time.sleep(1)
        else:
            time.sleep(1)
    
    ids_to_send = [str(item) for item in id_dict.values()]
    initMessage = {"state": "init", "base_location": [25, 25, 0],
"device_ids": ids_to_send}
    pair_stream.send_json(initMessage)

def assignId(speck_id):
    global currentFreeAddress
    payload = PayloadIdentification()
    if not speck_id in id_dict:
        id_dict[speck_id] = currentFreeAddress
        print "Speck {0} has now been given address {1}".format(speck_id,
currentFreeAddress)
        payload.initialise(speck_id,currentFreeAddress)
        currentFreeAddress += 1
    else:
        print "Speck %s has already been identified" % speck_id
        payload.initialise(speck_id, id_dict[speck_id])
    createAndSendPacket(0xFF,0x01,0x00,0x00, payload)
   
def createAndSendPacket(destinationId,ttl,msgType,timestamp,payload):
    p = Packet()
    p.initialise(0,destinationId,ttl,msgType,timestamp,payload)
    print "Creating and Sending: "
    print p
    global mesh_sending_socket
    mesh_sending_socket.sendData(p.getBytes())

command_stream.send_multipart(["PI"])
command_stream.on_recv(setup_pair)

command_stream.io_loop.start()
