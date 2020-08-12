import pandas as pd 
import numpy as np
import shutil
import click 
import json
from os import listdir, mkdir, rename
from os.path import join, isfile, isdir
import glob

CE_FOLDERNAME = 'ce'
CE_FILENAME = 'ce'

ELSE_FOLDERNAME = 'else'
ELSE_FILENAME = 'else'

INFO_FOLDERNAME = 'info'
INFO_FILENAME = 'info'

CE_TEMP_FILENAME = 'ce_temp'
ELSE_TEMP_FILENAME = 'else_temp'
INFO_TEMP_FILENAME = 'info_temp'

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

    into one folder (dest_folderpath) with one locations.JSON

    Only the .parquet files located in the */ce/ folder are saved. They are renamed to have the shape ce_{UNIQUE_FINGEPRINT_ID}.parquet

    Arguments:
        src_folderpath {str} -- Folder where the folders to combine (i.e. the ones holding the ce folder) are located
    """

    fingerprint_folders = sorted(listdir(src_folderpath))

    # Ensure dest_folderpath exists
    if not isdir(dest_folderpath):
        mkdir(dest_folderpath)

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

        # Get a list of the .parquet file in fingerprint_folder/ce/
        ce_fingerprint_folderpath = join(fingerprint_folderpath, CE_FOLDERNAME)
        parquet_files = list_parquet_files(ce_fingerprint_folderpath)
        print(f'\t\t {len(parquet_files)} .parquet files found in ce/\n')

        for parquet_file in parquet_files:
            # Copy and rename the .parquet file
            src_filepath = join(ce_fingerprint_folderpath, parquet_file)
            dest_temp_filepath = join(dest_folderpath, f'{CE_TEMP_FILENAME}.parquet') # temporary filepath before renaming the file
            dest_filepath = join(dest_folderpath, f'ce_{new_fingerprint_id}.parquet')

            shutil.copy(src_filepath, dest_temp_filepath)
            rename(dest_temp_filepath, dest_filepath)

            # Save its (new_fingerprint_id, [x,y]) pair
            fingerprint_id = parquet_file.split('.')[0].split('_')[-1]
            all_locations[str(new_fingerprint_id)] = locations[fingerprint_id]

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

def list_parquet_files(src_folderpath):
    '''List the filenames (with the .parquet) of all the .parquet files in src_folder
    '''
    filepaths = sorted(glob.glob(join(src_folderpath, "*.parquet")))
    filenames = [path.split('/')[-1] for path in filepaths] # only keep the filenames

    # order the filenames by ascending fingerprint ID's
    fingerprint_ids = [int(f.split('.')[0].split('_')[-1]) for f in filenames]
    filenames = list(np.array(filenames)[np.argsort(fingerprint_ids)])

    return filenames


if __name__ == '__main__':
    combine_fingerprint_folders() # pylint: disable=no-value-for-parameter