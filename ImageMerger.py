import argparse

from PIL import Image, ImageFile

"""
Script that merges images from two folders.
"""

# TODO: loop over directories and merge:
#   -> Test1_plot_1.png + Test1_skychart_1.png
#   -> Test1_plot_2.png + Test1_skychart_2.png

if __name__ == '__main__':
    argumentParser = argparse.ArgumentParser()
    argumentParser.add_argument(
        "--directory_radio_data",
        required=True,
        type=str
    )
    argumentParser.add_argument(
        "--directory_skychart",
        required=True,
        type=str
    )

    # FIX: raise OSError(msg) from e -> OSError: image file is truncated
    arguments = argumentParser.parse_args()

    ImageFile.LOAD_TRUNCATED_IMAGES = True
    with (Image.open(arguments.directory_radio_data) as radio_data_image, Image.open(arguments.directory_skychart) as sky_chart_image):
        width = radio_data_image.width + sky_chart_image.width
        height = max(radio_data_image.height, sky_chart_image.height)
        merged_image = Image.new("RGB", (width, height))
        merged_image.paste(radio_data_image)
        merged_image.paste(sky_chart_image, (radio_data_image.size[0], 0))
        merged_image.save("test_image_merged.jpeg", "JPEG")
