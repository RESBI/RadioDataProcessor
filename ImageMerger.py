import argparse
import multiprocessing
import os
import time

from PIL import Image

"""
Script that merges images from a input folder.

Example:

If folder structure:
    - /resources/output/Test1_chart_1.png
    - /resources/output/Test1_chart_2.png
    - /resources/output/Test1_plot_1.png
    - /resources/output/Test1_plot_2.png

Then command:

ImageMerger.py 
    --input_directory=resources/output
    --output_directory=resources/output/merged 
    --prefix_skychart=Test1_chart 
    --prefix_plot=Test1_plot 
"""


def create_dir_if_not_exists(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)
        print("Output directory created: %s" % directory)


def merge_image(task):
    both_paths_exists = False
    skychart_path = "%s/%s_%d.png" % (task["input_dir"], task["skychart_prefix"], task["counter"])
    plot_data_path = "%s/%s_%d.png" % (task["input_dir"], task["plot_prefix"], task["counter"])

    # Two if-statements for logging purposes.
    if os.path.exists(skychart_path):
        if os.path.exists(plot_data_path):
            both_paths_exists = True
        else:
            print("%s does not exist!" % plot_data_path)
    else:
        print("%s does not exist!" % skychart_path)

    if both_paths_exists:
        create_dir_if_not_exists(task["output_dir"])
        with (Image.open(plot_data_path) as plot_data_image, Image.open(skychart_path) as sky_chart_image):
            width = plot_data_image.width + sky_chart_image.width
            height = max(plot_data_image.height, sky_chart_image.height)
            merged_image = Image.new("RGB", (width, height))
            merged_image.paste(plot_data_image)
            merged_image.paste(sky_chart_image, (plot_data_image.size[0], 0))
            new_image_path = "%s/plot_sky_merge_%d.jpeg" % (task["output_dir"], task["counter"])
            merged_image.save(new_image_path, "JPEG")
            print("Image created: %s" % new_image_path)


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
        counter = 1
        fileCount = len(os.listdir(input_directory)) / 2
    else:
        raise Exception("Input directory \"%s\" does not exist." % input_directory)

    multithreading_tasks = []
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
    print("Time: %d minutes %d second" % (runTime // 60, runTime % 60))
