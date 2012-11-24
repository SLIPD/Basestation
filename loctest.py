from math import cos

from geopy.point import Point
from geopy.distance import distance

left_corner_of_area = (55.943721, -3.175135)

# Translate GPS co-ords into game co-ordinates
def loc_translate(gps_coords):
    global left_corner_of_area
    (l1, l2) = left_corner_of_area
    (x, y, z) = gps_coords

    #TODO: how does elev data come out of mesh?

    xCoord = distance(l1, x).m / 2.5
    yCoord = distance(l2, y).m / 2.5
    zCoord = distance(0, z).m / 2.5
    return [xCoord, yCoord, zCoord]

def game_to_location(game_coords):
    global left_corner_of_area
    print Point(left_corner_of_area)
    # The game co-ordinates are number of 2.5m squares from the left_corner_of_area
    [x, y, z] = game_coords

    #latDist = distance(
    # Latitude: 1 deg = 110540 m

    newlat =  (float(x) * 2.5) / float(110540) + left_corner_of_area[0]

    # Longitude: 1 deg = 111320 * cos(latitude) m
    newlon =  (float(y) * 2.5) / (float(111320) * cos(left_corner_of_area[0])) + left_corner_of_area[1]

    #TODO: Handle elevation
    elev = (z * 2.5)

    return (newlat, newlon, elev)

print loc_translate((55.943721, -3.175135, 0))
print loc_translate((55.948960, -3.175999, 0))

print game_to_location([233, 38, 0])