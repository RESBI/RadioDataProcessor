#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    A script reading readouts from the Dish in Calvin U.
    Goal: Read data stored in [prefix]_[index].txt, then make a plot for each index, then store those plots as [prefix]_plot_[index].png
    2025/01/25 Resbi & RJGamesAhoy
"""

# Here is our data reader.
from radioDataReader import *

import multiprocessing
import os

import matplotlib

# use Agg backend for non-interactive plotting
# makes 20% faster
matplotlib.use('Agg')  # Must come before pyplot import

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import time

MESSAGE = """
                                RadioDataProcessor(RDP) 

  RDP is a set of scripts that processing readouts from the IFAverage plugin for SDR# 
as used by the radio telescope located at Calvin University. 

  Our goal is to read data stored in [prefix]_[index].txt, 
then make a plot for each index, then store those plots as [prefix]_plot_[index].png 

  Besides of being a standalone script, we want to provide a light library for processing
readouts from the IFAverage plugin, such that one could customize their processing codes. 

  2025/01/25 Resbi & RJGamesAhoy\n"""

HELP = """You called help, then I'm here."""

# Initialize those constants. 
NUM_MP_PROCESS = 8
DEBUG = 0


# Besides of being our workout, this part is kind of like an example.
# Here begin our example.

# We independent this function to parallelize the process.
def plotPlot(config):
    file_item = config[0]
    chart_config = config[1]
    debug = config[2]

    prefix, index, file_path, input_dir, output_dir, file_name = file_item 
    item = Data(file_path = file_path, 
                    debug = debug)

    if (len(item.data)): 
        #print(item)
        # plot them
        output_file_name = "{}_plot_{}.png".format(prefix, index)
        output_file_path = "{}/{}".format(output_dir, output_file_name)

        print("[plotPlot] Saving: {} ...".format(output_file_path))
        plt.plot(item.data[0], item.data[1], linewidth = 0.5) 
        plt.xlabel("{} / {}".format(item.unit_x[0], item.unit_x[1]))
        plt.ylabel("{} / {}".format(item.unit_y[0], item.unit_y[1]))
        #plt.ylim([0.003, 0.03])
        plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%.6f'))
        plt.subplots_adjust(left = 0.2)
        plt.title(item.header[0])

        plt.savefig(output_file_path, dpi = 300)
        plt.close()

    else: 
        print("[plotPlot] Failed on {} \n\tNo data found !".format(file_path))


