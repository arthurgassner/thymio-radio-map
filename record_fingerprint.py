import os
import subprocess
import time
from threading import Timer

CONF_FILENAME = 'ue.conf'
SRSLTE_MODIFIED_SRSUE_FOLDERPATH = '../../srsLTE-modified/srsue'

def record_fingerprint(conf_folderpath, duration):
    """Record a fingerprint by running `sudo srsue {conf_folderpath}/ue.conf` for {duration} seconds
    
    Arguments:
        conf_folderpath [str] -- Folderpath where `ue.conf` is located
        duration [float] -- Duration [s] of the recording 
    """
    
    conf_filepath = os.path.join(conf_folderpath, CONF_FILENAME)
    command = ['sudo', './record_fingerprint.sh', str(duration)]
    #command = ['ping', 'google.com']
    subprocess.run(command, capture_output=True)

if __name__ == '__main__':
    record_fingerprint(SRSLTE_MODIFIED_SRSUE_FOLDERPATH, 10) # pylint: disable=no-value-for-parameter
 