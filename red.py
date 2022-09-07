# print out all the files in a given directory

# find the files that need to be deleted
# write the script to delete them
#

import os
from glob import glob
import time


def rid_soundfiles():
    cwd = os.getcwd()
    print('CWD: ', cwd)
    list_of_filenames = glob("soundbytes/*")
    for file in list_of_filenames:
        timestamp = file.split('_')[1].split('.')[0]
        if int(timestamp) < int(time.time()):
            print(f'REMOVED FILE--{file}')
            os.remove(f'{os.getcwd()}/{file}')


if __name__ == "__main__":
    rid_soundfiles()
