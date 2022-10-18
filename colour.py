from webbrowser import get
from xml.dom import minicompat
from tempo import get_tempo
import pyloudnorm as pyln
import librosa
import numpy as np
import soundfile as sf
import hsluv
from sty import bg

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


def get_colour(file_name):
    splat = file_name.split("_")
    timestamp = splat[1]
    station_name = splat[0].split("/")[1]

    # retrieving initial hsl values
    t = get_tempo('cnn', f'{file_name}.wav')
    l = loudness(f'{file_name}.wav')
    p = pitch(f'{file_name}.wav')

    # translating audio values into chroma value
    tempo_percentile = round(get_chroma_range(
        tempo_values['max'], tempo_values['min'], t) * 100)
    loudness_percentile = round(get_chroma_range(
        loudness_values['max'], loudness_values['min'], l) * 100)
    pitch_percentile = round(get_chroma_range(
        pitch_values['max'], pitch_values['min'], p) * 100)

    # HSL
    rgb = hsluv.hsluv_to_rgb(
        [(tempo_percentile / 100) * 180 + 180, loudness_percentile, pitch_percentile])

    return {
        'station': station_name,
        'rgb': rgb,
        'timestamp': timestamp
    }

    # printing hsl input values, to be converted to rgb
    # print(f'TEMPO: {round(t, 2)} bpm ({tempo_percentile}%)')
    # print(f'LOUDNESS: {round(l, 2)} db ({loudness_percentile}%)')
    # print(f'PITCH: {round(p, 2)} hz ({pitch_percentile}%)')

    # LAB IMPLEMENTATION
    # l = pitch_percentile * 120 - 60
    # a = loudness_percentile * 120 - 60
    # b = tempo_percentile * 120 - 60
    # [r, g, b] = lab_to_rgb(l, a, b)

    # # print(f'RED: {red}, GREEN: {green}, BLUE: {blue}')

    # qui = bg(round(rgb[0] * 255), round(rgb[1] * 255), round(rgb[2] * 255)) + \
    #     "                " + bg.rs
    # print(f'{station_name[11:]}: {qui}')


if __name__ == "__main__":
    # qui = bg(240, 10, 10) + \
    #     "This background color represents the musical value." + bg.rs
    # print(qui)
    # L: 0 to 100
    # a: -128 to 127
    # b: -128 to 127
    print(get_chroma_range(tempo_values['max'], tempo_values['min'], 153))
