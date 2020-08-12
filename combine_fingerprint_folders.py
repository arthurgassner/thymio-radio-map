import pandas as pd 
import numpy as np
import shutil
import click 
import json
from os import listdir, mkdir, rename
from os.path import join, isfile, isdir
import glob

CE_FOLDERNAME = 'ce'
CE_FILENAME_PREFIX = 'ce'

ELSE_FOLDERNAME = 'else'
ELSE_FILENAME_PREFIX = 'else'

INFO_FOLDERNAME = 'info'
INFO_FILENAME_PREFIX = 'info'

CE_TEMP_FILENAME = 'ce_temp.parquet'
ELSE_TEMP_FILENAME = 'else_temp.pkl'
INFO_TEMP_FILENAME = 'info_temp.pkl'

LOCATIONS_FILENAME = 'locations'

@click.command()
@click.option('--src_folderpath', prompt='Folder where the folders to combine (i.e. the ones holding the ce folder) are located', default='')
@click.option('--dest_folderpath', prompt='Name of the folder to hold the combined data', default='')
def combine_fingerprint_folders(src_folderpath, dest_folderpath):
    """Combine several folders (contained in src_folderpath) of the shape:

        src_folderpath/
            fingerprint_folder_0/
                ce/
                else/
                info/
                locations.JSON
            fingerprint_folder_1/
                ce/
                else/
                info/
                locations.JSON

    into 
    
        dest_folderpath/
            ce/
            else/
            info/
            locations.JSON

    The ce_*.parquet, else_*.pkl and info_*.pkl files are renamed to have the shape *_{UNIQUE_FINGEPRINT_ID}.*

    Arguments:
        src_folderpath {str} -- Folder where the folders to combine (i.e. the ones holding the ce folder) are located
        dest_folderpath {str} -- Destination folder
    """

    fingerprint_folders = sorted(listdir(src_folderpath))

    # Folderpath where to store the fingerprints
    dest_ce_folderpath = join(dest_folderpath, CE_FOLDERNAME)
    dest_else_folderpath = join(dest_folderpath, ELSE_FOLDERNAME)
    dest_info_folderpath = join(dest_folderpath, INFO_FOLDERNAME)

    # Ensure dest_folderpath exists
    if not isdir(dest_folderpath):
        mkdir(dest_folderpath)
    if not isdir(dest_ce_folderpath):
        mkdir(dest_ce_folderpath)
    if not isdir(dest_else_folderpath):
        mkdir(dest_else_folderpath)
    if not isdir(dest_info_folderpath):
        mkdir(dest_info_folderpath)

    print('')
    print(f'- Combine {len(fingerprint_folders)} fingerprint folders')
    print('')

    all_locations = {}
    new_fingerprint_id = 0
    for fingerprint_folder in fingerprint_folders:
        print('\tFingerprint folder:', fingerprint_folder)
        
        fingerprint_folderpath = join(src_folderpath, fingerprint_folder)

        # Load the locations.JSON associated with this fingerprint_folder
        locations = load_locations(fingerprint_folderpath, LOCATIONS_FILENAME)
        print(f'\t\t {len(locations)} RPs found in locations.JSON')

        ce_folderpath = join(fingerprint_folderpath, CE_FOLDERNAME)
        else_folderpath = join(fingerprint_folderpath, ELSE_FOLDERNAME)
        info_folderpath = join(fingerprint_folderpath, INFO_FOLDERNAME)

        # Get a list of the .parquet file in fingerprint_folder/ce/
        fingerprint_ids = list_fingerprint_ids(ce_folderpath)
        print(f'\t\t {len(fingerprint_ids)} .parquet files found in ce/\n')

        for fingerprint_id in fingerprint_ids:

            handle_fingerprint(fingerprint_id, new_fingerprint_id, ce_folderpath, else_folderpath, info_folderpath, dest_ce_folderpath, dest_else_folderpath, dest_info_folderpath)

            # Save its (new_fingerprint_id, [x,y]) pair
            all_locations[str(new_fingerprint_id)] = locations[str(fingerprint_id)]

            new_fingerprint_id += 1

    # Save the new locations.json
    with open(join(dest_folderpath, f'{LOCATIONS_FILENAME}.json'), 'w') as fp:
        json.dump(all_locations, fp)