if __name__ == "__main__": 
    import configparser
    import argparse

    print(MESSAGE)

    data = np.array([1])
    config_list = []
    index = 1

    # Default config file.
    config_file = "./RDP.config"

    # Set them 0 for not specified.
    input_dir = 0
    output_dir = 0
    prefix = 0
    plot_enable = 1
    chart_enable = 0
    latitude_raw = 0
    longitude_raw = 0
    altitude_raw = 0

    file_exist_flag = 1

    # Get args 
    arg_parser = argparse.ArgumentParser(description = HELP) 

    arg_parser.add_argument(
        "-f",
        "--config_file", 
        type = str,
        help = "Specify a config file."
    )

    arg_parser.add_argument(
        "-p", 
        "--prefix", 
        type = str,
        help = "Specify a prefix."
    ) 

    arg_parser.add_argument(
        "-i",
        "--input_dir",
        type = str,
        help = "Specify the input directory. Default = ./Input"
    )
    
    arg_parser.add_argument(
        "-o",
        "--output_dir",
        type = str,
        help = "Specify the output directory. Default = ./Output"
    )

    arg_parser.add_argument(
        "-t", 
        "--num_threads", 
        type = str, 
        help = "Specify total number of process to parallelize the process."
    ) 
    
    arg_parser.add_argument(
        "-pe", 
        "--plot_enable", 
        type = str, 
        help = "Specify whether to enable the plot."
    )

    arg_parser.add_argument(
        "-ce", 
        "--chart_enable", 
        type = str, 
        help = "Specify whether to enable the chart."
    ) 

    arg_parser.add_argument(
        "-lat", 
        "--latitude", 
        type = str, 
        help = "Specify latitude of the telescope."
    ) 

    arg_parser.add_argument(
        "-lon", 
        "--longitude", 
        type = str, 
        help = "Specify longitude of the telescope."
    )

    arg_parser.add_argument(
        "-alt", 
        "--altitude", 
        type = str, 
        help = "Specify altitude of the telescope."
    )

    arg_parser.add_argument(
        "-d", 
        "--debug", 
        type = str, 
        help = "Set the program print debug info or not."
    )

    args = arg_parser.parse_args()

    if (args.config_file):
        config_file = args.config_file

    # Read config file first. 
    if (config_file):
        config_parser = configparser.ConfigParser()
        config_parser.read(config_file)
        
        for item_name in config_parser["RDP"]:
            # Uses match for better performance and readability.
            match item_name:
                case "input_dir": 
                    input_dir = config_parser["RDP"]["input_dir"]
                case "output_dir":
                    output_dir = config_parser["RDP"]["output_dir"]
                case "prefix":
                    prefix = config_parser["RDP"]["prefix"]
                case "num_threads":
                    NUM_MP_PROCESS = int(config_parser["RDP"]["num_threads"])
                case "debug":
                    DEBUG = int(config_parser["RDP"]["debug"])
                case "plot_enable":
                    plot_enable = int(config_parser["RDP"]["plot_enable"])
                case "chart_enable":
                    chart_enable = int(config_parser["RDP"]["chart_enable"])
                case "latitude":
                    latitude_raw = config_parser["RDP"]["latitude"]
                case "longitude":
                    longitude_raw = config_parser["RDP"]["longitude"]
                case "altitude":
                    altitude_raw = config_parser["RDP"]["altitude"]

    # Read args second.
    if (args.input_dir):
        input_dir = args.input_dir

    if (args.output_dir):
        output_dir = args.output_dir

    if (args.prefix): 
        prefix = args.prefix 

    if (args.num_threads): 
        NUM_MP_PROCESS = int(args.num_threads) 

    if (args.debug):
        DEBUG = int(args.debug) 

    if (args.plot_enable):
        plot_enable = int(args.plot_enable)

    if (args.chart_enable):
        chart_enable = int(args.chart_enable)

    if (args.latitude):
        latitude_raw = args.latitude

    if (args.longitude):
        longitude_raw = args.longitude

    if (args.altitude):
        altitude_raw = args.altitude

    # If not specified, ask for them.
    if (prefix == 0): 
        print("You haven't specified a prefix, please input file prefix ([prefix]_xxxx.txt): ")
        prefix = input(">")
    
    if (input_dir == 0):
        print("You haven't specified an data input directory, please input input directory: ")
        input_dir = input(">")

    if (output_dir == 0):
        print("You haven't specified an result output directory, please input output directory: ")
        output_dir = input(">")

    if (chart_enable):
        # Ask for location if skychart is enabled.
        if (latitude_raw == 0):    
            print("Please input latitude (e.g. +42d55m42s): ")
            latitude_raw = input(">")
            
        if (longitude_raw == 0):
            print("Please input longitude (e.g. +85d32m50s): ")
            longitude_raw = input(">")

        if (altitude_raw == 0):
            print("Please input altitude in format of meter (e.g. 790.0m -> 790.0): ")
            altitude_raw = input(">")

    print("Configurations:")
    print("\tInput directory: {}".format(input_dir))
    print("\tOutput directory: {}".format(output_dir))
    print("\tPrefix: {}".format(prefix))
    print("\tNumber of threads: {}".format(NUM_MP_PROCESS))
    print("\tShow debug info? {}".format("Yes" if DEBUG == 1 else "No"))
    print("\tGenerate plots? {}".format("Yes" if plot_enable == 1 else "No"))
    print("\tGenerate skychart? {}".format("Yes" if chart_enable == 1 else "No"))
    if (chart_enable):
        print("\tLatitude: {}".format(latitude_raw))
        print("\tLongitude: {}".format(longitude_raw))
        print("\tAltitude: {}".format(altitude_raw))

    
    if not os.path.exists(output_dir):
        print("[main] Output directory not found, creating...")
        os.mkdir(output_dir)

    time_begin = time.time()

    # Search sequentially for files... 
    while (file_exist_flag): 
        # data : [header, [f1, p1], [f2, p2], ...]
        file_name = "{}_{:04d}.txt".format(prefix, index)
        file_path = "{}/{}".format(input_dir, file_name)
        try: 
            file_try = open(file_path, "r") 

            file_try.close() 
        except:
            file_exist_flag = 0
            index -= 1
        
        if (file_exist_flag): 
            print("[main] Found: {} ...".format(file_path))
            config_list.append(
                [
                    [prefix, index, file_path, input_dir, output_dir, file_name], 
                    [chart_enable, latitude_raw, longitude_raw, altitude_raw], 
                    DEBUG
                ]
            )

        index += 1

    print("[main] Found {} files in total.".format(index - 1))

    if (plot_enable):
        # Plot them
        print("[main] Begin to plot, paralleled in {} processes...".format(NUM_MP_PROCESS))
        with multiprocessing.Pool(NUM_MP_PROCESS) as p: 
            p.map(plotPlot, config_list)

    if (chart_enable):
        from skyChartGenerator import skyChartGenerator
        print("[main] Begin to generate skychart...")
        skychart = skyChartGenerator()
        for config_item in config_list:
            file_item = config_item[0]
            chart_config = config_item[1]
            debug = config_item[2]

            prefix, index, file_path, input_dir, output_dir, file_name = file_item 

            item = Data(file_path = file_path, 
                            debug = debug)

            chart_file_name = "{}_chart_{}".format(prefix, index)
            chart_file_path = "{}/{}.png".format(output_dir, chart_file_name)

            print("[main] Generating chart: {}...".format(chart_file_path))
            chart_enable, latitude_raw, longitude_raw, altitude_raw = chart_config
            skychart.setObservatory(latitude_raw, longitude_raw, altitude_raw)
            skychart.setObservatory(latitude_raw, longitude_raw, altitude_raw)
            skychart.generateChart(item.header[0], chart_file_name, fov = 330, height = 1440, width = 1920, destination = chart_file_path)
    
    time_end = time.time() 
    print("[main] Cost {} seconds.".format(time_end - time_begin))
