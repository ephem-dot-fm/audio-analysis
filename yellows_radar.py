from multiprocessing import Process
import requests
import time
import os
from pydub import AudioSegment
import subprocess
import os
from collections import deque
import websocket
import json

from colour import get_colour
from red import spring_cleaning
import config


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
    'SOMAIND': 'https://ice4.somafm.com/indiepop-128-mp3',
    'BFF': 'https://stream.bff.fm/1/mp3.mp3'
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


def write_stream(station_names, file_duration):
    time_to_leave = str(int(time.time()) + 120)

    # create processes for three different stations then run them
    processes = []
    files = []

    for station in station_names:
        file_name = f'soundbytes/{station}_{time_to_leave}'
        files.append(file_name)
        process = Process(
            target=stream_to_mp3, name="Write Stream to MP3", args=(stations[station], file_name))
        processes.append(process)

    print(f'PROCESSES: {processes}')

    for process in processes:
        process.start()

    time.sleep(15)

    for process in processes:
        process.terminate()

    # assuming here that relevant files have been written
    for file in files:
        mp3_to_wav(file)  # convert mp3 to WAV file

        # retrieve a color value from music sample
        audio_representation = get_colour(file)  # analyze
        print(
            f'AUDIO REPRESENTATION: {audio_representation} {type(audio_representation)}')
        data_encoded = json.dumps(audio_representation).encode(
            'utf-8')  # data serialized

        # send this to websocket server
        websocket.enableTrace(True)
        ws = websocket.WebSocket()
        ws.connect("ws://localhost:8000/ws/2")
        ws.send(data_encoded)
        print(ws.recv())
        ws.close()

    # delete all files older than one minute
    spring_cleaning()


if __name__ == "__main__":
    get_colour('soundbytes/SOMAMTL_1665971952')
