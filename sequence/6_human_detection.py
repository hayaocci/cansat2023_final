import time
import math
import rotation
from geopy.distance import geodesic

area_center_lat=goal_lat
area_center_lon=goal_lon
area_radius=10

current_lat,current_lon=get_gps_info
distance=geodesic((area_center_lat,area_center_lon)(current_lat,current_lon))

timeout=20*60

def area():