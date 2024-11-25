# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 14:51:38 2022

@author: ren tsai
"""
import serial
import numpy as np
from datetime import datetime
import time
import collections
from loc_method import two_stage_solve_trans, two_stage_solve
import pandas as pd

def UWB_dis():
    UWB_port = 'COM4'
    #ser_UWB = serial.Serial(UWB_port, baudrate = 9600, timeout=0.001)
    ser_UWB = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=0.001)
    dis_queue = collections.deque(maxlen=1)
    right_time_q = collections.deque(maxlen = 1)
        
    counter = 0
    t = time.time()
    
    string_time = datetime.now().strftime("%H_%M_%S")
    data_filename = 'UWB_data_' + string_time +'.txt'
    
    rx = ser_UWB.readline().decode('utf-8')
        # print('raw', rx)
    if(rx != ' ' and rx.find('mc') >= 0):
        dis = rx.split(' ')
        dis_array = np.array([(int(dis[2],16)),(int(dis[3],16)), (int(dis[4],16)), (int(dis[5],16))])/1000.0
        dis_array = dis_array - 0.65
        dis_array[0] = dis_array[0]-0.1
        dis_array[1] = dis_array[1]-0.1
        dis_array[2] = dis_array[2]+0.08
        dis_array[3] = dis_array[3]+0.04 
        # print('dis_array', dis_array)
        return dis_array
    
    data_filename = 'UWB_distance.csv'                                      
    anchor_positions = np.array([[0, 0, 0],
                                 [0, 4.83, 0],
                                 [27, 4.83, 1.60],
                                 [27, 0, 1.660]])
        
    #anchor_positions = np.array(anchor_positions)
    anchor_offset = anchor_positions[0]
    A = anchor_positions[1:] - anchor_offset
    u, s, vh = np.linalg.svd(A, full_matrices=True) 
    time_ls = []
    t = time.time()
    dis_to_tag_ls = []
    try:
        while(1):
            #print('start to read data')
            dis_to_tag = UWB_dis()
            if dis_to_tag is not None:
                print('dis_to_tag', dis_to_tag)
                ###校正
                t_two_stage = time.time() - t
                time_ls.append(t_two_stage)
                dis_to_tag_ls.append(dis_to_tag)
                two_stage_result = two_stage_solve_trans(dis_to_tag, anchor_positions,u)
                #two_stage_result = two_stage_solve(dis_to_tag, anchor_positions,u)
                
                print('two_stage_result', two_stage_result)
           
    except KeyboardInterrupt:
        time_ls = np.array(time_ls)
        time_ls = np.transpose(time_ls)
        dis_to_tag_ls = np.array(dis_to_tag_ls)
        dis_to_tag_ls = np.transpose(dis_to_tag_ls)
        df = pd.DataFrame({'time':time_ls.tolist(),
                           'A2':dis_to_tag_ls[:][0].tolist(),
                           'A3': dis_to_tag_ls[:][1].tolist(),
                           'A4': dis_to_tag_ls[:][2].tolist(),
                           'A5':dis_to_tag_ls[:][3].tolist()})
        df.to_csv(data_filename)  

