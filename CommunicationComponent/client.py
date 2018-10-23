#!/usr/bin/env python

import socket

from threading import Thread
from time import sleep
from CommunicationComponent.prediction_model import prediction_interface
import time
import numpy as np
import serial
import queue as q
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


# dummy class for ML integration test
class DataTestClass:
    def init(self):
        self.running = True

    def end(self):
        self.running = False

    def run(self):
        global dataQueue
        while True:
            dataList = []
            for x in range(0, 12):
                dataList.append(0.0)
            dataQueue.put(dataList)


class SerClass:
    hello = ("H").encode()
    ack = ("A").encode()
    nack = ("N").encode()
    res = ("R").encode()
    # setup
    ser = serial.Serial("/dev/serial0", 115200)
    ser.flushInput()
    time0 = 0

    def init(self):
        self.running = True

    def end(self):
        self.running = False

    def run(self):
        isHandshakeDone = False
        global voltage
        global current
        global power
        global cumPower
        global dataQueue

        # handshaking
        while isHandshakeDone == False:
            self.ser.write(self.hello)
            time.sleep(0.3)
            if self.ser.in_waiting > 0:
                ackMsg = self.ser.read().decode()
                if ackMsg == 'A':
                    self.ser.write(self.ack)
                    isHandshakeDone = True
                    self.ser.readline()
                else:
                    print("handshaking tbd")
                    sleep(0.3)
        prevHeader = -1

        # receive packet
        while True:
            if self.ser.in_waiting > 8:
                packet = self.ser.readline().decode()
                packet = packet.strip('\x00')
                dataList = list()
                # print("Message ", packet)
                # print("test what is ", packet.split(',', 1)[0])
                currHeader = int(packet.split(',', 1)[0])
                # print("header id: ", currHeader)
                if prevHeader >= currHeader:
                    self.ser.write(self.nack)
                    print("Header mismatch")
                else:
                    chkSum = int(packet.rsplit(',', 2)[1])
                    # print("checksum: ", chkSum)
                    packet = (packet.rsplit(',', 2)[0])
                    # print(len(packet))
                    checkList = bytearray(packet.encode())
                    # print(checkList.decode())
                    testSum = 0
                    for x in range(len(packet)):
                        testSum ^= checkList[x]
                        # print(x, testSum)
                    if testSum != chkSum:
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

                    # parsing data, temp write to csv & dataQueue
                    with open('/home/pi/Desktop/data.csv', 'a') as csvfile:
                        filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        dataList = []
                        for x in range(0, 16):
                            if (x == 0 or x == 1 or x == 5 or x == 9):  # indexes that contain header + sensor id
                                continue
                            val = float(packet.split(',', 18)[
                                            x])  # 18 is number of values that should remain, header id, 3 sensor id, 12 sensor readings, voltage + current
                            dataList.append(val)
                        # print(dataList)
                        filewriter.writerow(dataList)
                        dataQueue.put(dataList)

                    '''
                    # parse data, add to just dataQueue
                    dataList = []
                    for x in range(0, 16):
                        if (x == 0 or x == 1 or x == 5 or x == 9):  # indexes that contain header + sensor id
                            continue
                        val = float(packet.split(',', 18)[
                                        x])  # 18 is number of values that should remain, header id, 3 sensor id, 12 sensor readings, voltage + current
                        dataList.append(val)
                        #print(dataList)
                    dataQueue.put(dataList)
                    '''

                    # cumpower calc
                    voltage = float(packet.rsplit(',', 2)[1])
                    voltage = (voltage * 10) / 1023  # convert to Volts
                    # print("Voltage: ", voltage)
                    current = float(packet.rsplit(',', 2)[2])
                    current = (current * 5) / 1023  # convert to Amperes
                    # print("Current: ", current)
                    if (self.time0 == 0):
                        self.time0 = time.time()
                    else:
                        newTime = time.time()
                        timeElapsed = newTime - self.time0
                        cumPower += voltage * current * timeElapsed
                        power = voltage * current
                        self.time0 = newTime
                        # print("Cumpower: ", cumPower)


