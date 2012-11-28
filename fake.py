# Facilitates communications from mesh to server
# Sets up mesh by assigning addresses.
# Sends names from server to mesh
# 
# SLIP Group D, Steven Eardley s0934142

from sys import argv

from SocketConnection import SocketConnection
from Packet import Packet
from payload import *

import time
import threading



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



# ** PI to Mesh **
mesh_listening_socket = None
mesh_sending_socket = None

# Address to give to speck next
current_free_address = 1

# Stores the ID of the specks as {speckID : assignedAddress}
id_dict = dict()


   
def send_init():
    # Send initialisation information from mesh
    print "Connecting to mesh network..."
    global mesh_listening_socket, mesh_sending_socket, n_players, base_location
    
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
                firstData = mesh_listening_socket.receiveData()
                print "First Data: " + firstData.encode('hex_codec')
                first_packet = Packet(firstData)
                first_payload = first_packet.getPayload()
                print first_payload
                
                mesh_listening_socket.setTimeout(1.0)
                                
                # Assign addresses to the expected number of nodes
                s_time = time.time()
                while (len(id_dict) <= 1):
                    if (time.time() > s_time + 10):
                        break;
                    print "Time remaining: " + str(int(s_time + 10 - time.time() + 0.5))
                    try:
                        data = mesh_listening_socket.receiveData()
                        
                        packet = Packet(data)
                        if packet.isIdentification():
                            speck_id = packet.getPayload().getId()
                            
                            print "Id request from %s" % speck_id
                            id_dict.append(speck_id) 
                            # Respond to all requests: packet may have dropped
                            assign_address(speck_id)
                            print "Address assigned"
                            # Reset the start time so we wait from last receive
                            s_time = time.time()
                            print "Time Reset"
                    except:
                        print "No Data received. Retrying"
                
                break
            # If creating sockets doesn't work, wait and try again
            else: 
                time.sleep(1)
        else:
            time.sleep(1)
    
    assign_names()

# Assign an address from the next free address
def assign_address(speck_id):
    global current_free_address, base_location
    payload = PayloadIdentification()
    
    # Only assign an address if we don't have one yet, else send it again. 
    if not speck_id in id_dict:
        id_dict[speck_id] = current_free_address
        print "Speck {0} has now been given address {1}".format(speck_id, current_free_address)
        payload.initialise(speck_id, current_free_address)
        current_free_address += 1
        
        # Additionally, initialise the speck's location as at the base station
        loc_dict[spec_id] = base_location
    else:
        print "Speck %s has already been identified" % speck_id
        payload.initialise(speck_id, id_dict[speck_id])
    
    # Send this ID packet broadcast, with destinationId = 0xFF
    create_and_send_packet(0xFF,0x01,0x00,0x00, payload)
   
# Send a packet to a speck once it has an assigned address.
def create_and_send_packet(destinationId,ttl,msgType,timestamp,payload):
    global mesh_sending_socket
    p = Packet()
    p.initialise(0,destinationId,ttl,msgType,timestamp,payload)
    print "Creating and Sending: "
    print p
    try:
        mesh_sending_socket.sendData(p.getBytes())
        print "sent"
    except:
        print "A connection error happened. Are you simulating the mesh?"

# Give names to all specks as messages
def assign_names():
    m = PayloadMessage()
    m.initialise("WILL$N")
    for i in range(1,5):
        create_and_send_packet(1, 1, 3, 0, m) 
        time.sleep(1)
    for i in range(1,5):
        w = PayloadWaypoint(1,[(56,0),(56,0),(56,0)])
        create_and_send_packet(1,1,2,0,w)
        time.sleep(1)
    
    

# Send command messages to specks
def send_commands(commands):
    print commands
    for (speck_id, waypoints) in commands.items():
        gps_waypoints = map(game_to_location, waypoints)
        print gps_waypoints
        
        m = PayloadWaypoint()
        m.initialise(0, gps_waypoints)
        create_and_send_packet(speck_id, 1, 3, 0, m)



send_init()
