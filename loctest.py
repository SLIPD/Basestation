from math import cos

from geopy.point import Point
from geopy.distance import distance

left_corner_of_area = Point(55.943721, -3.175135)

# Translate GPS co-ords into game co-ordinates
def loc_translate(gps_coords):
    global left_corner_of_area
    (l1, l2, l3) = left_corner_of_area
    (y, x, z) = gps_coords

    #TODO: how does elev data come out of mesh?

    xCoord = distance(l2, x).m / 2.5
    yCoord = distance(l1, y).m / 2.5
    zCoord = distance(l3, z).m / 2.5
    return [xCoord, yCoord, zCoord]

def game_to_location(game_coords):
    global left_corner_of_area
    (l1, l2, l3) = left_corner_of_area
    
    # The game co-ordinates are number of 2.5m squares from the left_corner_of_area
    [x, y, z] = game_coords
    
    # latDist is the m distance of a degree latitude
    latDist = distance(l1, l1 + 1).m
    newlat =  (x * 2.5) / latDist + l1

    # lonDist is the m distance of a degree longitude
    lonDist = distance((l1, l2), (l1, l2 + 1)).m
    newlon =  (y * 2.5) / lonDist + l2

    #TODO: Handle elevation
    elev = (z * 2.5)

    return (newlat, newlon, elev)

print loc_translate((55.943721, -3.175135, 0))
print distance(game_to_location(loc_translate((55.943721, -3.175135, 0))), (55.948960, -3.175999, 0)).m

print game_to_location(loc_translate((55.948960, -3.175999, 0)))
print distance(game_to_location(loc_translate((55.948960, -3.175999, 0))), (55.948960, -3.175999, 0)).m