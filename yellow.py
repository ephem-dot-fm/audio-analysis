### COMMAND CENTER FOR RETRIEVAL ###
import time
from yellows_radar import write_stream

import threading
import schedule


def run_threaded(station_name, file_duration):
    job_thread = threading.Thread(
        target=write_stream, args=(station_name, file_duration))
    job_thread.start()


print("hi honey!")

# every 20 seconds, begins writing + analyzing a new stream
if __name__ == "__main__":
    print("hi there!")
    # file_duration = 20
    # schedule.every(file_duration).seconds.do(
    #     run_threaded, station_name='SOMACLQ', file_duration=file_duration)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
