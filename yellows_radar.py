import multiprocessing
import requests
import time
import os
from pydub import AudioSegment
import subprocess
import os
from collections import deque

from hsl import hsl
from red import spring_cleaning


stations = {
    'DDR': 'https://dublindigitalradio.out.airtime.pro/dublindigitalradio_a',
    'KUTX': 'https://kut.streamguys1.com/kutx-web',
    'WPRB': 'https://wprb.streamguys1.com/live',
    'SOMADSO': 'https://ice6.somafm.com/deepspaceone-128-mp3',
    'SOMADESI': 'https://ice1.somafm.com/suburbsofgoa-128-mp3',
    'SOMAMTL': 'https://ice1.somafm.com/metal-128-mp3',
    'SOMACLQ': 'https://ice6.somafm.com/cliqhop-128-mp3',
    'SOMAFOLK': 'https://ice4.somafm.com/folkfwd-128-mp3',
    'SOMALUSH': 'https://ice1.somafm.com/lush-128-mp3',
    'SOMAPOPT': 'https://ice1.somafm.com/poptron-128-mp3',
    'SOMAVPR': 'https://ice2.somafm.com/vaporwaves-128-mp3',
    'SOMAIND': 'https://ice4.somafm.com/indiepop-128-mp3'
}


def stream_to_mp3(station_url, file_name):
    with requests.get(station_url, stream=True) as r:
        with open(f'{file_name}.mp3', 'wb') as f:
            try:
                for block in r.iter_content(1024):
                    f.write(block)
            except KeyboardInterrupt:
                f.close()


def mp3_to_wav(file):
    src = f'{file}.mp3'
    dst = f'{file}.wav'

    try:
        audSeg = AudioSegment.from_file(src, "mp3")
        audSeg.export(dst, format="wav")
    except FileNotFoundError as f:
        print("Couldn't find that file homie")
    except:
        audSeg = AudioSegment.from_file(src, format="mp4")
        audSeg.export(dst, format="wav")


def write_stream(station_name, file_duration):
    print("Beginning to write a new stream")
    time_to_leave = str(int(time.time()) + 120)
    file_name = f'soundbytes/{station_name}_{time_to_leave}'

    # create a new Process which allows me to write a stream for x amount of time
    p = multiprocessing.Process(
        target=stream_to_mp3, name="Write Stream to MP3", args=(stations[station_name], file_name))

    p.start()
    time.sleep(file_duration)
    p.terminate()

    # convert mp3 to WAV file
    mp3_to_wav(file_name)

    # analyze
    hsl(file_name)

    # delete all files older than one minute
    spring_cleaning()


if __name__ == "__main__":
    hsl('soundbytes/SOMACLQ_1662489047')
