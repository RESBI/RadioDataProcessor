#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    A script reading readouts from the Dish in Calvin U.
    Goal: Read data stored in [prefix]_[index].txt, then make a plot for each index, then store those plots as [prefix]_plot_[index].png
    2025/01/25 Resbi & RJGamesAhoy
"""

import multiprocessing

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import time

def readData(content, debug = 0): 
    content_stripped = content.strip("\n")
    content_splitted = content_stripped.split("\n")
    data_string = content_splitted[1:]
    data = [list(map(float, data_line.split("  "))) for data_line in data_string]
    header_splitted = content_splitted[0].split("  ")
    header = [
        header_splitted[0], 
        int(header_splitted[1].split("Counts:")[1])
    ]

    if debug: 
        print("[readData] Data header: {}".format(content_splitted[0]))
        print("[readData] Data length: {}".format(len(data)))

    return [header, data]


def readOne(file_name, debug = 0): 
    data = []
        
    if debug:
        print("[readOne] Trying to read {} ...".format(file_name)) 
    
    try: 
        file_open = open(file_name, "r") 
        file_content = file_open.read() 
        file_open.close() 
        data_read = readData(file_content, debug = debug) 
        header, data = data_read
        result = [header, np.array(data)]
    except:
        print("[readOne] Failed to read {} ...".format(file_name)) 
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


def sortData(data): 
    x = data[0] 
    y = data[1]
    sortted_index = np.argsort(x) 
    return [x[sortted_index], y[sortted_index]]


def plotPlot(file, debug = 1):
    prefix, index, file_name = file
    read_out = readOne(file_name, debug = 1) 
        
    if (len(read_out)): 
        header, data = read_out
        #print(data)
        # Fuck those weird noices
        #data = filtOut(data, 0.05, debug = 1)
        data_T = data.transpose()
        #print(data_T)
        data_sortted = sortData(data_T)
        # plot them
        print("[main] Saving to figure {}_plot_{}.png ...".format(prefix, index))
        plt.plot(data_sortted[0], data_sortted[1], linewidth = 0.5) 
        plt.xlabel("frequency / MHz")
        plt.ylabel("power / dB")
        plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%.6f'))
        plt.subplots_adjust(left = 0.2)
        plt.title(header[0])
        plt.savefig("{}_plot_{}.png".format(prefix, index), dpi = 300)
        plt.close()
    else: 
        print("[plotPlot] Can't draw plot for {} !".format(file_name))


NUM_MP_PROCESS = 8

if __name__ == "__main__": 
    data = np.array([1])
    file_list = []
    index = 1
    file_exist_flag = 1
    prefix = input("Please input file prefix ([prefix]_xxxx.txt): ")
    time_begin = time.time()

    # Search files... 
    while (file_exist_flag): 
        # data = [header, [f1, p1], [f2, p2], ...]
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

    print("[main] Found {} files in total.".format(index))

    with multiprocessing.Pool(NUM_MP_PROCESS) as p: 
        p.map(plotPlot, file_list)

    time_end = time.time() 
    print("[main] Cost {} seconds.".format(time_end - time_begin))
