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

import colour
from red import spring_cleaning
import config


stations = {
    'DDR': { 'stream_url': 'https://dublindigitalradio.out.airtime.pro/dublindigitalradio_a',
            'audio_type': 'mp3'},
    'KUTX': { 'stream_url': 'https://kut.streamguys1.com/kutx-web',
            'audio_type': 'mp3'},
    'KOOP': { 'stream_url': 'https://streaming.koop.org/stream.aac',
            'audio_type': 'aac'},
    'WPRB': { 'stream_url': 'https://wprb.streamguys1.com/live',
            'audio_type': 'mp3'},
    'BFF': { 'stream_url': 'https://stream.bff.fm/1/mp3.mp3',
            'audio_type': 'mp3'}
}


def stream_to_audio_file(station_url, file_name):
    if (file_name[-3:] == "mp3"):
        with requests.get(station_url, stream=True) as r:
            with open(f'{file_name}', 'wb') as f:
                try:
                    for block in r.iter_content(1024):
                        f.write(block)
                except KeyboardInterrupt:
                    f.close()
    elif (file_name[-3:] == "aac"):
        with requests.get(station_url, stream=True) as r:
            with open(f'{file_name}', 'wb') as f:
                try:
                    for block in r.iter_content(1024):
                        f.write(block)
                except KeyboardInterrupt:
                    f.close()


def audio_file_to_wav(file):
    src = file
    dst = f'{file[:-4]}.wav'

    try:
        audSeg = AudioSegment.from_file(src, format=file[-3:])
        audSeg.export(dst, format="wav")
        return dst
    except FileNotFoundError as f:
        print("Couldn't find that file homie")
    except Exception as e:
        print(f'Exception {e} in audio_file_to_wav function')


def write_stream(station_names, file_duration):
    time_to_leave = str(int(time.time()) + 120)

    # create processes for three different stations then run them
    processes = []
    files = []

    for station in station_names:
        audio_type = stations[station]['audio_type']
        file_name = f'soundbytes/{station}_{time_to_leave}.{audio_type}'
        files.append(file_name)
        process = Process(
            target=stream_to_audio_file, 
            name="Write stream to mp3 or aac", 
            args=(stations[station]['stream_url'], file_name))
        processes.append(process)


    for process in processes:
        process.start()

    time.sleep(15)

    for process in processes:
        process.terminate()

    for file in files:
        wav_file = audio_file_to_wav(file) 

        # retrieve a color value from music sample
        try:
            station = wav_file.split(".")[0].split("_")[0].split("/")[1].lower()
            audio_stats = colour.get_colour(wav_file)  # analyze
            audio_stats['station'] = station
            print(f'Line 97 in yellows radar. wav_file{wav_file}, station: {station}, audio statsaudio_stats: {audio_stats}')
            audio_stats_wrapper = {
                'audio_values': audio_stats
            }
            audio_stats_encoded = json.dumps(audio_stats_wrapper).encode('utf-8')  # audio stats serialized

            # send this to websocket server
            websocket.enableTrace(True)
            ws = websocket.WebSocket()
            ws.connect("wss://websocket-server-production.up.railway.app/ws")
            ws.send(audio_stats_encoded)
            print(ws.recv())
            ws.close()
            
        except Exception as e:
            print(f"An exception occurred in write_stream within yellows_radar.py.  It is {e}.")

    # delete all files older than one minute
    spring_cleaning()


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocket()
    ws.connect("wss://websocket-server-production.up.railway.app/ws")
    ws.send("hello")
    print(ws.recv())
    ws.close()