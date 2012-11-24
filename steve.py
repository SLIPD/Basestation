# Facilitates communications from mesh to server
# Sets up mesh by assigning addresses.
# SLIP Group D, Steven Eardley s0934142

from zmq.core import context, socket
from zmq.eventloop import zmqstream
from zmq.utils import jsonapi
from sys import argv, exit
from math import cos

from SocketConnection import SocketConnection
from Packet import Packet
from payload import *

from geopy.point import Point
from geopy.distance import distance

import time

ip = ""
port = ""
if (len(argv) != 3):
    ip = "127.0.0.1"
    port = "31415"
    print "Invalid number of arguments. Usage: steve.py host port"
    print "Continuing with default of 127.0.0.1:31415"
else:
    ip = argv[1]
    port = argv[2]

# ** PI to Server **
ctx = context.Context.instance()
command_socket = ctx.socket(socket.REQ)
command_socket.connect("tcp://{0}:{1}".format(ip,port))

command_stream = zmqstream.ZMQStream(command_socket)
pair_socket = None
pair_stream = None

# Info to be filled in by server
n_players = 0
left_corner_of_area = None

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
    print "Received from Server:"
    try:
        try:
            j = jsonapi.loads(''.join(msg))
        except TypeError:
            j = jsonapi.loads(msg)

        if j['state'] == 'naming':
            assign_names(j['mapping'])
        elif j['state'] == 'commanding':
            send_commands(j['commanding'])
    finally:
        pass

# Translate GPS co-ords into game co-ordinates
def loc_translate(gps_coords):
    global left_corner_of_area
    (lat, long, elev) = left_corner_of_area
    (y, x, z) = gps_coords
    
    #TODO: how does elev data come out of mesh?
    
    yCoord = round(distance((lat,0), (y,0)).m / 2.5)
    xCoord = round(distance((lat,long), (lat,x)).m / 2.5)
    
    zCoord = (elev - z) / 2.5
    return [xCoord, yCoord, zCoord]

def game_to_location(game_coords):
    global left_corner_of_area
    (lat, long, elev) = left_corner_of_area
    
    # The game co-ordinates are number of 2.5m squares from the left_corner_of_area
    [y, x, z] = game_coords
    
    # latDist is the m distance of a degree latitude
    latDist = distance((lat,0), (lat + 1,0)).m
    newlat =  ((x * 2.5) / latDist) + lat
    # lonDist is the m distance of a degree longitude
    lonDist = distance((newlat, long), (newlat, long + 1)).m
    newlon =  (y * 2.5) / lonDist + long

    #TODO: Handle elevation
    newelev = (z * 2.5) + elev

    return (newlat, newlon, newelev)
    

# Creates the paired port to the game server.
def setup_pair(msg):
    global pair_socket, pair_stream, left_corner_of_area, n_players
    [new_port, n_devices, zx, zy] = msg
    print "Reply Received. Port: " + str(new_port)
   
    n_players = int(n_devices)
    left_corner_of_area = Point(zx, zy)
    
    # Create a paired socket to communicate with server
    pair_socket = ctx.socket(socket.PAIR)
    pair_socket.connect("tcp://{0}:{1}".format(ip, new_port))
    pair_stream = zmqstream.ZMQStream(pair_socket, command_stream.io_loop)
    pair_stream.on_recv(pair_recv)
    
    # Send the reply
    send_init()
    #send_init_no_mesh()

# Dummy initialisation with the server
def send_init_no_mesh():
    global mesh_listening_socket, current_free_address, n_players, pair_stream
    
    mesh_listening_socket = SocketConnection('localhost')
    
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
                first_packet = Packet(mesh_listening_socket.receiveData())
                first_payload = first_packet.getPayload()
                print first_payload
                base_gps = Point(first_payload.getDecimalLatitude(), first_payload.getDecimalLongitude(), first_payload.getElevation())
                print "Base GPS: " + str(base_gps)
                
                mesh_listening_socket.setTimeout(1.0)
                                
                # Assign addresses to the expected number of nodes
                s_time = time.time()
                while (time.time() < s_time + 20) and (len(id_dict) < n_players):
                    print "Time remaining: " + str(int(s_time + 20 - time.time() + 0.5))
                    try:
                        data = mesh_listening_socket.receiveData()
                        
                        packet = Packet(data)
                        if packet.isIdentification():
                            speck_id = packet.getPayload().getId()
                            
                            print "Id request from %s" % speck_id
                            
                            # Respond to all requests: packet may have dropped
                            assign_address(speck_id)
                            
                            # Reset the start time so we wait from last receive
                            s_time = time.time()
                    except:
                        print "No Data received. Retrying"
                    
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
    print "INIT MESSAGE: " + str(initMessage)
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
    print names
    for speck_id in id_dict.values():
        try:
            assigned_name = names[str(speck_id)]
        except KeyError:
            print "No name found for speck with ID %d" % speck_id
        
        print "Giving name {0} to speck {1}".format(assigned_name, speck_id)
        
        m = PayloadMessage()
        m.initialise(assigned_name)
        create_and_send_packet(speck_id, 1, 3, 0, m) 

# Send command messages to specks
def send_commands(commands):
    print commands
    for (speck_id, waypoints) in commands.items():
        gps_waypoints = map(game_to_location, waypoints)
        print gps_waypoints
        
        m = PayloadWaypoint()
        m.initialise(0, gps_waypoints)
        create_and_send_packet(speck_id, 1, 3, 0, m)

# Set the ball rolling...
print "Saying hello to server..."
command_stream.send_multipart(["PI"])
command_stream.on_recv(setup_pair)

command_stream.io_loop.start()
