import matplotlib
import csv

def get_map(file_path):
    with open(file_path) as f:
        #スペースで区切る
        reader = csv.reader(f, delimiter=' ')
        data = [row for row in reader]

    #-----lat, lonの取得-----#
    for _ in range(5):
        lat = data[0][3]
        lon = data[0][4]
        rover_azimuth = data[0][5]
        print(lat, lon, rover_azimuth)
