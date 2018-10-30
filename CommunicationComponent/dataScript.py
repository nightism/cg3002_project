#!/usr/bin/env python

import socket

from threading import Thread
from time import sleep
import time
import serial
import sys
import csv

from Crypto.Util.py3compat import *


class SerClass:
    # core variables
    ser = serial.Serial("/dev/serial0", 115200)
    time0 = 0
    lastMsgTime = None
    cumPower = 0

    # serial messages
    hello = ("H").encode()
    ack = ("A").encode()
    nack = ("N").encode()
    res = ("R").encode()

    def init(self):
        self.running = True

    def end(self):
        self.running = False

    def handshake(self):
        self.ser.write(self.hello)
        time.sleep(0.3)
        if self.ser.in_waiting > 0:
            ackMsg = self.ser.read().decode()
            print("received ack msg ", ackMsg)
            if ackMsg == 'A':
                self.ser.write(self.ack)
                self.ser.readline()
                self.lastMsgTime = time.time()
                print("received A")
                return True
            else:
                print("handshaking tbd")
                sleep(0.3)
        return False

    def run(self):
        global MOVE

        # handshaking
        self.ser.flush()
        while self.handshake() is False:
            continue
        prevHeader = -1
        num = 0

        # receive packet
        while True:
            if (self.ser.in_waiting > 8):
                packet = self.ser.readline().decode()
                packet = packet.strip('\x00')
                self.lastMsgTime = time.time()
                print("Message ", packet)
                print("test what is ", packet.split(',', 1)[0])
                currHeader = int(packet.split(',', 1)[0])
                print("header id: ", currHeader)
                if (prevHeader >= currHeader):
                    self.ser.write(self.nack)
                    print("Header mismatch")
                else:
                    chkSum = int(packet.rsplit(',', 2)[1])
                    print("checksum: ", chkSum)
                    packet = (packet.rsplit(',', 2)[0])
                    # print(len(packet))
                    checkList = bytearray(packet.encode())
                    # print(checkList.decode())
                    testSum = 0
                    for x in range(len(packet)):
                        testSum ^= checkList[x]
                    # print(x, testSum)
                    if (testSum != chkSum):
                        print("break")
                        self.ser.write(self.res)
                    else:
                        self.ser.write(self.ack)
                        prevHeader = currHeader

                    '''
                    #clear existing csv
                    with open('data.csv', 'w') as file:
                        file.truncate()
                        file.close()
                    '''
                    '''
                    header = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "d11", "d12",
                              "d13", "d14", "d15", "target"]
                    '''

                    header = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "d11", "d12", "target"]

                    # parsing data, temp write to csv
                    with open('data.csv', 'a') as csvfile:
                        filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        if num == 0:
                            filewriter.writerow(header)
                        dataList = []
                        for x in range(0, 16):
                            if x == 0 or x == 1 or x == 5 or x == 9:  # indexes that contain header+sensor id
                                continue
                            val = float(packet.split(',', 18)[x])  # 18 is number of values that should remain
                            # header id, 3 sensor id, 12 sensor readings, voltage + current
                            dataList.append(val)
                        print(dataList)
                        dataList.append(MOVE)
                        filewriter.writerow(dataList)

                    num = 1
                    # cumpower calc
                    voltage = float(packet.rsplit(',', 2)[1])
                    voltage = (voltage * 10) / 1023  # convert to Volts
                    print("Voltage: ", voltage)
                    current = float(packet.rsplit(',', 2)[2])
                    current = (current * 5) / 1023  # convert to Amperes
                    print("Current: ", current)
                    if (self.time0 == 0):
                        self.time0 = time.time()
                    else:
                        newTime = time.time()
                        timeElapsed = newTime - self.time0
                        self.cumPower += voltage * current * timeElapsed
                        self.time0 = newTime
                        print("Cumpower: ", self.cumPower)

            # re-handshake functionality
            else:
                if time.time() - self.lastMsgTime > 5:
                    self.ser.close()
                    self.ser = serial.Serial("/dev/serial0", 115200)
                    sleep(0.2)
                    self.ser.flush()
                    self.ser.readline()
                    while self.handshake() is False:
                        print("Re-handshaking")


MOVE = sys.argv[1]

serComm = SerClass()
serCommThread = Thread(target=serComm.run)

serCommThread.start()
