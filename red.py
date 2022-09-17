import os
from glob import glob
import time


def spring_cleaning():
    cwd = os.getcwd()
    # print('CWD: ', cwd)
    list_of_filenames = glob("soundbytes/*")
    # print(f'LIST OF FILE NAMES: {list_of_filenames}')
    cur_files = os.listdir(os.curdir)
    # print(f'CURRENT FILES: {cur_files}')
    for file in list_of_filenames:
        # print(f'FILE: {file}')
        if 'starter.txt' in file:
            continue

        timestamp = file.split('_')[1].split('.')[0]
        if int(timestamp) < int(time.time()):
            # print(f'REMOVED FILE--{file}')
            os.remove(f'{os.getcwd()}/{file}')


if __name__ == "__main__":
    spring_cleaning()
