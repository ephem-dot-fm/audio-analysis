### COMMAND CENTER FOR RETRIEVAL ###
import time
from yellows_radar import write_stream

import threading
import schedule
import sys


def get_going(ws):
    # defining basic variables
    station_names = ['SOMADSO', 'SOMAMTL', 'SOMADESI']
    file_duration = 5

    # enqueue the jobs to run
    schedule.every(file_duration).seconds.do(
        run_threaded,
        station_name=station_names,
        file_duration=file_duration)

    # let's go!
    while True:
        schedule.run_pending()
        time.sleep(5)


def run_threaded(station_name, file_duration):
    # defining a thread with a function of write_stream and relevent args
    job_thread = threading.Thread(
        target=write_stream,
        args=(station_name, file_duration))

    job_thread.start()


# every 20 seconds, begins writing + analyzing a new stream
if __name__ == "__main__":
    # station_key = sys.argv[1]
    # print(f'TESTING STATION {station_key}')

    station_names = ['BFF']
    file_duration = 20

    schedule.every(file_duration).seconds.do(
        run_threaded, station_name=station_names, file_duration=file_duration)

    while True:
        schedule.run_pending()
        all_jobs = schedule.get_jobs()
        # print(f'ALL JOBS INCLUDE: {all_jobs}')
        time.sleep(5)
