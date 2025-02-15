"""
Script that merges images from a input folder.
Example folder structure:
    - /resources/output/Test1_chart_1.png
    - /resources/output/Test1_chart_2.png
    - /resources/output/Test1_plot_1.png
    - /resources/output/Test1_plot_2.png
Example command for script (if above is structure):
ImageMerger.py
  --input_directory=resources/output
  --output_directory=resources/output/merged
  --prefix_skychart=Test1_chart
  --prefix_plot=Test1_plot
"""

import argparse
import multiprocessing
import os
import time

from PIL import Image


def create_dir_if_not_exists(directory):
    """Simple function for checking if there is directory and else create it."""
    if not os.path.isdir(directory):
        os.mkdir(directory)
        print(f"Output directory created: {directory}")


def merge_image(task):
    """Function for merging images in multithreading environment."""
    both_paths_exists = False
    skychart_path = f'{task["input_dir"]}/{task["skychart_prefix"]}_{task["counter"]}.png'
    plot_data_path = f'{task["input_dir"]}/{task["plot_prefix"]}_{task["counter"]}.png'

    # Two if-statements for logging purposes.
    if os.path.exists(skychart_path):
        if os.path.exists(plot_data_path):
            both_paths_exists = True
        else:
            print(f"{plot_data_path} does not exist!")
    else:
        print(f"{skychart_path} does not exist!")

    if both_paths_exists:
        create_dir_if_not_exists(task["output_dir"])
        with (Image.open(plot_data_path) as plot_data_image,
              Image.open(skychart_path) as sky_chart_image):
            width = plot_data_image.width + sky_chart_image.width
            height = max(plot_data_image.height, sky_chart_image.height)
            merged_image = Image.new("RGB", (width, height))
            merged_image.paste(plot_data_image)
            merged_image.paste(sky_chart_image, (plot_data_image.size[0], 0))
            new_image_path = f'{task["output_dir"]}/plot_sky_merge_{task["counter"]}.jpeg'
            merged_image.save(new_image_path, "JPEG")
            print(f"Image created: {new_image_path}")


if __name__ == '__main__':
    startTime = time.time()
    argumentParser = argparse.ArgumentParser()
    argumentParser.add_argument(
        "--input_directory",
        required=True,
        type=str
    )
    argumentParser.add_argument(
        "--output_directory",
        required=True,
        type=str
    )
    argumentParser.add_argument(
        "--prefix_skychart",
        required=True,
        type=str
    )
    argumentParser.add_argument(
        "--prefix_plot",
        required=True,
        type=str
    )

    args = argumentParser.parse_args()
    input_directory = args.input_directory
    output_directory = args.output_directory
    skychart_prefix = args.prefix_skychart
    plot_prefix = args.prefix_plot

    if os.path.exists(input_directory):
        fileCount = len(os.listdir(input_directory)) / 2
    else:
        raise FileNotFoundError(f"Input directory \"{input_directory}\" does not exist.")

    multithreading_tasks = []
    counter = 1
    while counter <= fileCount:
        multithreading_tasks.append({"input_dir": input_directory,
                                     "output_dir": output_directory,
                                     "skychart_prefix": skychart_prefix,
                                     "plot_prefix": plot_prefix,
                                     "counter": counter})
        counter += 1

    with multiprocessing.Pool(8) as pool:
        pool.map(merge_image, multithreading_tasks)

    runTime = time.time() - startTime
    print(f"Time: {runTime // 60} minutes {runTime % 60} second")
