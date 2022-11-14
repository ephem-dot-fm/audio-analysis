### COMMAND CENTER FOR RETRIEVAL ###
import time
from yellows_radar import write_stream

import threading
import schedule
import sys

def main(station_names, file_duration):
    # each {x} seconds, create a thread to analyze audio from stream
    schedule.every(file_duration).seconds.do(
        run_threaded, station_name=station_names, file_duration=file_duration)

    while True:
        schedule.run_pending()
        all_jobs = schedule.get_jobs()
        print(f'Checkpoint 1. All scheduled jobs are: {all_jobs}')
        time.sleep(5)

def run_threaded(station_name, file_duration):
    # creating a thread with a function of write_stream
    job_thread = threading.Thread(
        target=write_stream,
        args=(station_name, file_duration))

    job_thread.start()

if __name__ == "__main__":
    station_names = ['DDR', 'BFF', 'KOOP']
    file_duration = 20
    main(station_names, file_duration)
    
    # station_key = sys.argv[1]
    # print(f'TESTING STATION {station_key}')


# def get_going(ws):
#     # defining basic variables
#     station_names = ['SOMADSO', 'SOMAMTL', 'SOMADESI']
#     file_duration = 5

#     # enqueue the jobs to run
#     schedule.every(file_duration).seconds.do(
#         run_threaded,
#         station_name=station_names,
#         file_duration=file_duration)

#     # let's go!
#     while True:
#         schedule.run_pending()
#         time.sleep(5)