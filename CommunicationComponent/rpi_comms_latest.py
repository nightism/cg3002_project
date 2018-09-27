#!/usr/bin/env python

import socket

from threading import Thread
from time import sleep
import time
import serial

#from Crypto.Util.Padding import pad
from Crypto import Random
from Crypto.Cipher import AES

import base64

from Crypto.Util.py3compat import *

#imported pad function from Crypto.Util.Padding
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

        padding_len = block_size-len(data_to_pad)%block_size
        if style == 'pkcs7':
                padding = bchr(padding_len)*padding_len
        elif style == 'x923':
                padding = bchr(0)*(padding_len-1) + bchr(padding_len)
        elif style == 'iso7816':
                padding = bchr(128) + bchr(0)*(padding_len-1)
        else:
                raise ValueError("Unknown padding style")
        return data_to_pad + padding


class serClass:	
	def init(self):
		self.running = True
	
	def end(self):
		self.running = False
	
	
	def run(self):
		#setup
		ser = serial.Serial ("/dev/ttyS0", 115200)
		hello = ("\r\nH").encode()
		ack = ("\r\nA").encode()
		nack = ("\r\nN").encode()
		res = ("\r\nR").encode()
		ser.flushInput()
		isHandshakeDone = False
		
		#handshaking
		while(isHandshakeDone == False):
			ser.write(hello)
			time.sleep(0.3)
			if(ser.in_waiting > 0):
				ackMsg = ser.read().decode()
				if ackMsg == ('A'):
					ser.write(ack)
					isHandshakeDone = True
			sleep(3)
		
		prevHeader = -1
		
		#receive packet
		while True:
			if(ser.in_waiting > 8):
				packet = ser.readline().decode()
				print("Message ", packet)
				print("test what is ", packet.split(',',1)[0])
				currHeader = int(packet.split(',',1)[0])
				print("header id: ", currHeader)
				if(prevHeader == currHeader):
                                    ser.write(nack)
                                    break
				chkSum = int(packet.rsplit(',',2)[1])
				print("checksum: ", chkSum)
				packet = (packet.rsplit(',',2)[0])
				#print(len(packet))
				checkList = bytearray(packet.encode())
				#print(checkList.decode())
				testSum = 0
				for x in range(len(packet)):
                                    testSum ^= checkList[x]
                                    print(x, testSum)
				if(testSum != chkSum):
                                    print("break")
                                    ser.write(res)
                                    break
				prevHeader = currHeader
				voltage = int(packet.split(',',3)[1])
				print("Voltage: ", voltage)
				current = int(packet.split(',',3)[2])
				print("Current: ", current)
			

	
class tcp:
	def init(self):
		self.running = True
	
	def end(self):
		self.running = False
	
	def run(self):
		TCP_IP = '172.17.201.182'
		TCP_PORT = 88
		#BUFFER_SIZE = 100
		MSG = bytes("#chicken | 1 | 2 | 3 | 4 |", 'utf8')
		SECRET_KEY = bytes("hellohellohello!", 'utf8')

		#initiate connection to server
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((TCP_IP, TCP_PORT))
		
		infLoop = True
		counter = 0

		while(infLoop == True):
			#initialise cipher
			iv = Random.new().read(AES.block_size)
			cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
			#encrypt and encode message with AES_CBC and base64 then transmit
			padMsg = pad(MSG, AES.block_size)
			#padMsg = MESSAGE
			encryptMsg = cipher.encrypt(padMsg)
			encodeMsg = base64.b64encode(iv + encryptMsg)
			print(encodeMsg)

			s.send(encodeMsg)
			
			counter += 1
			if(counter > 5):
                            MSG = bytes("#logout | 1 | 2 | 3 | 4 |", 'utf8')
			sleep(5)
		

		s.close()
	
#threading
tcpComm = tcp()
tcpCommThread = Thread(target=tcpComm.run)

serComm = serClass()
serCommThread = Thread(target=serComm.run)

#tcpCommThread.start()
serCommThread.start()