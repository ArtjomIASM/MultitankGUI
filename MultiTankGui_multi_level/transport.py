import traceback, sys
from socket import socket as Socket, error as SocketError, AF_INET, SOCK_DGRAM
from threading import Thread, Event, Lock
from struct import unpack, pack_into
from sys import exc_info
from config import *

ITEM_SIZE_IN_BYTES = 8
SENSORS_CALIBRATED_VAR = 100

class Transport:
    def __init__(self, nDataItemsCount):
        self.receiverStopped = Event() # Create event
        self.receiverStopped.set() # Set event up
        self.cbkLock = Lock()


        self.threadKill = Event()

        self.socketIN = None
        self.socketOUT = None

        self.nDataItemsCount = nDataItemsCount
        self.mapReceivedCbk = {}

    def registerCallback(self, cbkOwner, cbk):
        self.cbkLock.acquire(True)
        try:
            self.mapReceivedCbk[cbkOwner] = cbk
        finally:
            self.cbkLock.release()

    def unRegisterCallback(self, cbkOwner):
        self.cbkLock.acquire(True)
        try:
            self.mapReceivedCbk.pop(cbkOwner, None)
        finally:
            self.cbkLock.release()

    def doConnect(self, client, server):
        bRet = False
        try:
            self.socketOUT = Socket(AF_INET, SOCK_DGRAM)
            self.socketOUT.connect(server)

            self.socketIN = Socket(AF_INET, SOCK_DGRAM)
            self.socketIN.bind(client)

            bRet = True

            self.threadKill.clear()
            receiver = Thread(target = self.receiverMain, args = (self,))
            receiver.daemon = True
            receiver.setName("RecvThread")
            receiver.start()
        except SocketError:
            pass
        return bRet

    def doSend(self, lstValues):
        nSent = 0
        if None != self.socketOUT:
            packetData = bytearray(lstValues.__len__() * ITEM_SIZE_IN_BYTES)
            nOffset = 0
            for strValue in lstValues:
                print "Sending Value:" + str(strValue)
                pack_into('>d', packetData, nOffset, float(strValue))
                nOffset += ITEM_SIZE_IN_BYTES
            nSent = self.socketOUT.send(packetData)

        return nSent

    def doDisconnect(self):
        self.threadKill.set()
        while not self.receiverStopped.wait(1):
            pass
        bRet = False
        if None != self.socketOUT:
            self.socketOUT.close()
            self.socketOUT = None
            bRet = True
        if None != self.socketIN:
            self.socketIN.close()
            self.socketIN = None
            bRet = True
        return bRet

    def flushSocket(self):
        while 1:
            try:
                PacketBytes = self.socketIN.recv(ITEM_SIZE_IN_BYTES * self.nDataItemsCount * 10)
            except:
                break

    def receiverMain(self, kwArgs): # Data exchange and make send and receive for PID
        self.receiverStopped.clear()
        self.socketIN.setblocking(0)

        while not self.threadKill.wait(1.0 / MAX_FRAMES_PER_SEC_TO_RECEIVE):
            if None != self.socketIN:
                nBufferLen = ITEM_SIZE_IN_BYTES * self.nDataItemsCount
                buffer = bytearray(nBufferLen)
                try:
                    # Try to read date from socket to buffer
                    lstServerData = []
                    self.socketIN.recv_into(buffer, nBufferLen)
                    # Remove all data waiting in the socket, since server can send data more frequently than we read it
                    self.flushSocket()

                    # Unpacking data from buffer and adding data in lstServerData
                    for i in range(self.nDataItemsCount):
                        dataItem = unpack('>d', buffer[i * ITEM_SIZE_IN_BYTES: (i + 1) * ITEM_SIZE_IN_BYTES])
                        lstServerData.append(dataItem[0] * SENSORS_CALIBRATED_VAR) # REMOVE WHEN ACTUATORS CALIBRATED  * 100

                    # Notify UI
                    self.cbkLock.acquire(True)
                    try:
                        for cbk in self.mapReceivedCbk.values():
                            try:
                                cbk(lstServerData)
                            except:
                                print "Failed to execute callback!"
                                traceback.print_exc(file=sys.stdout)
                    finally:
                        self.cbkLock.release()
                except SocketError as e:
                    pass
        self.receiverStopped.set()
