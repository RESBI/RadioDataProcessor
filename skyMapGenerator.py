"""
    Script that generates sky-maps from cartes du ciel
    uses time from the radio data to create the sky-maps
    will help to narrow down the location that the telescope is pointing at any one time.

    WORK IN PROGRESS... ALMOST THERE.
"""

import os
import sys
import socket 
import platform


class skyChartGenerator():
    def __init__(self):
        HOMEDIR = os.environ["HOME"]
        match(platform.system()):
            # Sets the location to find the TCP Port from the Cartes Du Ciel server based on system currently used
            case "Windows":
                tcpPortLocation = open("HKCU\Software\Astro_PC\Ciel\Status\TcpPort",'r')
            case "Linux":
                tcpPortLocation = open(HOMEDIR+'/.skychart/tmp/tcpport','r')
            case "Darwin":
                tcpPortLocation = open(HOMEDIR+'/.skychart/tmp/tcpport','r')
        
        self.PHOTOLOCATION = (HOMEDIR+'./skychart/tmp')
    
        self.HOST = 'localhost'

        self.PORT = int(tcpPortLocation.read())

        print(self.PORT)
        if self.PORT == 0:
            pass
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connect()

    # function to clear the receive buffer
    def purgeRecieveBuffer(self):
        self.s.setblocking(0)
        resp = '.\r\n'
        while resp != '':
            try:
                resp = self.s.recv(1024)
            except:
                resp = ''
        self.s.setblocking(1)
        return resp

    # function to send a command and wait for the response

    # \r\n must be sent after every command.
    # commands must be in ASCII formatting before being sent.

    def sendCommand(self, cmd, prterr=True):
        self.purgeRecieveBuffer()
        self.s.setblocking(1)
        formattedCommand = str(cmd)+'\r\n'
        self.s.send(formattedCommand.encode('ascii'))
        data = ''
        resp = '.\r\n'
        while True:
            resp = str(self.s.recv(1024))
            data = data + resp
            if ("OK!" in resp )or("Failed!" in resp):
                break
        if (prterr)and("OK!" not in resp) :
            print(cmd + ' ' + data)
        return data

    def connect(self):
        self.s.connect((self.HOST, self.PORT))
        data = self.s.recv(1024)
        print (data) 

    def generateChart(self, dateTime, fileName, fov = 360):

        ##TODO Add parsing of DateTime into set commands for the SkyChart Server, so that the time can be precisely set.
        ##TODO Add movement of the files to a directory in the head directory of RDP, so they can have matching file names to the others.
        self.sendCommand('SETFOV ' + str(fov))
        self.sendCommand('CLEANUPMAP')
        self.sendCommand('SAVEIMG PNG ' + fileName)
        return
    
    def timeParser(self):
        pass    

def test():
    print("This is in TESTING MODE.")
    test = skyChartGenerator()
    test.generateChart(10, "TESTING2", 330)
    return

if __name__ == "__main__":
    test()


