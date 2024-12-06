import serial
import binascii
import numpy as np
import pandas as pd
import collections
import time
import socket
const COM_PORT = 'dev/ttyUSB0'  # for rpi
# const COM_PORT = 'COM0'   # for computer
const anchor_IDs = ['0241000000000000','0341000000000000','0441000000000000','0541000000000000']

def swapEndianness(hexstring):
	ba = bytearray.fromhex(hexstring)
	ba.reverse()
	return ba.hex()

def UWB_dis():

    BAUD_RATES = 57600    
    ser_UWB = serial.Serial(COM_PORT, BAUD_RATES) 
    dis_queue = collections.deque(maxlen = 1)
    t = time.time()
    rx = ser_UWB.read(66) # original 264 = 66*4
    rx = binascii.hexlify(rx).decode('utf-8')
    global diss = np.zeros(4)
    
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
            print("anchor ID 7:" + str(dis_to_tag[1]))

            if(0 not in dis_to_tag):
                count = count + 1

                a2_value = dis_to_tag[0] 
                a3_value = dis_to_tag[1] 
                a4_value = dis_to_tag[2] 
                a5_value = dis_to_tag[3]
                print('anchor ID 7:' + a3_value) 
                dis_to_tag = [a2_value, a3_value, a4_value, a5_value]
                dis_to_tag_ls.append(dis_to_tag)
           
    except KeyboardInterrupt:

        dis_to_tag_ls = np.array(dis_to_tag_ls)
            

if __name__ == '__main__':  
    _main()
