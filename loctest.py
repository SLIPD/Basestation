from math import cos

from geopy.point import Point
from geopy.distance import distance

origin = (55.943721, -3.175135, 0)
left_corner_of_area = Point(origin[0], origin[1])

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


#p = (origin[0] + 0.001, origin[1] + 0.001, 0)
p = (origin[0] + 1, origin[1],0)

print origin
print loc_translate(origin)
print game_to_location(loc_translate(origin))
print distance(game_to_location(loc_translate(origin)), origin).m
print ""
print "old p: " + str(p)
print "p -> game coordinate: " + str(loc_translate(p))
print "new p: " + str(game_to_location(loc_translate(p)))
print "distance from above to p: " + str(distance(game_to_location(loc_translate(p)), p).m)