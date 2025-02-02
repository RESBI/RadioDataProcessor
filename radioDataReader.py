import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


def sortData(data): 
    x = data[0] 
    y = data[1]
    sortted_index = np.argsort(x) 
    return [x[sortted_index], y[sortted_index]]


def readData(content, debug = 0): 
    content_stripped = content.strip("\n")
    content_splitted = content_stripped.split("\n")
    data_string = content_splitted[1:]
    data = [list(map(float, data_line.split("  "))) for data_line in data_string]
    header_splitted = content_splitted[0].split("  ")
    # header : [datastamp, # of averaged data]
    header = [
        header_splitted[0], 
        int(header_splitted[1].split("Counts:")[1])
    ]

    if debug: 
        print("[readData] Data header: {}".format(content_splitted[0]))
        #print("[readData] Data length: {}".format(len(data)))

    return [header, data]


def readOne(file_path, debug = 0): 
    data = []

    if debug:
        print("[readOne] Trying to read {} ...".format(file_path)) 
    
    try: 
        file_open = open(file_path, "r") 
        file_content = file_open.read() 
        file_open.close() 
        header, data = readData(file_content, debug = debug) 

        result = [
            header, 
            sortData(np.array(data).transpose())
        ]
    except:
        print("[readOne] Failed on reading {} ...".format(file_path)) 
        result = []

    if debug:
        print("[readOne] {} points in total!".format(len(data)))

    return result


def filtOut(data, bar, debug = 0): 
    data_filtted = []

    for data_line in data: 
        if data_line[1] < bar: 
            data_filtted.append(data_line) 
        elif debug:
            print("[filtOut] filtted data: {}".format(data_line))

    return np.array(data_filtted)


class Data:
    def __init__(self, 
                 file_path = "", 
                 unit_x = ["frequency", "MHz"], 
                 unit_y = ["power", "dB"], 
                 debug = 0): 

        self.file_path = file_path
        
        if (len(file_path)): 
            self.header, self.data = readOne(file_path, debug = debug)
        else: 
            self.header = []
            self.data = np.array([])

        self.unit_x = unit_x 
        self.unit_y = unit_y 
        self.debug = debug


    def ReadData(self, 
                 file_path): 
        self.data = readOne(file_path, debug = self.debug) 


    def UnitConvert(self, xORy="x"):
        match xORy:
            case "x":
                # Add conversion logic here
                print("X unit conversion placeholder")
            case "y":
                # Add conversion logic here 
                print("Y unit conversion placeholder")
            case _:  # Default case
                print("Invalid conversion target: {}".format(xORy))

if __name__ == "__main__":
    print("Testing script is a todo~")
