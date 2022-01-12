#import modules
import os
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#open and clear csv file
filename = "urma_temp.csv"
f = open(filename, "w+")

f = open('coordinates.txt') #open coordinates document
contents = f.read() #read coordinates
coordinates = contents.splitlines() #turn coordinates into list

for x in range (len(coordinates)): #for each coordinate
    cmd_tmp = "/usr/bin/wgrib2 %s -match '%s' -lon %s >> urma_temp.csv" % ('hrrr.t00z.wrfsfcf00_1.grib2', ':TMP:2 m above ground:anl:', coordinates[x])
    os.system(cmd_tmp) #perform command to put lat, lon, and value into csv

with open('urma_temp.csv', 'r') as f:
  csv_reader = csv.reader(f)
  csv_list = list(csv_reader)  
    
for location in csv_list:
    location[0] = float((location[0]).split('=')[1])
    location[1] = float((location[1]).split('=')[1])
    location[2] = float((location[2]).split('=')[1])
    location = str(location)

df = pd.DataFrame(columns=['latitude', 'longitude', 'value'])
for i in range(len(csv_list)):
    df.loc[i] = csv_list[i][0],csv_list[i][1],csv_list[i][2]
print(df)