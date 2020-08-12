import os
import time 

from thymio import Thymio

N_STEPS = 100 # Amount of RPs to gather
DISTANCE_TO_TRAVEL = 5 # [cm] distance between each RP
THYMIO_POSITIONS_FILENAME = 'thymio_positions'
DEST_FOLDERPATH = 'test_thymio'

INITIAL_POSITION = [0,0]

def test_thymio():
    last_position = INITIAL_POSITION # (x,y) coordinates of the position where the Thymio last stopped

    # Inspect {THYMIO_POSITIONS_FILENAME}.txt to infer the Thymio's absolute position    
    thymio_positions_filepath = os.path.join(DEST_FOLDERPATH, f'{THYMIO_POSITIONS_FILENAME}.txt')
    if os.path.isfile(thymio_positions_filepath):
        positions = []
        with open(thymio_positions_filepath, 'r') as fp:
            positions = [line.rstrip() for line in fp.readlines()]
        last_position = eval(positions[-1])

    print('Moving {}cm ({}cm increments) from [{:.2f}, {:.2f}] \n'.format(DISTANCE_TO_TRAVEL * N_STEPS, DISTANCE_TO_TRAVEL, last_position[0], last_position[1]))

    for step in range(N_STEPS):
        print(f'- #{step} Move Thymio to ', end='')
        time.sleep(0.1)
        thymio = Thymio(initial_position=last_position, 
                        distance_to_travel=DISTANCE_TO_TRAVEL, 
                        positions_filename=THYMIO_POSITIONS_FILENAME,
                        dest_folderpath=DEST_FOLDERPATH)
        thymio.run()
        last_position = fetch_last_position(filepath=os.path.join(DEST_FOLDERPATH, f'{THYMIO_POSITIONS_FILENAME}.txt'))
        print('[{:.2f}, {:.2f}]'.format(last_position[0], last_position[1]))
        print('')
        time.sleep(1)

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
    test_thymio()
