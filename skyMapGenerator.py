"""
    Script that generates sky-maps from cartes du ciel
    uses time from the radio data to create the sky-maps
    will help to narrow down the location that the telescope is pointing at any one time.

    WORK IN PROGRESS... ALMOST THERE.
"""

import os
import sys
import time
import socket 
import platform


class skyChartGenerator():
    def __init__(self):
        HOMEDIR = os.environ["HOME"]
        match(platform.system()):
            # Sets the location to find the TCP Port from the Cartes Du Ciel server based on system currently used
            case "Windows":
                tcpPortLocation = 2##open("HKCU\Software\Astro_PC\Ciel\Status\TcpPort",'r')
            case "Linux":
                tcpPortLocation = open(HOMEDIR+'/.skychart/tmp/tcpport','r')
            case "Darwin":
                print("Creating sky charts is not currently supported on MacOs")
                sys.exit(0)
        
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

    def sendCommandToServer(self, cmd, prterr=True):
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


def test():
    print("This is in TESTING MODE.")
    test = skyChartGenerator()
    test.sendCommandToServer('SETFOV 330')
    test.sendCommandToServer('REDRAW')
    test.sendCommandToServer('SETFOV 5')
    test.sendCommandToServer('CLEANUPMAP')
    test.sendCommandToServer('SJPG')
    test.sendCommandToServer('SHUTDOWN')
    return

if __name__ == "__main__":
    test()


