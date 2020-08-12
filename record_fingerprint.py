import os
import subprocess
import time
from threading import Timer

RECORDING_TIMEOUT = 30.0 # timeout [s] afterwhich the fingerprint recording process is killed
CLOSING_SRSLTE_TIMEOUT = 3.0 # timeout [s] to wait for srsLTE to close
N_RECORDING_TRY_UPPER_LIMIT = 10 # Amount of time we try recording a fingerprint before giving up

def record_fingerprint(conf_filepath, ce_filepath, ce_filesize, verbose=False):
    """Record a fingerprint by running `sudo srsue {conf_filepath}` for {duration} seconds
    
    Arguments:
        conf_filepath [str] -- Filepath to `ue.conf`
        ce_filepath [str] -- Filename to the file holding the ce fingerprint (typically ce.txt)
        ce_filesize [float] -- Size [MB] of the ce.txt before stopping the fingerprint's recording
        verbose [bool] -- whether to be verbose
    """

    subprocess.run('touch ./ce.txt', shell=True)
    subprocess.run('touch ./else.txt', shell=True)
    subprocess.run('touch ./info.txt', shell=True)

    fingerprint_is_recorded = False
    give_up = False
    n_recording_try = 0
    start_time = time.perf_counter()
    while (not fingerprint_is_recorded) and (not give_up):
        start_recording(conf_filepath=conf_filepath, verbose=verbose)
        n_recording_try += 1

        while True:
            if time.perf_counter() - start_time > RECORDING_TIMEOUT: # check if RECORDING_TIMEOUT has elapsed since we last started to try recording a fingerprint
                print(f'\t \t Timeout ({RECORDING_TIMEOUT}s) reached')
                if n_recording_try < N_RECORDING_TRY_UPPER_LIMIT:
                    start_time = time.perf_counter()
                    print('\t \t Trying again...')  
                else:
                    print('\t \t Giving up...')  
                    give_up = True
                break

            time.sleep(0.5)

            if os.path.isfile(ce_filepath): # check if ce.txt has reached {ce_filesize} MB
                size = os.stat(ce_filepath).st_size # size of filepath in Bytes
                if size > ce_filesize * 1e6: # ce_filesize in is MB, size in B
                    print('\t \t ce.txt filesize ({:.2f} MB) limit ({} MB) reached'.format(size/1e6, ce_filesize))
                    fingerprint_is_recorded = True
                    break
        
        stop_recording()
        time.sleep(CLOSING_SRSLTE_TIMEOUT)

def start_recording(conf_filepath, verbose=False):
    command = f'sudo ./record_fingerprint.sh {conf_filepath}'
    if verbose:
        subprocess.run(command, shell=True)
    else:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

def stop_recording():
    command = 'sudo pkill -INT srsue'
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
