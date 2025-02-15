import argparse
import os

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


def createDirIfNotExists(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)
        print("Output directory created: %s" % directory)


if __name__ == '__main__':
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

    arguments = argumentParser.parse_args()

    counter = 1
    inputDirectory = arguments.input_directory
    outputDirectory = arguments.output_directory
    fileCount = len(os.listdir(inputDirectory)) / 2

    while counter <= fileCount:
        bothPathExists = False
        skychartPath = "%s/%s_%d.png" % (inputDirectory, arguments.prefix_skychart, counter)
        plotDataPath = "%s/%s_%d.png" % (inputDirectory, arguments.prefix_plot, counter)

        # Two if-statements for logging purposes.
        if os.path.exists(skychartPath):
            if os.path.exists(plotDataPath):
                bothPathExists = True
            else:
                print("%s does not exist!" % plotDataPath)
        else:
            print("%s does not exist!" % skychartPath)

        if bothPathExists:
            createDirIfNotExists(outputDirectory)
            with (Image.open(plotDataPath) as plot_data_image, Image.open(skychartPath) as sky_chart_image):
                width = plot_data_image.width + sky_chart_image.width
                height = max(plot_data_image.height, sky_chart_image.height)
                merged_image = Image.new("RGB", (width, height))
                merged_image.paste(plot_data_image)
                merged_image.paste(sky_chart_image, (plot_data_image.size[0], 0))
                new_image_path = "%s/plot_sky_merge_%d.jpeg" % (arguments.output_directory, counter)
                merged_image.save(new_image_path, "JPEG")
                print("Image created: %s" % new_image_path)

        counter += 1
