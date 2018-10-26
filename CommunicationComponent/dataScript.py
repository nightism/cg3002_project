#!/usr/bin/env python

import socket

from threading import Thread
from time import sleep
import time
import serial
# import queue as q
import csv

# from Crypto.Util.Padding import pad
from Crypto import Random
from Crypto.Cipher import AES

import base64

from Crypto.Util.py3compat import *


# imported pad function from Crypto.Util.Padding
def pad(data_to_pad, block_size, style='pkcs7'):
    """Apply standard padding.
    :Parameters:
      data_to_pad : byte string
            The data that needs to be padded.
      block_size : integer
            The block boundary to use for padding. The output length is guaranteed
            to be a multiple of ``block_size``.
      style : string
            Padding algorithm. It can be *'pkcs7'* (default), *'iso7816'* or *'x923'*.
    :Return:
      The original data with the appropriate padding added at the end.
    """

    padding_len = block_size - len(data_to_pad) % block_size
    if style == 'pkcs7':
        padding = bchr(padding_len) * padding_len
    elif style == 'x923':
        padding = bchr(0) * (padding_len - 1) + bchr(padding_len)
    elif style == 'iso7816':
        padding = bchr(128) + bchr(0) * (padding_len - 1)
    else:
        raise ValueError("Unknown padding style")
    return data_to_pad + padding


class serClass:
    hello = ("H").encode()
    ack = ("A").encode()
    nack = ("N").encode()
    res = ("R").encode()
    # dataQueue = q.Queue()
    cumPower = 0
    # setup
    ser = serial.Serial("/dev/ttyS0", 115200)
    ser.flushInput()
    time0 = 0

    def init(self):
        self.running = True

    def end(self):
        self.running = False

    def run(self):
        global MOVE
        isHandshakeDone = False

        # handshaking
        while (isHandshakeDone == False):
            self.ser.write(self.hello)
            time.sleep(0.3)
            if (self.ser.in_waiting > 0):
                ackMsg = self.ser.read().decode()
                if ackMsg == ('A'):
                    self.ser.write(self.ack)
                    isHandshakeDone = True
                    self.ser.readline()
                else:
                    print("handshaking tbd")
                    sleep(0.3)
        prevHeader = -1

        # receive packet
        while True:
            if (self.ser.in_waiting > 8):
                packet = self.ser.readline().decode()
                packet = packet.strip('\x00')
                dataList = list()
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

                    # parsing data, temp write to csv
                    with open('data.csv', 'a') as csvfile:
                        filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        header = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10", "d11", "d12", "target"]
                        filewriter.writerow(header)
                        dataList = []
                        for x in range(0, 16):
                            if (x == 0 or x == 1 or x == 5 or x == 9):  # indexes that contain header + sensor id
                                continue
                            val = float(packet.split(',', 18)[
                                            x])  # 18 is number of values that should remain, header id, 3 sensor id, 12 sensor readings, voltage + current
                            dataList.append(val)
                        print(dataList)
                        dataList.append(MOVE)
                        filewriter.writerow(dataList)

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


MOVE = sys.argv[1]

serComm = serClass()
serCommThread = Thread(target=serComm.run)

serCommThread.start()
