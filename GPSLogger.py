import GPIS
import csv

from micropyGPS import MicropyGPS

from time import sleep
from time import time

file = open("GPS_log2.txt","w")

myI2CGPS = GPIS.I2CGPS()

print("GTOP Read Example")

x = 0

loc = " "

gps = MicropyGPS(8, "dd")

lat = 0
lon = 0

def userConfig():
        print("Type 0 to skip configuration")
        intin = input("PTMK Number: ")
        intin = int(intin)
        if intin == 0:
                return
        din = raw_input("PTMK Datastream: ")
        writeToGPS(intin, din)
        print("Press 0 to enter another input, 1 to continue")
        intint = input("Input: ")
        if int(intin) == 0:
                userConfig()


def writeToGPS(PMTK, datastream):
        configString = myI2CGPS.createMTKpacket(PMTK, datastream)
        print("Config String: " + configString)
        myI2CGPS.sendMTKpacket(configString)
        sleep(1)

# Initialize by setting to $GPGLL
print("Initializing TITAN X1\n\nSetting NMEA to GPS")
writeToGPS(353, ",1,0,0,0,0")
print("Setting NMEA to RMC")
writeToGPS(314, ",1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
# userConfig()


startTime = time()

with open('gpsdata.csv', mode = 'w') as gpsdata:
    gpswriter = csv.writer(gpsdata, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    while True:
        while myI2CGPS.available() != 0:
            incoming = myI2CGPS.read()
            if (incoming == 36):
                break
            loc += chr(incoming)
        locs = loc.splitlines()
        for y in locs:
            if(len(y) > 1):
                if y[0] == " ":
                    y= y[1:]
                y = "$" +y
                
        #print(y)
        file.write(str(y) + "\n")
        for x in y:
            gps.update(x)
        if time() > startTime + 1:
            print(gps.date)
            print(gps.timestamp)
            print(gps.latitude)
            print(gps.longitude)
            print("DateTime: " + str(gps.date[1]) + "/" + str(gps.date[0]) + "/" + str(gps.date[2]) + " "
                + str(gps.timestamp[0]) + ":" + str(gps.timestamp[1]) + ":" + str(gps.timestamp[2]))
            print("Location : " + str(gps.latitude[0]) + str(gps.latitude[1]) + " "
                + str(gps.longitude[0]) + str(gps.longitude[1]))
            print("Speed: " + str(gps.speed[2]) + "km/h")
            print("Course: " + str(gps.course))
            print(gps.valid)
            gpswriter.writerow([gps.latitude[0], gps.latitude[1], gps.longitude[0], gps.longitude[1], gps.valid])
            startTime = time()


