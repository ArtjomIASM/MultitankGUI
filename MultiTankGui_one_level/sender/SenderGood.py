import socket
import time
import struct
import sys # for exit
import random
from math import*
import numpy as np

def Main():
    try:
        host = 'localhost'
        port = 3030
        server = ('localhost', 3031)
    except host.error:
        print 'Failed to create host and port'
        sys.exit()

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host,port))
    except socket.error:
        print 'Failed to create socket'
        sys.exit()

    print "Client Started."
    print "Client IP: ", host
    print "Client PORT: ", port

    fs = 1000.0  # sample rate
    f = 2  # the frequency of the signal

    # compute the value (amplitude) of the sin wave at the for each sample
    y1 = [np.sin(2.0 * np.pi * f * (i / fs)) for i in np.arange(fs)]
    y2 = [np.sin(0.5 * np.pi * f * (i / fs)) for i in np.arange(fs)]
    y3 = [np.sin(1.0 * np.pi * f * (i / fs)) for i in np.arange(fs)]
    while True:
            #Send
            rnd = 0
            for i in range(len(y1)):
                if (i % 100 == 0):
                    rnd = random.uniform(0, 10)
                    rnd2 = random.uniform(0, 25)
                packetData = struct.pack('>3d', (y1[i] + 1) +  rnd, abs(y2[i]) * rnd2, abs(y3[i]) * rnd2)
                s.sendto(packetData, server)

                time.sleep(20)
    s.close()
if __name__ == '__main__':
    Main()
