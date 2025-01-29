#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    A script reading readouts from the Dish in Calvin U.
    Goal: Read data stored in [prefix]_[index].txt, then make a plot for each index, then store those plots as [prefix]_plot_[index].png
    2025/01/25 Resbi & RJGamesAhoy
"""


import multiprocessing
import matplotlib

if __name__ == "__main__":
    # use Agg backend for non-interactive plotting
    matplotlib.use('Agg')  # Must come before pyplot import

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import time
import argparse 


MESSAGE = """
                                RadioDataProcessor(RDP) 

  RDP is a set of scripts that processing readouts from the IFAverage plugin for SDR# 
as used by the radio telescope located at Calvin University. 

  The goal is to read data stored in [prefix]_[index].txt, 
then make a plot for each index, then store those plots as [prefix]_plot_[index].png 

  Besides of being a standalone script, we want to provide a light library for processing
readouts from the IFAverage plugin, such that one could customize their processing codes. 

  2025/01/25 Resbi & RJGamesAhoy\n"""

HELP = """-h/--help is a todo ^_^ ."""

# Initialize those constants. 
NUM_MP_PROCESS = 8
DEBUG = 0


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


def readOne(file_name, debug = 0): 
    data = []
        
    if debug:
        print("[readOne] Trying to read {} ...".format(file_name)) 
    
    try: 
        file_open = open(file_name, "r") 
        file_content = file_open.read() 
        file_open.close() 
        header, data = readData(file_content, debug = debug) 
        result = [
            header, 
            sortData(np.array(data).transpose())
        ]
    except:
        print("[readOne] Failed on reading {} ...".format(file_name)) 
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
                 file_name = "", 
                 unit_x = ["frequency", "MHz"], 
                 unit_y = ["power", "dB"], 
                 debug = 0): 
        self.file_name = file_name
        
        if (len(file_name)): 
            self.header, self.data = readOne(file_name, debug = debug)
        else: 
            self.header = []
            self.data = np.array([])

        self.unit_x = unit_x 
        self.unit_y = unit_y 
        self.debug = debug

    def ReadData(self, 
                 file_name): 
        self.data = readOne(file_name, debug = self.debug) 

    def UnitConvert(self, 
                    xORy = "x"): 
        match xORy: 
            case "x": 
                print("Unit convert is a todo ^_^ .")
            case "y": 
                print("Unit convert is a todo ^_^ .")



def plotPlot(file_item, debug = DEBUG):
    prefix, index, file_name = file_item 
    item = Data(file_name = file_name, 
                    debug = DEBUG)
        
    if (len(item.data)): 
        #print(item)
        # plot them
        print("[plotPlot] Saving: {}_plot_{}.png ...".format(prefix, index))
        plt.plot(item.data[0], item.data[1], linewidth = 0.5) 
        plt.xlabel("{} / {}".format(item.unit_x[0], item.unit_x[1]))
        plt.ylabel("{} / {}".format(item.unit_y[0], item.unit_y[1]))
        #plt.ylim([0.003, 0.03])
        plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%.6f'))
        plt.subplots_adjust(left = 0.2)
        plt.title(item.header[0])
        plt.savefig("{}_plot_{}.png".format(prefix, index), dpi = 300)
        plt.close()
    else: 
        print("[plotPlot] Failed: {} !".format(file_name))


# Besides of being our workout, this part is kind of like an example.
if __name__ == "__main__": 
    print(MESSAGE)

    data = np.array([1])
    file_list = []
    index = 1
    prefix = 0
    file_exist_flag = 1

    # Get args 
    arg_parser = argparse.ArgumentParser(description = HELP) 

    arg_parser.add_argument(
        "-p", "--prefix", 
        type = str,
        help = "Specify a prefix."
    ) 
    
    arg_parser.add_argument(
        "-t", 
        "--num_threads", 
        type = int, 
        help = "Specify total number of process to parallelize the process."
    ) 
    
    arg_parser.add_argument(
        "-d", 
        "--debug", 
        type = int, 
        help = "Set the program print debug info or not."
    )

    args = arg_parser.parse_args()

    if (args.prefix): 
        prefix = args.prefix 
        print("You've specified the prefix: {}".format(prefix)) 

    if (args.num_threads): 
        NUM_MP_PROCESS = args.num_threads 
        print("You've specified to run {} processes. ".format(NUM_MP_PROCESS)) 

    if (args.debug):
        DEBUG = args.debug 
        print("You've enable the program to show debug info. ")


    if (prefix == 0): 
        prefix = input("You haven't specified a prefix, please input file prefix ([prefix]_xxxx.txt): \n>")

    print("Please input latitude in format of degree, minute, second (e.g. 42d30m00s -> 42,30,00): ")
    latitude_raw = input(">")
    print("Please input longitude in format of degree, minute, second (e.g. 85d30m00s -> 85,30,00): ")
    longitude_raw = input(">")

    time_begin = time.time()

    # Search files... 
    while (file_exist_flag): 
        # data : [header, [f1, p1], [f2, p2], ...]
        file_name = "{}_{:04d}.txt".format(prefix, index)
        try: 
            file_try = open(file_name, "r") 
            file_try.close() 
        except:
            file_exist_flag = 0
            index -= 1
        
        if (file_exist_flag): 
            print("[main] Found: {} ...".format(file_name))
            file_list.append([prefix, index, file_name])

        index += 1

    print("[main] Found {} files in total.".format(index - 1))

    # Plot them
    print("[main] Begin to plot, paralleled in {} processes...".format(NUM_MP_PROCESS))
    with multiprocessing.Pool(NUM_MP_PROCESS) as p: 
        p.map(plotPlot, file_list)

    time_end = time.time() 
    print("[main] Cost {} seconds.".format(time_end - time_begin))
