import shutil
import click 
import os 
import json

CE_FOLDERNAME = 'ce'
CE_FILENAME = 'ce'

ELSE_FOLDERNAME = 'else'
ELSE_FILENAME = 'else'

INFO_FOLDERNAME = 'info'
INFO_FILENAME = 'info'

LOCATIONS_FILENAME = 'locations'

@click.command()
@click.option('--x', prompt='x-coordinate where the fingerprint was taken')
@click.option('--y', prompt='y-coordinate where the fingerprint was taken')
@click.option('--src_folderpath', default='../srsLTE-modified/srsue', help='Folderpath where the fingerprint files (ce.txt, else.txt, info.txt) are located')
@click.option('--dest_folderpath', default='dev', help='Folderpath where the ce, else and info folder will be located')
@click.option('--verbose', '-V', default=True)
def move_fingerprint_clickwrapper(x, y, src_folderpath, dest_folderpath, verbose):
    """ Wrapper for click functionality
    """
    move_fingerprint(x, y, src_folderpath, dest_folderpath, verbose)

def move_fingerprint(x, y, src_folderpath, dest_folderpath, verbose):
    """Move {CE_FILENAME}.txt, {ELSE_FILENAME}.txt and {INFO_FILENAME}.txt to dest_folderpath for safe-keeping.
    A unique ID is assigned to the three files (one ID per triplet of files).
    The mapping between the ID and the (x,y) coordinates is logged in the {LOCATIONS_FILENAME}.json file

    Arguments:
        x {float} -- x-coordinate where the fingerprint was taken
        y {float} -- y-coordinate where the fingerprint was taken
        src_folderpath {str} -- Folderpath where the fingerprint files (ce.txt, else.txt, info.txt) are located
        dest_folderpath {str} -- Folderpath where the ce, else and info folder will be located
        verbose {bool} -- Whether or not to enable printing
    """

    log('', verbose=verbose)
    log('Moving fingerprint located at ({}, {})\n'.format(x,y), verbose=verbose)

    log('- Ensure destination folder structure', verbose=verbose)
    ensure_dest_dir_structure(dest_folderpath, 
                            ce_foldername=CE_FOLDERNAME, 
                            else_foldername=ELSE_FOLDERNAME, 
                            info_foldername=INFO_FOLDERNAME, 
                            locations_filename=LOCATIONS_FILENAME,
                            verbose=verbose)
    fingerprint_id = get_fingerprint_id(dest_folderpath, LOCATIONS_FILENAME)
    log('', verbose=verbose)

    # Move {CE_FILENAME}.txt
    log('- Move {}.txt'.format(CE_FILENAME), verbose=verbose)
    src_ce_filename = '{}.txt'.format(CE_FILENAME)
    src_ce_filepath = os.path.join(src_folderpath, src_ce_filename)
    dest_ce_folderpath = os.path.join(dest_folderpath, 'ce')
    dest_ce_filepath = os.path.join(dest_ce_folderpath, '{}_{}_raw.txt'.format(CE_FILENAME, fingerprint_id))
    move(src_ce_filepath, dest_ce_filepath, verbose=verbose)


    # Move {ELSE_FILENAME}.txt
    log('- Move {}.txt'.format(ELSE_FILENAME), verbose=verbose)
    src_else_filename = '{}.txt'.format(ELSE_FILENAME)
    src_else_filepath = os.path.join(src_folderpath, src_else_filename)
    dest_else_filepath = os.path.join(dest_folderpath, 'else/{}_{}_raw.txt'.format(ELSE_FILENAME, fingerprint_id))
    move(src_else_filepath, dest_else_filepath, verbose=verbose)


    # Move {INFO_FILENAME}.txt
    log('- Move {}.txt'.format(INFO_FILENAME), verbose=verbose)
    src_info_filename = '{}.txt'.format(INFO_FILENAME)
    src_info_filepath = os.path.join(src_folderpath, src_info_filename)
    dest_info_filepath = os.path.join(dest_folderpath, 'info/{}_{}_raw.txt'.format(INFO_FILENAME, fingerprint_id))
    move(src_info_filepath, dest_info_filepath, verbose=verbose)


    # Add the saved fingerprint id to the {LOCATIONS_FILENAME}.json to keep track of its locations
    log('- Add {}: ({}, {}) to {}.json'.format(fingerprint_id, x, y, LOCATIONS_FILENAME), end='', verbose=verbose)
    locations = {}
    with open('{}/{}.json'.format(dest_folderpath, LOCATIONS_FILENAME), 'r') as fp:
        locations = json.load(fp)

    with open('{}/{}.json'.format(dest_folderpath, LOCATIONS_FILENAME), 'w') as fp:
        locations[fingerprint_id] = [float(x), float(y)]
        json.dump(locations, fp)

    log('\t Done\n', verbose=verbose)

