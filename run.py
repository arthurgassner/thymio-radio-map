import os

from move_fingerprint import move_fingerprint
from record_fingerprint import record_fingerprint
from thymio import Thymio

SRSUE_FOLDERPATH = '../../srsLTE-modified/srsue'
RECORDING_DURATION = 10.0 # [s]
N_STEPS = 10 # Amount of RPs to gather
DISTANCE_TO_TRAVEL = 10 # [cm] distance between each RP
THYMIO_POSITIONS_FILENAME = 'thymio_positions'

INITIAL_POSITION = [0,0]

def run():
    last_position = INITIAL_POSITION # (x,y) coordinates of the position where the Thymio last stopped

    # Inspect {THYMIO_POSITIONS_FILENAME}.pkl to infer the Thymio's absolute position    
    thymio_positions_filepath = '{}.txt'.format(THYMIO_POSITIONS_FILENAME)
    if os.path.isfile(thymio_positions_filepath):
        positions = []
        with open(thymio_positions_filepath, 'r') as fp:
            positions = [line.rstrip() for line in fp.readlines()]
        last_position = eval(positions[-1])


    for _ in range(N_STEPS):
        print ('Fingerprint in [{:.1f}, {:.1f}]'.format(last_position[0], last_position[1]))
        print('\t- Record fingerprint')
        record_fingerprint(SRSUE_FOLDERPATH, RECORDING_DURATION)

        print('\t- Move fingerprint')
        move_fingerprint(x=last_position[0],
                         y=last_position[1], 
                         src_folderpath='./',
                         dest_folderpath='dev',
                         verbose=False)

        print('\t- Move Thymio to ', end='')
        thymio = Thymio(initial_position=last_position, distance_to_travel=DISTANCE_TO_TRAVEL)
        thymio.run()
        last_position = fetch_last_position(filename=THYMIO_POSITIONS_FILENAME)
        print('[{:.1f}, {:.1f}]'.format(last_position[0], last_position[1]))
        print('')


def fetch_last_position(filename):
    """Inspect {filename}.txt to infer the Thymio's last absolute position, i.e. the last one appended    

    Args:
        filename (str): Name of the file holding the positions where the Thymio stopped

    Returns:
        [List of floats]: (x,y) absolute coordinates of the Thymio's last stop
    """

    thymio_positions_filepath = '{}.txt'.format(filename)
    positions = []
    with open(thymio_positions_filepath, 'r') as fp:
        positions = [line.rstrip() for line in fp.readlines()]
    last_position = eval(positions[-1])
    return last_position


if __name__ == '__main__':
    run()
