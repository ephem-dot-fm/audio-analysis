from audio_characteristics.tempo import get_tempo
import pyloudnorm as pyln
import librosa
import numpy as np
import soundfile as sf

# locates loudness of music, adjusted for human perception
# will be used to determine saturation of color
def loudness(file):
    # load audio (with shape (samples, channels))
    data, rate = sf.read(file)
    meter = pyln.Meter(rate)  # create BS.1770 meter
    perceived_loudness = meter.integrated_loudness(data)  # measure loudness

    return perceived_loudness

# locates spectral centroid which corresponds to 'brightness' of tone
# will be used to find lightness to darkness of color
def pitch(file):
    y, sr = librosa.load(file, sr=None)

    # get spectral centroid, mean of that, and masked mean using librosa
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    centroid_arr = centroid[0]
    regular_mean = centroid_arr.mean()
    masked = np.ma.masked_equal(centroid, 0)
    masked_mean = masked.mean()

    return regular_mean

def get_audio_characteristics(file_name):
    try:
        return {
                'station': '',
                'tempo': int(get_tempo('cnn', f'{file_name}')),
                'loudness': int(loudness(f'{file_name}')),
                'pitch': int(pitch(f'{file_name}'))
            }
    except Exception as e:
        print(f'Exception occurred in get_colour method within colour.py. It is: {e}')


if __name__ == "__main__":
    print('boogeyman')
    