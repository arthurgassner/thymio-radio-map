import pandas as pd 
import numpy as np
import shutil
import click 
import json
from os import listdir 
from os.path import join, isfile 

CE_FOLDERNAME = 'ce'
CE_FILENAME = 'ce'

ELSE_FOLDERNAME = 'else'
ELSE_FILENAME = 'else'

INFO_FOLDERNAME = 'info'
INFO_FILENAME = 'info'

LOCATIONS_FILENAME = 'locations'

STOP_SYMBOL = 123
N_RECORDING_PER_SECOND = 1000
N_SUBCARRIERS = 400

@click.command()
@click.option('--src_folderpath', prompt='Folder where the ce, else and info folder are located', default='')
@click.option('--force', '-f', is_flag=True, help='Whether to reclean already cleaned files')
def clean_fingerprints(src_folderpath, force):
    """Load all the fingerprints referenced in {LOCATIONS_FILENAME}.json
    If --force is True, clean all the files from all the fingerprints
    Else, only clean the files that do not have a "clean" version already

    Save the cleaned files as
        - .parquet for ce.txt 
        - .pkl for else.txt and info.txt

    Arguments:
        src_folderpath {str} -- Source folder where the CE_FOLDERNAME, ELSE_FOLDERNAME and INFO_FOLDERNAME folder are located
    """

    src_ce_folderpath = join(src_folderpath, CE_FOLDERNAME)
    src_else_folderpath = join(src_folderpath, ELSE_FOLDERNAME)
    src_info_folderpath = join(src_folderpath, INFO_FOLDERNAME)

    # Load fingerprint IDs
    fingerprint_ids = load_fingerprint_ids(src_folderpath, LOCATIONS_FILENAME)

    if not force:
        cleaned_fingerprint_ids = get_cleaned_fingerprint_ids(src_ce_folderpath, src_else_folderpath, src_info_folderpath) # get IDs of the fingerprints that already have all three files cleaned
        fingerprint_ids = sorted(list(set(fingerprint_ids) - set(cleaned_fingerprint_ids)))

    print('')
    print('Cleaning {} fingerprints\n'.format(len(fingerprint_ids)))

    for fingerprint_id in fingerprint_ids:
        print('- Clean fingerprint #{}'.format(fingerprint_id))

        # Clean and save ce_{id}_raw.txt
        src_ce_filename = '{}_{}_raw.txt'.format(CE_FILENAME, fingerprint_id)
        dest_ce_filename = '{}_{}.parquet'.format(CE_FILENAME, fingerprint_id)

        src_ce_filepath = join(src_ce_folderpath, src_ce_filename)
        dest_ce_filepath = join(src_ce_folderpath, dest_ce_filename)

        print('\t {} -> '.format(src_ce_filename), end='')
        ce_df = clean_ce(ce_filepath=src_ce_filepath) # Clean ce_id_raw.txt
        ce_df.to_parquet(dest_ce_filepath, index=False, compression='gzip')
        print(dest_ce_filename)

        
        # Clean and save else_{id}_raw.txt
        src_else_filename = '{}_{}_raw.txt'.format(ELSE_FILENAME, fingerprint_id)
        dest_else_filename = '{}_{}.pkl'.format(ELSE_FILENAME, fingerprint_id)

        src_else_filepath = join(src_else_folderpath, src_else_filename)
        dest_else_filepath = join(src_else_folderpath, dest_else_filename)

        print('\t {} -> '.format(src_else_filename), end='')
        else_df = clean_else(else_filepath=src_else_filepath) # Clean else_id_raw.txt
        else_df.to_pickle(dest_else_filepath)
        print(dest_else_filename)


        # Clean and save info_{id}_raw.txt
        src_info_filename = '{}_{}_raw.txt'.format(INFO_FILENAME, fingerprint_id)
        dest_info_filename = '{}_{}.pkl'.format(INFO_FILENAME, fingerprint_id)

        src_info_filepath = join(src_info_folderpath, src_info_filename)
        dest_info_filepath = join(src_info_folderpath, dest_info_filename)

        print('\t {} -> '.format(src_info_filename), end='')
        info_df = clean_info(info_filepath=src_info_filepath) # Clean info_id_raw.txt
        info_df.to_pickle(dest_info_filepath)
        print(dest_info_filename, '\n')


def load_fingerprint_ids(src_folderpath, location_filename):
    """Load the fingerprint IDs located in src_folderpath/location_filename.JSON

    Arguments:
        src_folderpath {str} -- Path to the folder holding the location_filename
        location_filename {str} -- Name of the JSON file holding the "Fingerprint ID" -> [x,y] mapping

    Returns:
        fingerprint_ids [list] -- Sorted (ascending) list of the fingerprint IDs located in src_folderpath/location_filename.JSON
    """

    locations_filepath = join(src_folderpath, '{}.json'.format(LOCATIONS_FILENAME))
    fingerprint_ids = []
    
    with open(locations_filepath, 'r') as fp:
        locations = json.load(fp)
        fingerprint_ids = sorted(list(locations.keys()))

    return fingerprint_ids


