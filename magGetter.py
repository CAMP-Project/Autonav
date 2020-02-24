# Simple demo of the LSM9DS1 accelerometer, magnetometer, gyroscope.
# Will print the acceleration, magnetometer, and gyroscope values every second.
import time
import board
import busio
import adafruit_lsm9ds1
import csv

# I2C connection:
def setup():
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)
    centerX, centerY, centerZ = 0, 0, 0

def getAccel():
    return sensor.acceleration

def getMag():
    magX, magY, magZ = sensor.magnetic
    magX = magX - centerX
    magY = magY - centerY
    magZ = magZ - centerZ
    return magX, magY, magZ

def getDeg():
    #this will return the heading in degrees northwise.

def getGyro():
    return sensor.gyro

def setCenterManual(x,y,z):
    # Finds center with user given data
    centerX = x
    centerY = y
    centerZ = z

#def setCenter():
#    # Finds center with fancy algorithm

#main code stuff
setup()
setCenter(0.2,0.2)
<<<<<<< HEAD
print(getMag())
=======
print getMag()
>>>>>>> 5621c46494bfbdd0a7673e6ebaf304860c98140b
