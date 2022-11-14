from webbrowser import get
from xml.dom import minicompat
from tempo import get_tempo
import pyloudnorm as pyln
import librosa
import numpy as np
import soundfile as sf
import hsluv
from sty import bg
from datetime import datetime
import psycopg2
import time


from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color

# TEMPO
tempo_values = {
    'max': 140,
    'min': 60
}

loudness_values = {
    'max': -7,
    'min': -18
}

pitch_values = {
    'max': 6000,
    'min': 400
}


# time-based characteristics => base color
# def retrieve_tempo(file_name):
#     general_tempo = get_tempo('cnn', f'{file_name}.mp3')
#     return general_tempo


# how saturated color is => loudness
def loudness(file):
    # load audio (with shape (samples, channels))
    data, rate = sf.read(file)
    meter = pyln.Meter(rate)  # create BS.1770 meter
    perceived_loudness = meter.integrated_loudness(data)  # measure loudness

    return perceived_loudness


# lightness to darkness => spectral centroid which corresponds to 'brightness' of tone
def pitch(file):
    y, sr = librosa.load(file, sr=None)

    # get spectral centroid, mean of that, and masked mean using librosa
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    centroid_arr = centroid[0]
    regular_mean = centroid_arr.mean()
    masked = np.ma.masked_equal(centroid, 0)
    masked_mean = masked.mean()

    return regular_mean


def get_chroma_range(max, min, initial):
    percentile = (initial - min) / (max - min)
    if percentile > 1:
        return .95
    if percentile < 0:
        return .05
    return percentile


def lab_to_rgb(l, a, b):
    def to_rgb(color):
        color = round(color * 255)
        if color > 255:
            return 255
        if color < 0:
            return 0
        return color

    color1_lab = LabColor(l, a, b)
    print(color1_lab)

    color1_rgb = convert_color(color1_lab, sRGBColor)
    color1_rgb_tuple = color1_rgb.get_value_tuple()
    print(color1_rgb_tuple)
    r, g, b = to_rgb(color1_rgb_tuple[0]), to_rgb(
        color1_rgb_tuple[1]), to_rgb(color1_rgb_tuple[2])

    return [r, g, b]

    # qui = bg(r, g, b) + \
    #     "                " + bg.rs
    # print(qui)


# def get_current_show(station_name):
#     splat = file_name.split(".")[0].split("_")
#     print(f'Checkpoint line 125 of colour.py. What we want to split comes to {splat}')
#     timestamp = splat[1]
#     station_name = splat[0].split("/")[1].lower()
#     show, dj = '', ''

#     try:
#         show_deets = get_current_show(station_name)
#         show, dj = show_deets[0], show_deets[1]
#     except Exception as e:
#         print(e)

#     utc_now = datetime.utcnow()
#     utc_now_day = utc_now.strftime('%w')
#     utc_now_hour = utc_now.hour

#     # select statement where day is the same and hour is same as or equal to begin and less than end (this select statement could be improved upon over time)
#     conn = psycopg2.connect('postgresql://postgres:BBWjnHbbic4d0qoJnQYe@containers-us-west-46.railway.app:7052/railway')
#     cursor = conn.cursor()

#     cursor.execute('SELECT show, dj FROM schedules WHERE station = (%s) AND begin_day = (%s) AND begin_hour <= (%s) AND end_hour > (%s)',
#                    (station_name, utc_now_day, utc_now_hour, utc_now_hour))

#     shows = cursor.fetchall()
#     conn.commit()
#     cursor.close()
#     conn.close()

#     if len(shows) == 1:
#         return shows[0]
#     else:
#         print('problem here!')
#         return

def get_colour(file_name):
    # retrieving initial hsl values
    t = get_tempo('cnn', f'{file_name}')
    l = loudness(f'{file_name}')
    p = pitch(f'{file_name}')


    # translating audio values into chroma value
    tempo_percentile = round(get_chroma_range(
        tempo_values['max'], tempo_values['min'], t) * 100)
    loudness_percentile = round(get_chroma_range(
        loudness_values['max'], loudness_values['min'], l) * 100)
    pitch_percentile = round(get_chroma_range(
        pitch_values['max'], pitch_values['min'], p) * 100)

    print(f'Checkpoint 3: retrieved values.')
    print(f'Show: {show} on {station_name}.')
    print(f'Tempo: {t} = {tempo_percentile}%')
    print(f'Loudness: {l} = {loudness_percentile}%')
    print(f'Pitch: {p} = {pitch_percentile}%')

    # RGB
    [r, g, b] = hsluv.hsluv_to_rgb(
        [(tempo_percentile / 100) * 180 + 180, loudness_percentile, pitch_percentile])
    rgb = round(r * 255), round(g * 255), round(b * 255)

    return {
        'current_colors':  {
            'station': station_name,
            'rgb': rgb
        }
    }


if __name__ == "__main__":
    print(time.time())
    # print(get_colour('hi/bff_good'))

    # qui = bg(round(rgb[0] * 255), round(rgb[1] * 255), round(rgb[2] * 255)) + \
    #     "                " + bg.rs
    # print(f'{station_name[11:]}: {qui}')
