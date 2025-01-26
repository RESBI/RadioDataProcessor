#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    A script reading readouts from the Dish in Calvin U.
    Goal: Read data stored in [prefix]_[index].txt, then make a plot for each index, then store those plots as [prefix]_plot_[index].png
    2025/01/25 Resbi & RJGamesAhoy
"""

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


if __name__ == "__main__": 
    data = np.array([1])
    index = 1
    prefix = input("Please input file prefix ([prefix]_xxxx.txt): ")
    time_begin = time.time()

    while (index): 
        # data = [header, [f1, p1], [f2, p2], ...]
        file_name = "{}_{:04d}.txt".format(prefix, index)
        read_out = readOne(file_name, debug = 1) 
        
        if (len(read_out)): 
            header, data = read_out
            #data = filtOut(data, 0.05, debug = 1) Originally used to filter out random noise spike at 1419.999876MHZ
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
            print("[main] Process finished!")
            index = -1
        
        index += 1

    time_end = time.time() 
    print("[main] Cost {} seconds.".format(time_end - time_begin))
