import os
import time
import subprocess

from move_fingerprint import move_fingerprint
from record_fingerprint import record_fingerprint
from thymio import Thymio

STARTING_TIMER = 20 # Timer [s] before starting, in case you need to exit the room
SRSUE_CONF_FILEPATH = '../srsLTE-modified/srsue/ue-digital-lab.conf'
CE_FILEPATH = 'ce.txt'
CE_FILESIZE = 20 # Filesize [MB] above which the recording is stopped
N_STEPS = 5 # Amount of RPs to gather
DISTANCE_TO_TRAVEL = 1 # [cm] distance between each RP
THYMIO_POSITIONS_FILENAME = 'thymio_positions'
DEST_FOLDERPATH = 'line-7'

INITIAL_POSITION = [0,0]

def run():
    start_time = time.time()
    last_position = INITIAL_POSITION # (x,y) coordinates of the position where the Thymio last stopped

    # Inspect {THYMIO_POSITIONS_FILENAME}.txt to infer the Thymio's absolute position    
    thymio_positions_filepath = os.path.join(DEST_FOLDERPATH, f'{THYMIO_POSITIONS_FILENAME}.txt')    
    positions = []

    if os.path.isfile(thymio_positions_filepath):
        with open(thymio_positions_filepath, 'r') as fp:
            positions = [line.rstrip() for line in fp.readlines()]
        last_position = eval(positions[-1])
        print('Already {} fingerprints found in {}/ \n'.format(len(positions), DEST_FOLDERPATH))

    print('Gathering {} fingerprints over {}cm \n'.format(N_STEPS, DISTANCE_TO_TRAVEL * N_STEPS))
    print(f'Wait {STARTING_TIMER}s before starting... \n')
    time.sleep(STARTING_TIMER)

    for step in range(N_STEPS):
        print('Fingerprint #{} in [{:.2f}, {:.2f}]'.format(step + len(positions), last_position[0], last_position[1]))

        rm_fingerprint()

        while True:
            if os.path.isfile('ce.txt'): # check if ce.txt has reached {ce_filesize} MB
                size = os.stat('ce.txt').st_size # size of filepath in Bytes
                if size > CE_FILESIZE * 1e6: # ce_filesize in is MB, size in B
                    print('\t \t ce.txt filesize ({:.2f} MB) limit ({} MB) reached'.format(size/1e6, CE_FILESIZE))
                    break

        print('\t- Move fingerprint')
        move_fingerprint(x=last_position[0],
                         y=last_position[1], 
                         src_folderpath='./',
                         dest_folderpath=DEST_FOLDERPATH,
                         verbose=False)

        print('\t- Move Thymio to ', end='')
        thymio = Thymio(initial_position=last_position, 
                        distance_to_travel=DISTANCE_TO_TRAVEL, 
                        positions_filename=THYMIO_POSITIONS_FILENAME,
                        dest_folderpath=DEST_FOLDERPATH)
        thymio.run()
        last_position = fetch_last_position(filepath=os.path.join(DEST_FOLDERPATH, f'{THYMIO_POSITIONS_FILENAME}.txt'))
        print('[{:.2f}, {:.2f}]'.format(last_position[0], last_position[1]))
        print('')

    elapsed_time = time.time() - start_time
    print('Script took {}'.format(time.strftime('%H:%M:%S', time.gmtime(elapsed_time))))

    # Warn user that the script has finished
    duration = 10  # seconds
    freq = 880  # Hz
    os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))

def rm_fingerprint():
    subprocess.run('rm -f ce.txt', shell=True)
    subprocess.run('rm -f else.txt', shell=True)
    subprocess.run('rm -f info.txt', shell=True)

def fetch_last_position(filepath):
    """Inspect {filepath}.txt to infer the Thymio's last absolute position, i.e. the last one appended    

    Args:
        filepath (str): Name of the file holding the positions where the Thymio stopped

    Returns:
        [List of floats]: (x,y) absolute coordinates of the Thymio's last stop
    """

    positions = []
    with open(filepath, 'r') as fp:
        positions = [line.rstrip() for line in fp.readlines()]
    last_position = eval(positions[-1])
    return last_position


if __name__ == '__main__':
    run()