class TcpClass:
    MSG = bytes("#|0|0|0|0|", 'utf8')
    lastMsgTime = None
    startTime = None
    dataList = []
    predictArr = [0, 0, 0, 0]
    predictCount = 0
    moveList = ["", "wipers", "number7", "chicken", "sidestep", "turnclap", "number6", "salute", "mermaid", "swing",
                "cowboy", "logout"]

    def init(self):
        self.running = True

    def end(self):
        self.running = False

    def createMsg(self):
        global currMove
        global voltage
        global current
        global power
        global cumPower
        # if currMove == 0 and self.predictCount != 10:
        if currMove == 0:
            # self.MSG = bytes("#|" + str(format(voltage, '.2f')) + "|" + str(format(current, '.2f')) + "|"
            #                 + str(format(power, '.2f')) + "|" + str(format(cumPower, '.2f')) + "|", 'utf8')
            self.MSG = None
            return

        # to test sending
        self.predictCount = 0

        self.MSG = bytes(
            "#" + self.moveList[currMove] + "|" + str(voltage) + "|" + str(current) + "|" + str(power) + "|" + str(
                cumPower) + "|", 'utf8')
        # self.MSG = bytes("#chicken" + "|" + str(format(voltage, '.2f')) + "|" + str(format(current, '.2f')) + "|"
        #                 + str(format(power, '.2f')) + "|" + str(format(cumPower, '.2f')) + "|", 'utf8')

    def getPredict(self):
        global dataQueue
        global model
        global currMove
        # print("predict")
        self.dataList.append(dataQueue.get())
        self.dataList.pop(0)

        # to test sending
        self.predictCount += 1

        if time.time() - self.startTime < 0.2:
            # print(time.time() - self.startTime)
            return
        else:
            self.startTime = time.time()
            # print("predict")
        np_arr = np.array(self.dataList)
        self.predictArr.append(prediction_interface.get_predictions(model, np_arr))
        self.predictArr.pop(0)
        if self.predictArr[0] == self.predictArr[1] == self.predictArr[2] == self.predictArr[3]:
            currMove = self.predictArr[0]
        else:
            currMove = 0
        # print(self.moveList[currMove])

    def run(self):
        global currMove
        global dataQueue
        TCP_IP = '192.168.137.1'
        TCP_PORT = 88
        # BUFFER_SIZE = 100
        SECRET_KEY = bytes("hellohellohello!", 'utf8')
        self.startTime = time.time()

        # initiate connection to server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))

        # infLoop = True
        # counter = 0

        # wait for min sensor readings
        while dataQueue.qsize() < 10:
            continue
        for x in range(0, 8):
            self.dataList.append(dataQueue.get())

        # infinite loop for prediction and sending
        while True:
            # poll model for prediction
            # if self.getPredict() == 0 or self.getPredict() == None:
            #    continue
            # if(self.MSG == None):
            # continue
            self.getPredict()

            # message generation
            self.createMsg()
            print(self.moveList[currMove])

            '''
            # temp termination
            if (counter > 6):
                self.MSG = bytes("#logout|1|2|3|4|", 'utf8')
                infLoop = False
            '''

            '''
            # future termination
            if(currMove == "logout"):
                infLoop = False
            '''

            # send message block
            if self.MSG and (self.lastMsgTime is None or time.time() - self.lastMsgTime > 5):
                # initialise cipher
                iv = Random.new().read(AES.block_size)
                cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
                # encrypt and encode message with AES_CBC and base64 then transmit
                padMsg = pad(self.MSG, AES.block_size)
                encryptMsg = cipher.encrypt(padMsg)
                encodeMsg = base64.b64encode(iv + encryptMsg)
                # print(encodeMsg)

                s.send(encodeMsg)

                # update message delay time
                self.lastMsgTime = time.time()

            # counter += 1
            currMove = 0
            # sleep(2)

        s.close()


voltage = 0
current = 0
power = 0
cumPower = 0
dataQueue = q.Queue()
currMove = 0
model = prediction_interface.get_model()

# threading
tcpComm = TcpClass()
tcpCommThread = Thread(target=tcpComm.run)

serComm = SerClass()
serCommThread = Thread(target=serComm.run)

# dataTest = DataTestClass()
# dataTestThread = Thread(target=dataTest.run)

# dataTestThread.start()
serCommThread.start()
tcpCommThread.start()