import serial
import binascii
import numpy as np
import pandas as pd

COM_PORT = '/dev/ttyUSB0'  # for rpi/wsl
# COM_PORT = 'COM4'   # for computer
# anchor_IDs = ['0241000000000000','0341000000000000','0441000000000000','0541000000000000']
anchor_IDs = ['0241000000000000','0341000000000000','0541000000000000']
BAUD_RATES = 57600    
ser_UWB = serial.Serial(COM_PORT, BAUD_RATES) 
diss = np.zeros(4)

# anchor position
x1 = 1
y1 = 2
x2 = 3
y2 = 4
x3 = 5
y3 = 6

# position calculation initialization
X = np.array([x1, x2, x3])
Y = np.array([y1, y2, y3])
XY = np.cross(X,Y).dot(np.array([1, 1, 1]))
C0 = np.array([(x1*x1 + y1*y1), (x2*x2 + y2*y2), (x3*x3 + y3*y3)])

def swapEndianness(hexstring):
	ba = bytearray.fromhex(hexstring)
	ba.reverse()
	return ba.hex()

def UWB_dis():
    rx = ser_UWB.read(66 * len(anchor_IDs))
    rx = binascii.hexlify(rx).decode('utf-8')
    global diss
    
    for index, anchor_ID in enumerate(anchor_IDs):
        if( rx != ' ' and rx.find(anchor_ID) >= 0 and rx.find(anchor_ID) <= (len(rx)-24)):
            dis_index = rx.find(anchor_ID) 
            dis = rx[dis_index + 16 : dis_index + 24] # ToF distance
            dis = swapEndianness(dis)

            if dis != "":
                dis = int(dis,16)
                if dis >= 32768:      # solve sign
                    dis = 0
            else:
               dis = 0
        else:
            dis = 0
        diss[index] = dis
        
    return diss

def _main():
    try:
        while(count < 100):
            dis_to_tag = UWB_dis()
            print("anchor ID 6: " + str(dis_to_tag[0]), end="\t")
            print("anchor ID 7: " + str(dis_to_tag[1]), end="\t")
            print("anchor ID 9: " + str(dis_to_tag[2]))
            if (0 not in dis_to_tag):
                r1 = dis_to_tag[1]
                r2 = dis_to_tag[2]
                r3 = dis_to_tag[3]
                C = C0 - np.array([r1*r1, r2*r2, r3*r3])
                CY = np.cross(C,Y).dot(np.array([1, 1, 1]))
                XC = np.cross(X,C).dot(np.array([1, 1, 1]))
                x = CY / XY / 2
                y = XC / XY / 2
                print("(x, y) = ({}, {})".format(x, y))
            

           
    except KeyboardInterrupt:
           pass 

if __name__ == '__main__':  
    _main()
