from loc_method import two_stage_solve_trans
import serial
import binascii
import numpy as np
import pandas as pd
import collections
import time
import socket
from fakeGPS import simulate_GPS

def swapEndianness(hexstring):
	ba = bytearray.fromhex(hexstring)
	ba.reverse() 
	return ba.hex()

def UWB_dis():

    COM_PORT = 'COM5'    
    BAUD_RATES = 57600    
    ser_UWB = serial.Serial(COM_PORT, BAUD_RATES) 
    dis_queue = collections.deque(maxlen = 1)
    t = time.time()
    rx = ser_UWB.read(264)
    rx = binascii.hexlify(rx).decode('utf-8')
    global dis_1
    global dis_2
    global dis_3
    global dis_4
    global dis
    
    if( rx != ' ' and rx.find('0241000000000000') >= 0 and rx.find('0241000000000000') <= (len(rx)-24)):
        
        dis_1_index = rx.find('0241000000000000') 
        dis_1 = rx[dis_1_index + 16 : dis_1_index + 24]
        dis_time1 = rx[dis_1_index - 18 : dis_1_index - 16]
        dis_1 = swapEndianness(dis_1)
        if dis_1 != "":
            dis_1 = int(dis_1,16)
            dis_1 = dis_1/100 
            dis_1 = round(float(dis_1),2)
        else:
           dis_1 = 0
    else:
        dis_1 = 0
    
    if( rx != ' ' and rx.find('0341000000000000') >= 0 and rx.find('0341000000000000') <= (len(rx)-24)):
        
        dis_2_index = rx.find('0341000000000000')
        dis_2 = rx[dis_2_index + 16 : dis_2_index + 24]
        dis_time2 = rx[dis_2_index - 18 : dis_2_index - 16]
        dis_2 = swapEndianness(dis_2)
        
        if dis_2 != "":
            dis_2 = int(dis_2,16)
            dis_2 = round(dis_2/100,2)
        else:
           dis_2 = 0
    else:
        dis_2 = 0
    
    if( rx != ' ' and rx.find('0441000000000000') >= 0 and rx.find('0441000000000000') <= (len(rx)-24)):
        
        dis_3_index = rx.find('0441000000000000')
        dis_3 = rx[dis_3_index + 16 : dis_3_index + 24]
        dis_time3 = rx[dis_3_index - 18 : dis_3_index - 16]
        dis_3 = swapEndianness(dis_3)
        
        if dis_3 != "":
            dis_3 = int(dis_3,16)
            dis_3 = round(dis_3/100,2)
        else:
           dis_3 = 0
    else:
        dis_3 = 0
        
    if( rx != ' ' and rx.find('0541000000000000') >= 0 and rx.find('0541000000000000') <= (len(rx)-24)):
        
        dis_4_index = rx.find('0541000000000000')
        dis_4 = rx[dis_4_index + 16 : dis_4_index + 24]
        dis_time4 = rx[dis_4_index - 18 : dis_4_index - 16]
        dis_4 = swapEndianness(dis_4)
        
        if dis_4 != "":
            dis_4 = int(dis_4,16)
            dis_4 = round(dis_4/100,2)
        else :
           dis_4 = 0
    else:
        dis_4 = 0
        
    dis = np.array([dis_1, dis_2, dis_3, dis_4])
    #print('dis',dis)
    return dis

def _main():
    data_filename = 'UWB_distance.csv'    
    dis_to_tag_ls = []
    count = 0
    try:
        while(1):

            dis_to_tag = UWB_dis()
            if(0 not in dis_to_tag):
                count = count + 1

                a2_value = dis_to_tag[0] 
                a3_value = dis_to_tag[1] 
                a4_value = dis_to_tag[2] 
                a5_value = dis_to_tag[3] 
                dis_to_tag = [a2_value, a3_value, a4_value, a5_value]
                dis_to_tag_ls.append(dis_to_tag)
           
    except KeyboardInterrupt:

        dis_to_tag_ls = np.array(dis_to_tag_ls)
            

if __name__ == '__main__':  
    _main()