def ensure_dest_dir_structure(dest_folderpath, ce_foldername, else_foldername, info_foldername, locations_filename, verbose):
    """Ensure that the destination directory has the following structure:
    dest_folderpath/
        ce_foldername/
        else_foldername/
        info_foldername/
        {locations_filename}.json

    If dest_folder is missing a directory or {locations_filename}.json, 
    then the missing directory/file is created

    Arguments:
        dest_folderpath {str} -- Folderpath to the destination folder
        ce_foldername {str} -- Name of the folder holding the ce data (i.e. channel estimate)
        else_foldername {str} -- Name of the folder holding the else data (i.e. RSRP, RSRQ, ...)
        info_foldername {str} -- Name of the folder holding the info data (i.e. PCI, ...)
        locations_filename {str} -- Name of the file holding the locations JSON data
    """
    # Ensure dest_folderpath exists
    if not os.path.isdir(dest_folderpath):

        os.mkdir(dest_folderpath)
        os.chmod(dest_folderpath, 0o777) # set folder permission 

    # Ensure ce_foldername exists
    dest_ce_folderpath = os.path.join(dest_folderpath, ce_foldername)
    if not os.path.isdir(dest_ce_folderpath):
        log('\t - {}/: '.format(dest_ce_folderpath), end='', verbose=verbose)
        os.mkdir(dest_ce_folderpath)
        os.chmod(dest_ce_folderpath, 0o777) # set folder permission 
        log('Created', verbose=verbose)

    # Ensure else_foldername exists
    dest_else_folderpath = os.path.join(dest_folderpath, else_foldername)
    if not os.path.isdir(dest_else_folderpath):
        log('\t - {}/: '.format(dest_else_folderpath), end='', verbose=verbose)
        os.mkdir(dest_else_folderpath)
        os.chmod(dest_else_folderpath, 0o777) # set folder permission 
        log('Created', verbose=verbose)

    # Ensure info_foldername exists
    dest_info_folderpath = os.path.join(dest_folderpath, info_foldername)
    if not os.path.isdir(dest_info_folderpath):
        log('\t - {}/: '.format(dest_info_folderpath), end='', verbose=verbose)
        os.mkdir(dest_info_folderpath)        
        os.chmod(dest_info_folderpath, 0o777) # set folder permission 
        log('Created', verbose=verbose)

    # Ensure {locations_filename}.json exists
    locations_filepath = os.path.join(dest_folderpath, '{}.json'.format(locations_filename))
    if not os.path.isfile(locations_filepath):
        log('\t - {}: '.format(locations_filepath), end='', verbose=verbose)
        locations = {}
        with open(locations_filepath, 'w') as fp:
            json.dump(locations, fp)
        log('Created', verbose=verbose)

def get_fingerprint_id(dest_folderpath, locations_filename):
    """Lookup the {locations_filename}.json to see which fingerprint ID is available.
    Starts with 0 and increment by 1

    Arguments:
        dest_folderpath {str} -- Folderpath to the destination folder
        locations_filename {str} -- Filename of the JSON file holding the locations data

    Returns:
        fingerprint_id {int} -- Unique ID linked to a fingerprint
    """
    with open('{}/{}.json'.format(dest_folderpath, locations_filename), 'r') as fp:
        locations = json.load(fp)
        fingerprint_ids = sorted(list(locations.keys()))
        if len(fingerprint_ids) > 0:
            return int(fingerprint_ids[-1]) + 1
        else:
            return 0


def move(src, dest, verbose):
    log('\t Move {} to {}'.format(src, dest), end='', verbose=verbose)
    shutil.move(src, dest)
    log('\t Done\n', verbose=verbose)

def log(string, verbose, end='\n'):
    if verbose:
        print(string, end=end)

if __name__ == '__main__':
    move_fingerprint_clickwrapper() # pylint: disable=no-value-for-parameter
