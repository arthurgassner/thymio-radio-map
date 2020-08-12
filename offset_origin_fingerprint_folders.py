import pandas as pd 
import numpy as np
import shutil
import click 
import json
from os import listdir, mkdir, rename
from os.path import join, isfile, isdir
import glob

LOCATIONS_FILENAME = 'locations'

@click.command()
@click.option('--src_folderpath', prompt='Folder holding the locations.json to offset', default='')
@click.option('--x_offset', prompt='Offset [cm] to add to the x-coordinates', default=0.0)
@click.option('--y_offset', prompt='Offset [cm] to add to the y-coordinates', default=0.0)
def offset_origin_locations(src_folderpath, x_offset, y_offset):
    """offset the origin of the locations.JSON

    Effectively adds an offset to the x and y coordinates of each positions.

    Arguments:
        src_folderpath {str} -- Folder holding the locations.json to offset
    """
    # Load the locations.json
    locations_filepath = join(src_folderpath, '{}.json'.format(LOCATIONS_FILENAME))
    locations = {}
    with open(locations_filepath, 'r') as fp:
        locations = json.load(fp)

    # Offset the x and y coordinates
    for k in locations.keys():
        locations[k][0] += x_offset
        locations[k][1] += y_offset

    # Save the new locations.json
    with open(locations_filepath, 'w') as fp:
        json.dump(locations, fp)


if __name__ == '__main__':
    offset_origin_locations() # pylint: disable=no-value-for-parameter