def load_locations(src_folderpath, location_filename):
    """Load the fingerprint IDs located in src_folderpath/location_filename.JSON

    Arguments:
        src_folderpath {str} -- Path to the folder holding the location_filename
        location_filename {str} -- Name of the JSON file holding the "Fingerprint ID" -> [x,y] mapping

    Returns:
        locations [dict] -- Dict stored in src_folderpath/location_filename.JSON. The fingerprint IDs are key, and the [x,y] coordinates are values.
    """

    locations_filepath = join(src_folderpath, '{}.json'.format(location_filename))
    locations = []

    with open(locations_filepath, 'r') as fp:
        locations = json.load(fp)

    return locations

def list_fingerprint_ids(src_folderpath):
    '''List the fingerprint IDs of all the .parquet files in src_folderpath
    '''

    filepaths = sorted(glob.glob(join(src_folderpath, "*.parquet")))
    filenames = [path.split('/')[-1] for path in filepaths] # only keep the filenames

    # order the filenames by ascending fingerprint ID's
    fingerprint_ids = [int(f.split('.')[0].split('_')[-1]) for f in filenames]

    return sorted(fingerprint_ids)

def handle_fingerprint(fingerprint_id, new_fingerprint_id, ce_folderpath, else_folderpath, info_folderpath, dest_ce_folderpath, dest_else_folderpath, dest_info_folderpath):
    """Handle the fingerprint with the ID {fingerprint_id}.

    That is, copy the files related to that fingerprint_id (ce.parquet, else.pkl and info.pkl)
    Then, rename them so that they have the ID {new_fingerprint_id}

    Args:
        fingerprint_id (int): ID of the fingerprint to handle
        new_fingerprint_id (int): New ID given to the handled fingerprint
        ce_folderpath ([type]): [description]
        else_folderpath ([type]): [description]
        info_folderpath ([type]): [description]
        dest_ce_folderpath ([type]): [description]
        dest_else_folderpath ([type]): [description]
        dest_info_folderpath ([type]): [description]
    """

    src_folderpaths = [ce_folderpath, else_folderpath, info_folderpath]
    dest_folderpaths = [dest_ce_folderpath, dest_else_folderpath, dest_info_folderpath]

    ce_filename = f'{CE_FILENAME_PREFIX}_{fingerprint_id}.parquet' 
    else_filename = f'{ELSE_FILENAME_PREFIX}_{fingerprint_id}.pkl' 
    info_filename = f'{INFO_FILENAME_PREFIX}_{fingerprint_id}.pkl' 
    filenames = [ce_filename, else_filename, info_filename]

    new_ce_filename = f'{CE_FILENAME_PREFIX}_{new_fingerprint_id}.parquet' 
    new_else_filename = f'{ELSE_FILENAME_PREFIX}_{new_fingerprint_id}.pkl' 
    new_info_filename = f'{INFO_FILENAME_PREFIX}_{new_fingerprint_id}.pkl' 
    new_filenames = [new_ce_filename, new_else_filename, new_info_filename]
    
    # Copy and rename the files 
    for filename, new_filename, temp_filename, folderpath, dest_folderpath in zip(filenames, new_filenames, [CE_TEMP_FILENAME, ELSE_TEMP_FILENAME, INFO_TEMP_FILENAME], src_folderpaths, dest_folderpaths):
        src_filepath = join(folderpath, filename)
        dest_temp_filepath = join(dest_folderpath, temp_filename) # temporary filepath before renaming the file
        dest_filepath = join(dest_folderpath, new_filename)

        shutil.copy(src_filepath, dest_temp_filepath)
        rename(dest_temp_filepath, dest_filepath)

if __name__ == '__main__':
    combine_fingerprint_folders() # pylint: disable=no-value-for-parameter