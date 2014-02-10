#!/usr/bin/python
"""
author: matt venn
"""

#import the cosm library
from CosmFeedUpdate import *
import serial
import fcntl
import datetime
import time
import re

#locking
file = "/tmp/current_cost.lock"
fd = open(file,'w')
try:
    print "check lock"
    fcntl.lockf(fd,fcntl.LOCK_EX | fcntl.LOCK_NB)
    print "ok"
except IOError:
    print "another process is running with lock. quitting!", file
    exit(1)

#private key stored in a file
keyfile="api.key"
key=open(keyfile).readlines()[0].strip()

feed_id = "130883"
pfu = CosmFeedUpdate(feed_id,key)

meter_port = "/dev/ttyUSB0"

def read_meter():
    serial_port = serial.Serial()
    serial_port.port=meter_port
    serial_port.baudrate=57600
    serial_port.timeout=10
    serial_port.open()
    print "opened serial"

    data = None
    full_line = ""
    while not data:
        for line in serial_port.readline():
            full_line += line
        """
<msg><src>CC128-v0.11</src><dsb>00591</dsb><time>03:01:16</time><tmpr>15.7</tmpr><sensor>0</sensor><id>00077</id><type>1</type><ch1><watts>02777</watts></ch1></msg>
        """

        m = re.search( "<tmpr>(\d+\.\d+)</tmpr>.*<watts>(\d+)</watts>", full_line )
        if m != None:
            if m.group(1) and m.group(2):
                data = (float(m.group(1)), float(m.group(2)))
                break

    if not data:
        raise Exception( "problem getting serial_port data" )
    else:
        return data

data = read_meter()
print "temp: ", data[0]
print "energy: ", data[1]

pfu.addDatapoint('temperature', data[0])
pfu.addDatapoint('energy', data[1])

# finish up and submit the data
pfu.buildUpdate()
pfu.sendUpdate()
print "done"