def get_cleaned_fingerprint_ids(ce_folderpath, else_folderpath, info_folderpath):
    """Return the fingerprints IDs of the fingerprints that have all three files cleaned (ce, else and info)

    Arguments:
        ce_folderpath {str} -- Path to the folder holding the cleaned ce files (.parquet)
        else_folderpath {str} -- Path to the folder holding the cleaned else files (.pkl)
        info_folderpath {str} -- Path to the folder holding the cleaned info files (.pkl)

    Returns:
        [list] -- [Fingerprints IDs of the fingerprints that have all three files cleaned (ce, else and info)]
    """
    cleaned_ce_files = [f.split('.')[0] for f in listdir(ce_folderpath) if f.split('.')[-1] == 'parquet'] # list all .parquet file in ce_folderpath
    cleaned_ce_fingerprint_ids = [f.split('_')[-1] for f in cleaned_ce_files] # extract fingerprint ID from .parquet filename (e.g ce_123 --> 123)

    cleaned_else_files = [f.split('.')[0] for f in listdir(else_folderpath) if f.split('.')[-1] == 'pkl'] # list all .pkl file in else_folderpath
    cleaned_else_fingerprint_ids = [f.split('_')[-1] for f in cleaned_else_files] # extract fingerprint ID from .parquet filename (e.g else_123 --> 123)
    
    cleaned_info_files = [f.split('.')[0] for f in listdir(info_folderpath) if f.split('.')[-1] == 'pkl'] # list all .pkl file in info_folderpath
    cleaned_info_fingerprint_ids = [f.split('_')[-1] for f in cleaned_info_files] # extract fingerprint ID from .parquet filename (e.g info_123 --> 123)

    return list(set(cleaned_ce_fingerprint_ids).intersection(set(cleaned_else_fingerprint_ids)).intersection(set(cleaned_info_fingerprint_ids)))


def clean_ce(ce_filepath):
    ce_dt = np.dtype([('TTI', np.float32), ('SC_ID', np.float32),
               ('CE_0_AMPLITUDE', np.float32), ('CE_0_PHASE', np.float32), 
               ('CE_1_AMPLITUDE', np.float32), ('CE_1_PHASE', np.float32), 
               ('CE_2_AMPLITUDE', np.float32), ('CE_2_PHASE', np.float32), 
               ('CE_3_AMPLITUDE', np.float32), ('CE_3_PHASE', np.float32),
               ('STOP', np.float32)])

    ce_data = np.fromfile(ce_filepath, dtype=ce_dt)
    ce_df = pd.DataFrame(ce_data)

    # Clean the dataset because of recording errors
    ce_data_1d = ce_df.values.reshape((-1,))

    n_rows = (ce_data_1d == STOP_SYMBOL).sum() # 1 row per occurence of STOP_SYMBOL
    cleaned_ce_data = np.full((n_rows, ce_df.shape[1] - 1), fill_value=np.nan) # minus 1 since we discard the STOP column

    row_idx = 0
    column_idx = 0
    for i, e in enumerate(ce_data_1d):
        column_idx += 1
        if e == STOP_SYMBOL:
            if column_idx == 11:
                cleaned_ce_data[row_idx, :] = ce_data_1d[i-10:i]
                row_idx += 1
            column_idx = 0

    clean_ce_df = pd.DataFrame(cleaned_ce_data, columns=ce_dt.names[:-1]).dropna()

    # Convert to appropriate types
    for column in ['TTI', 'SC_ID']:
        clean_ce_df[column] = clean_ce_df[column].astype(np.int64)

    return clean_ce_df


def clean_else(else_filepath):
    else_dt = np.dtype([('TTI', np.float32), ('NOISE_ESTIMATE_DBM', np.float32),
               ('SNR_DB', np.float32), ('SNR_DB_0', np.float32), ('SNR_DB_1', np.float32), ('SNR_DB_2', np.float32), ('SNR_DB_3', np.float32), 
               ('RSRP_DBM', np.float32), ('RSRP_NEIGH', np.float32), ('RSRP_DBM_0', np.float32), ('RSRP_DBM_1', np.float32), ('RSRP_DBM_2', np.float32), ('RSRP_DBM_3', np.float32),
               ('RSRQ_DB', np.float32), ('RSRQ_DB_0', np.float32), ('RSRQ_DB_1', np.float32), ('RSRQ_DB_2', np.float32), ('RSRQ_DB_3', np.float32), 
               ('RSSI_DBM', np.float32), ('CFO', np.float32), ('SYNC_ERROR', np.float32)])
    
    else_data = np.fromfile(else_filepath, dtype=else_dt)
    else_df = pd.DataFrame(else_data)

    for column in ['TTI']:
        else_df[column] = else_df[column].astype(np.int64)

    else_df['TTI'] /= 1e3 # Convert TTI to seconds

    return else_df 


def clean_info(info_filepath):
    info_dt = np.dtype([('PCI', np.float32), 
                    ('NOF_PRB', np.float32), 
                    ('NOF_PORTS', np.float32), 
                    ('NOF_RX_ANTENNAS', np.float32),
                    ('TTI', np.float32)])
    
    info_data = np.fromfile(info_filepath, dtype=info_dt)
    info_df = pd.DataFrame(info_data)

    for column in ['PCI', 'NOF_PRB', 'NOF_PORTS', 'NOF_RX_ANTENNAS', 'TTI']:
        info_df[column] = info_df[column].astype(np.int64)

    return info_df


if __name__ == '__main__':
    clean_fingerprints() # pylint: disable=no-value-for-parameter