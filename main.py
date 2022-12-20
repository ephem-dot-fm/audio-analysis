import schedule
import time
from multiprocessing import Process
import requests
import os
from pydub import AudioSegment
import websocket
import json
from glob import glob

from dotenv import load_dotenv
load_dotenv()

from audio_characteristics.profile import get_audio_characteristics

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
    """
    Takes in a streaming url as input and writes the data coming from that stream to either an mp3 or aac file, which can the be converted to a wav file.  It does so with the help of the iter library to read it in in chunks. This method gets cut off once the time.sleep() method within analyze_audio concludes and is currently set to 5 seconds.  Therefore, roughly 5 second audio snippets will be extracted from a radio station then analyzed.

    Notes:
    - stream=True inside of requests.get() allows for the radio streams to properly be read in.
    """

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
    """
    Turns an audio file of mp3 or aac format into a wav file, which is the file format necessary for later processing.
    """
    
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

def send_via_ws(data):
    """
    This method is rather self-explanatory, creating a websocket connection to the fastapi websocket server deployed through Railway.app.  It's just a helper method that DRYs up code inside of analyze_audio. 
    """
    # send this to websocket server
    websocket.enableTrace(True)
    ws = websocket.WebSocket()
    ws.connect(os.getenv("DEPLOYED_WEBSOCKET_URL"))
    ws.send(data)
    print(ws.recv())
    ws.close()

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

def analyze_audio():
    """
    This method is the core of what's going on here.

    In step 1 the audio is retrieved from the (currently 3) radio stations and saved to a WAV file.  These processes
    are run simultaneously using the Process module and it's necessary to add them to an array, start everything in that 
    array, then end them.  
    
    The audio file names are tracked then passed into step 2 of the method, which analyzes them for audio characteristics including 
    loudness, mean pitch, and tempo. 
    """

    time_to_leave = str(int(time.time()) + 120)

    # create processes for three different stations then run them
    processes = []
    files = []

    station_names = ['DDR', 'BFF', 'KOOP']

    # Step 1: Write audio to files
    for station in station_names:
        audio_type = stations[station]['audio_type']
        file_name = f'soundbytes/{station}_{time_to_leave}.{audio_type}'
        files.append(file_name)
        process = Process(
            target=stream_to_audio_file, 
            name="Write stream to mp3 or aac", 
            args=(stations[station]['stream_url'], file_name))
        processes.append(process)

    # Start reading of radio stream
    for process in processes:
        process.start()
    
    # Let it write for 6 seconds
    time.sleep(6)

    # Terminate processes and also seal off files
    for process in processes:
        process.terminate()

    # Step 2: Analyze audio in file
    for file in files:
        wav_file = audio_file_to_wav(file) 

        try:
            station = wav_file.split(".")[0].split("_")[0].split("/")[1].lower()
            audio_stats = get_audio_characteristics(wav_file)  # analyze
            audio_stats_encoded = json.dumps({'audio_values' : {**audio_stats, 'station' : station}}).encode('utf-8')
            
            send_via_ws(audio_stats_encoded)
            
        except Exception as e:
            print(f"An exception occurred in write_stream within yellows_radar.py.  It is {e}.")

def schedule_audio_analyses():
    """
    Every six minutes four calls are made, separated by 20 second intervals, to analyze the audio of a radio station.  The thinking here is that by separating them by 20 seconds only they'll be proximate enough to be analyzing the same thing (i.e. the same song) and therefore we can expect similar values to be returned, hence making us more sure that any outliers detected are indeed outliers.

    After each of these the audio files that were written and subsequently analyzed are removed.
    """

    hourly_radio_analysis_times = ["00:00", "00:20", "00:40", "01:00", "06:00", "06:20", "06:40", "07:00", "12:00", "12:20", "12:40", "13:00", "18:00", "18:20", "18:40", "19:00", "24:00", "24:20", "24:40", "25:00", "30:00", "30:20", "30:40", "31:00", "36:00", "36:20", "36:40", "37:00", "42:00", "42:20", "42:40", "43:00", "48:00", "48:20", "48:40", "49:00", "54:00", "54:20", "54:40", "55:00"]

    hourly_file_cleanup_times = ["03:00", "09:00", "15:00", "21:00", "27:00", "33:00", "39:00", "45:00", "51:00", "57:00"]

    for time in hourly_radio_analysis_times:
        schedule.every().hour.at(time).do(analyze_audio)

    for time in hourly_file_cleanup_times:
        schedule.every().hour.at(time).do(spring_cleaning)   

def lights_on():
    schedule_audio_analyses()
    
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__=="__main__":
    lights_on()