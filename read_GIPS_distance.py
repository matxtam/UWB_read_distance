import serial
import binascii
import numpy as np
import pandas as pd
import collections
import time
import socket
# COM_PORT = 'dev/ttyUSB0'  # for rpi
COM_PORT = '/dev/ttyS3'  # for rpi
# COM_PORT = 'COM4'   # for computer
anchor_IDs = ['0241000000000000','0341000000000000','0441000000000000','0541000000000000']
BAUD_RATES = 57600    
ser_UWB = serial.Serial(COM_PORT, BAUD_RATES) 
diss = np.zeros(4)

x1 = 1
y1 = 2
x2 = 3
y2 = 4
x3 = 5
y3 = 6

X = np.array([x1, x2, x3])
Y = np.array([y1, y2, y3])
XY = X.cross(Y).dot(np.array([1, 1, 1]))
C0 = np.array([(x1*x1 + y1*y1),(x2*x2 + y2*y2), (x3*x3 + y3*y3) ])

def swapEndianness(hexstring):
	ba = bytearray.fromhex(hexstring)
	ba.reverse()
	return ba.hex()

def UWB_dis():

    # dis_queue = collections.deque(maxlen = 1)
    # t = time.time()
    rx = ser_UWB.read(66) # original 264 = 66*4
    rx = binascii.hexlify(rx).decode('utf-8')
    global diss
    
    for index, anchor_ID in anchor_IDs:
        if( rx != ' ' and rx.find(anchor_ID) >= 0 and rx.find(anchor_ID) <= (len(rx)-24)):
            dis_index = rx.find(anchor_ID) 
            dis = rx[dis_index + 16 : dis_index + 24] # ToF distance
            dis = swapEndianness(dis)
            # dis_time = rx[dis_index - 18 : dis_index - 16]

            if dis != "":
                dis = int(dis_1,16)
                if dis >= 65536:      # solve sign
                    dis = 65536 - dis
            else:
               dis = 0
        else:
            dis = 0
        diss[index] = dis
        
    return diss

def _main():
    data_filename = 'UWB_distance.csv'    
    dis_to_tag_ls = []
    count = 0
    try:
        while(count < 100):
            dis_to_tag = UWB_dis()
            print("anchor ID 0? " + str(dis_to_tag[0]), end="\t")
            print("anchor ID 7: " + str(dis_to_tag[1]), end="\t")
            print("anchor ID 2? " + str(dis_to_tag[2]), end="\t")
            print("anchor ID 3? " + str(dis_to_tag[3]))
            r1 = dis_to_tag[1]
            r2 = dis_to_tag[2]
            r3 = dis_to_tag[3]
            C = C0 - np.array([r1*r1, r2*r2, r3*r3])
            CY = C.cross(Y).dot(np.array([1, 1, 1]))
            XC = X.cross(C).dot(np.array([1, 1, 1]))
            x = CY / XY / 2
            y = XC / XY / 2
            print("(x, y) = ({}, {})".format(x, y))
            

           
    except KeyboardInterrupt:

        dis_to_tag_ls = np.array(dis_to_tag_ls)
            

if __name__ == '__main__':  
    _main()
