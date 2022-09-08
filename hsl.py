from webbrowser import get
# from hue import hue
import pyloudnorm as pyln
import librosa
import numpy as np
import soundfile as sf


# time-based characteristics => base color
def hue(file_name):
    bpm = hue('cnn', f'{file_name}.mp3')
    hue = bpm

    return hue


# how saturated color is => loudness
def saturation(file):
    # load audio (with shape (samples, channels))
    data, rate = sf.read(file)
    meter = pyln.Meter(rate)  # create BS.1770 meter
    loudness = meter.integrated_loudness(data)  # measure loudness

    return loudness


# lightness to darkness => spectral centroid which corresponds to 'brightness' of tone
def value(file):
    y, sr = librosa.load(file, sr=None)

    # get spectral centroid, mean of that, and masked mean using librosa
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    centroid_arr = centroid[0]
    regular_mean = centroid_arr.mean()
    masked = np.ma.masked_equal(centroid, 0)
    masked_mean = masked.mean()

    return regular_mean


def hsl(file_name):
    # h = hue(file_name)
    s = saturation(file_name)
    v = value(file_name)
    print(f'SATURATION IS: {saturation}')
    print(f'VALUE IS: {value}')


if __name__ == "__main__":
    # hue = get_hue('cnn', 'soundbytes/SOMACLQ_1662489047.mp3')
    # print(hue)
    pass
