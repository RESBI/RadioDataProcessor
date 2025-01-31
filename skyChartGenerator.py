"""
    Script that generates sky-maps from cartes du ciel
    uses time from the radio data to create the sky-maps
    will help to narrow down the location that the telescope is pointing at any one time.

    WORK IN PROGRESS... ALMOST THERE.
"""

import os
import socket 
import platform
import sys
import psutil
import shutil
import time

class skyChartGenerator():
    def __init__(self):

        match(platform.system()):
            # Sets the location to find the TCP Port from the Cartes Du Ciel server based on system currently used
            case "Windows":
                HOMEDIR = os.environ["USERPROFILE"]
                self.PHOTOLOCATION = (HOMEDIR + '/AppData/Local/skychart/tmp')
                self.PROCESSNAME = "skychart.exe"
            case "Linux":
                HOMEDIR = os.environ["HOME"]
                self.PHOTOLOCATION = (HOMEDIR + '/.skychart/tmp')
                self.PROCESSNAME = "skychart"

            case "Darwin":
                HOMEDIR = os.environ["HOME"]
                self.PHOTOLOCATION = (HOMEDIR + '/.skychart/tmp')
                self.PROCESSNAME = "skychart"

        # Read config file
        server_config = []
        config_file = open("skyMap.config", "r") 
        for line in config_file.readlines(): 
            server_config.append(line)
        config_file.close()
        # default = "localhost"
        self.HOST = server_config[0].strip("\n") 

        self.PORT = int(server_config[1])


        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


        if self.isSkyChartRunning() != True:
            print("Your SkyChart is not open. Please open it before using this feature.")
            print("EXITING.")
            sys.exit(0)
        try:
            self.connect()
        except:
            print("Your SkyChart server is offline. Check configuration to see if the server is set to a different port or is disabled.")
            print("EXITING.")
            sys.exit(0)

        # Default window size.
        self.setWindowSize(1440, 1920)

    def isSkyChartRunning(self):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == self.PROCESSNAME:
                return True
        return False

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
        # print (data) - Uncomment for Debug

    def generateChart(self, dateTime, fileName, destination = str(os.getcwd()) + '/Output/' + fileName + ".png", fov = 330, height = 1440, width = 1920):
        parsedTime = self.timeParser(dateTime)
        self.sendCommand(f'SETDATE {parsedTime}')
        self.sendCommand('SETFOV ' + str(fov))
        self.sendCommand('CLEANUPMAP')
        self.sendCommand(f'SAVEIMG PNG {fileName}')
        self.movePhotos(fileName, destination = destination)
        return
    
    def setWindowSize(self, height, width):
        # Height and Width in pixels
        self.sendCommand(f'RESIZE {width} {height}')
        self.sendCommand('CLEANUPMAP')
        return

    def setObservatory(self, latitude = "+42d55m42s", longitude="+85d32m50s", altitude="790", name = "United States - Michigan/Calvin_University"):
        # I have no explanation to why this requires two identical commands to actually change the name of the observatory.
        self.sendCommand(f'SETOBS LAT:{latitude}LON:{longitude}ALT:{altitude}mOBS:{name}')
        self.sendCommand('CLEANUPMAP')
        self.sendCommand(f'SETOBS LAT:{latitude}LON:{longitude}ALT:{altitude}mOBS:{name}')
        return
    
    def movePhotos(self, fileName, destination = str(os.getcwd()) + '/Output/' + fileName + ".png"):
        # Takes photos from the temp directory in skycharts files, and moves them to the folder that this script is being ran within
        source = self.PHOTOLOCATION + '/' + fileName + ".png"
        shutil.move(source, destination)
        return

    def timeParser(self, time):
        # SDR SHARP FORMAT - 1/25/2025 1:22:23 PM (Exmaple)
        # takes time from SDR# output, converts to format for skychart
        # Skychart format = YYYY-MM-DDTHH:MM:SS

        timeList = []

        notParsed = True
        selection = 0
        currentList = []

        while notParsed:
            currentCharacter = time[selection]
            if currentCharacter == 'P':
                timeList.append("PM")
                break
            elif currentCharacter == 'A':
                timeList.append("AM")
                break
            elif (currentCharacter != "/") & (currentCharacter != ":") & (currentCharacter != " "):
                currentList.append(currentCharacter)
            else:
                if len(timeList) == 2:
                    # Length required a change for the year value.
                    length = 4
                else:
                    length = 2
    
                if len(currentList) != length:
                    temp = currentList[0]
                    currentList[0] = '0'
                    currentList.append(temp)

                timeList.append(currentList)
                currentList = []
    
            selection += 1
        
        if timeList[6] == 'PM':
            # adjustments for AM/PM - > 24hr time
            if timeList[3] != ['1', '2']:
                timeList[3][0] = str(int(timeList[3][0]) + 1)
                timeList[3][1] = str(int(timeList[3][1]) + 2)
        elif timeList[6] == 'AM':
            if timeList[3] == ['1', '2']:
                timeList[3][0] = '0'
                timeList[3][1] = '0'
        
        timeList.pop(6)

        finalTime = ""

        # reshuffles order of date and time
        for daysUnit in [2, 0, 1]:
            for digit in timeList[daysUnit]:
                finalTime += digit
            if daysUnit != 1:
                finalTime += "-"
        finalTime += "T"
        for timeUnit in [3, 4, 5]:
            for digit in timeList[timeUnit]:
                finalTime += digit
            if timeUnit != 5:
                finalTime += ":"
        
        return finalTime
        
        

def test():
    print("This is in TESTING MODE.")
    time_start = time.time()
    test = skyChartGenerator()
    test.setObservatory()
    test.generateChart("1/25/2025 11:22:23 PM", "TESTING2", 330)
    time_end = time.time()
    print("[main] Cost {} seconds.".format(time_end - time_start))
    
    return

if __name__ == "__main__":
    test()


