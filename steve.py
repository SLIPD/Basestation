# Facilitates communications from mesh to server
# Sets up mesh by assigning addresses.
# SLIP Group D, Steven Eardley s0934142

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

# ** PI to Mesh **
mesh_listening_socket = None
mesh_sending_socket = None

# Address to give to speck next
current_free_address = 1

# Stores the ID of the specks as {speckID : assignedAddress}
id_dict = dict()

# The GPS location of the base station
base_gps = None

# Handle different sorts of messages from server
def pair_recv(msg):
    print "Received from Server"
    try:
        try:
            j = jsonapi.loads(''.join(msg))
        except TypeError:
            j = jsonapi.loads(msg)
        
        m = "JSON: " + str(j)

        if j['state'] == 'naming':
            assign_names(j['mapping'])
        elif j['state'] == 'commanding':
            # Handle the commands
            print "Command Stuff"
    finally:
        pass
    print m

# Translate GPS co-ords into game co-ordinates
def loc_translate(gps_coords):
    return [25,25,0]

# Creates the paired port to the game server.
def setup_pair(msg):
    global pair_socket, pair_stream, left_corner_of_area, n_players
    [new_port, n_devices, zx, zy] = msg
    print "Reply Received. Port: " + str(new_port)
   
    n_players = int(n_devices)
    left_corner_of_area = (zx, zy)
    
    # Create a paired socket to communicate with server
    pair_socket = ctx.socket(socket.PAIR)
    pair_socket.connect("tcp://{0}:{1}".format(argv[1], new_port))
    pair_stream = zmqstream.ZMQStream(pair_socket, command_stream.io_loop)
    pair_stream.on_recv(pair_recv)
    
    # Send the reply
    #send_init()
    send_init_no_mesh()

# Dummy initialisation with the server
def send_init_no_mesh():
    global current_free_address, n_players, pair_stream
    
    # Add dummy adresses for expected number of players
    for i in range(0, n_players):
        id_dict[i] = current_free_address
        current_free_address += 1
    ids_to_send = [str(item) for item in id_dict.values()]
    
    base_location = loc_translate((0,0,0))
    
    # Send the itialisation message to the server
    initMessage = {"state": "init", "base_location": base_location,"device_ids": ids_to_send}
    pair_stream.send_json(initMessage)
   
def send_init():
    # Send initialisation information from mesh
    print "Connecting to mesh network..."
    global mesh_listening_socket, mesh_sending_socket, n_players, base_gps
    
    mesh_listening_socket = SocketConnection('localhost')
    
    # Perform initialisation actions with mesh: get location and assign addresses.
    while True:
        if mesh_listening_socket.connectAsReceiver():
            mesh_sending_socket = SocketConnection('', 29877)
            if mesh_sending_socket.connectAsSender():
                
                # Start the connection to the mesh
                print "Sending init packet to mesh"
                mesh_sending_socket.sendData('*')
                
                # Get the base station location packet
                first_packet = Patcket(mesh_listening_socket.receiveData())
                first_payload = first_packet.getPayload()
                base_gps = (first_payload.getLatitude(), first_payload.getLongitude(), first_payload.getElevation())
                print base_gps
                
                # Assign addresses to the expected number of nodes
                s_time = time.clock()
                while (len(id_dict) < n_players) and (time.clock() < s_time+ 5):
                    data = mesh_listening_socket.receiveData()
                    packet = Packet(data)
                    if packet.isIdentification():
                        speck_id = packet.getPayload().getId()
                        
                        print "Id request from %s" % speck_id
                        
                        # Respond to all requests: packet may have dropped
                        assign_address(speck_id)
                        
                        # Reset the start time so we wait from last receive
                        s_time = time.clock()
                break
            # If creating sockets doesn't work, wait and try again
            else: 
                time.sleep(1)
        else:
            time.sleep(1)
    
    # Package the assigned addresses for server
    ids_to_send = [str(item) for item in id_dict.values()]
    
    base_location = loc_translate(base_gps)
    
    # Send the itialisation message to the server
    initMessage = {"state": "init", "base_location": base_location,"device_ids": ids_to_send}
    pair_stream.send_json(initMessage)

# Assign an address from the next free address
def assign_address(speck_id):
    global current_free_address
    payload = PayloadIdentification()
    
    # Only assign an address if we don't have one yet, else send it again. 
    if not speck_id in id_dict:
        id_dict[speck_id] = current_free_address
        print "Speck {0} has now been given address {1}".format(speck_id, current_free_address)
        payload.initialise(speck_id, current_free_address)
        current_free_address += 1
    else:
        print "Speck %s has already been identified" % speck_id
        payload.initialise(speck_id, id_dict[speck_id])
    
    # Send this ID packet broadcast, with destinationId = 0xFF
    create_and_send_packet(0xFF,0x01,0x00,0x00, payload)
   
# Send a packet to a speck once it has an assigned address.
def create_and_send_packet(destinationId,ttl,msgType,timestamp,payload):
    p = Packet()
    p.initialise(0,destinationId,ttl,msgType,timestamp,payload)
    print "Creating and Sending: "
    print p
    global mesh_sending_socket
    try:
        mesh_sending_socket.sendData(p.getBytes())
    except:
        print "A connection error happened. Are you simulating the mesh?"

# Give names to all specks as messages
def assign_names(names):
    for speck_id in id_dict.values():
        try:
            assigned_name = names[str(speck_id)]
        except KeyError:
            print "No name found for speck with ID %d" % speck_id
        
        print "Giving name {0} to speck {1}".format(assigned_name, speck_id)
        
        m = PayloadMessage()
        m.initialise(assigned_name)
        create_and_send_packet(speck_id, 1, 3, 0, m.getBytes()) 


# Set the ball rolling...
command_stream.send_multipart(["PI"])
command_stream.on_recv(setup_pair)

command_stream.io_loop.start()