import os

from move_fingerprint import move_fingerprint
from record_fingerprint import record_fingerprint

SRSUE_CONF_FILEPATH = '../srsLTE-modified/srsue/ue-digital-lab.conf'
CE_FILEPATH = 'ce.txt'
CE_FILESIZE = 10 # Filesize [MB] above which the recording is stopped
DEST_FOLDERPATH = 'test_fingerprint'

FAKE_POSITION = [0,0]

def test_fingerprint():
    print('- Record fingerprint')
    record_fingerprint(SRSUE_CONF_FILEPATH, CE_FILEPATH, CE_FILESIZE, verbose=True)

    print('- Move fingerprint')
    move_fingerprint(x=FAKE_POSITION[0],
                     y=FAKE_POSITION[1], 
                     src_folderpath='./',
                     dest_folderpath=DEST_FOLDERPATH,
                     verbose=False)

if __name__ == '__main__':
    test_fingerprint()
