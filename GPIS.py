## Nick Purcell - 2019
# GAUSS-R ASV Team
# Python Library for Titan X1 GPS
# Based on Arduino code for GPS module
# https://github.com/sparkfun/SparkFun_I2C_GPS_Arduino_Library/blob/master/src/SparkFun_I2C_GPS_Arduino$
# https://github.com/sparkfun/SparkFun_I2C_GPS_Arduino_Library/blob/master/src/SparkFun_I2C_GPS_Arduino$
from smbus2 import SMBus
import operator
from time import sleep
from time import time
from micropyGPS import MicropyGPS



# Address of MT33x (0x10)
MT333x_ADDR = 0x10

# This is a limitation of the counter variable "head"
# in the arduino code being an 8-bit unsigned int, might
# not be an issue with the pi
MAX_PACKET_SIZE = 255

# I2C channel, will always be 1 for GPIO
channel = 1



class I2CGPS:

    # Location of the next available spot in the gpsData array, limited to 255
    _head = 0
    # Location of last spot read from gpsData array, limited to 255
    _tail = 0

    # Flag to print the serial commands we are sending to the serial port for debug
    _printDebug = False

    # Empty list for gps data
    gpsData = [0] * MAX_PACKET_SIZE

    # Set up I2C
    def __init__(self):
        # Initialize I2C
        self.bus = SMBus(channel)
        # Reset _head and _tails
        self._tail = 0

    def check(self):
        # Read new data from GPS and check if different from old data
        # If data is new append it to gpsData array
        for x in range (0, 255):
            # Pull in a byte from the GPS and check if it's new.
            incoming = self.bus.read_byte_data(MT333x_ADDR, 1)
            if incoming != 0x0A:
                # Record the byte
                self.gpsData[self._head] = incoming
                self._head += 1
                self._head %= MAX_PACKET_SIZE
                if self._printDebug and self._head == self._tail:
                   print("Buffer Overrun")

    # Return num of available bytes that can be read
    def available(self):
        # If tail = head then there is no new available data in the buffer
        # Check to see if the module has anything in the buffer
        if self._tail == self._head:
            self.check()

        # Return new data count
        if self._head > self._tail:
            return self._head - self._tail
        if self._tail > self._head:
            return MAX_PACKET_SIZE - self._tail + self._head
        # No data available
        return 0

        # Return the next available byte from the gps data array
        # Return 0 if no byte available

    def read(self):
        if self._tail != self._head:
            datum = self.gpsData[self._tail]
            self._tail += 1
            self._tail %= MAX_PACKET_SIZE
            return datum
        return 0

    def enableDebugging(self):
        self._printDebug = True

    def disableDebugging(self):
        self._printDebug = False

    # Send commands to the GPS module

    # Send a give command or config string to the module
    # THe input buffer on the MTK is 255 bytes.  Strings
    # Must be that short.  Delay 10ms after transmission
    def sendMTKpacket(self, command):
        if len(command) > 255:
            if self._printDebug:
                print("Message too long!")
            return False
        # Transmit 16 chunks of 16 Bytes
        for chunk in range(0, 15):
            if chunk*16 >= len(command):
                break
            comChunk = [ord(command[chunk * 16])]
            for x in range(1, 16):
                if len(command) <= chunk * 16 + x: # Done sending bytes
                    break
                comChunk.append(ord(command[chunk * 16 + x]))
            self.bus.write_i2c_block_data(MT333x_ADDR, 0, comChunk)
            sleep(.01);     # Process bytes for 10mS
        return True

    # Given a packet_type and settings return string that is a full
    # config sentence with CRC and \r \n ending bytes
    # PMTK uses different packet numbers to configure the module
    # These vary from 0 to 999.
    # https://www.sparkfun.com/datasheets/GPS/Modules/PMTK_Protocol.pdf
    def createMTKpacket(self, packet_type, data_field_in):
        # Start PMTK sentence off with "PMTK"
        config_sentence = "PMTK"
        # Encode data_field_in
        data_field = data_field_in.encode("utf-8")
        # A zero if the packet type is less than 100, and two zeros if the packet_type is < 10
        if packet_type < 100:
            config_sentence += "0"
        if packet_type < 10:
            config_sentence += "0"
        config_sentence += str(packet_type)
        # only add a data_field if there is a data_field to add
        if len(data_field) > 0:
            config_sentence += data_field
        # Append star followed by checksum
        config_sentence += "*" + str(self.calcCRCforMTK(config_sentence))
        # Put a dollar sign on the front (this must be left until now to properly calculate the cheksum)
        config_sentence = "$" + config_sentence
        # NMEA sentences end with a \r\n
        config_sentence += "\r"
        config_sentence += "\n"

        return config_sentence

    # Calculate a checksum
    def calcCRCforMTK(self, sentence):
        calc_cksum = reduce(operator.xor, (ord(s) for s in sentence), 0)
        return ("0x%X" % calc_cksum).rstrip("L").lstrip("0x") or "0"


