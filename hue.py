import librosa as librosa
import tensorflow as tf
import numpy as np
from pathlib import Path
import pkgutil
import logging
import urllib.request
from urllib.error import HTTPError
import sys

logger = logging.getLogger('tempocnn.classifier')


def std_normalizer(data):
    """
    Normalizes data to zero mean and unit variance.
    Used by Mazurka models.

    :param data: data
    :return: standardized data
    """
    # normalize as 64 bit, to avoid numpy warnings
    data = data.astype(np.float64)
    mean = np.mean(data)
    std = np.std(data)
    if std != 0.:
        data = (data-mean) / std
    return data.astype(np.float16)


def max_normalizer(data):
    """
    Divides by max. Used as normalization by older models.

    :param data: data
    :return: normalized data (max = 1)
    """
    m = np.max(data)
    if m != 0:
        data /= m
    return data


class TempoClassifier:
    """
    Classifier that can estimate musical tempo in different formats.
    """

    def __init__(self, model_name='fcn'):
        """
        Initializes this classifier with a Keras model.

        :param model_name: model name from sub-package models. E.g. 'fcn', 'cnn', or 'ismir2018'
        """
        if 'fma' in model_name:
            # fma model uses log BPM scale
            factor = 256. / np.log(10)
            self.to_bpm = lambda index: np.exp((index + 435) / factor)
        else:
            self.to_bpm = lambda index: index + 30

        # match alias for dt_maz_v fold 0.
        if model_name == 'mazurka':
            model_name = 'dt_maz_v_fold0'
        # match aliases for specific deep/shallow models
        elif model_name == 'deeptemp':
            model_name = 'deeptemp_k16'
        elif model_name == 'shallowtemp':
            model_name = 'shallowtemp_k6'
        elif model_name == 'deepsquare':
            model_name = 'deepsquare_k16'
        self.model_name = model_name

        # mazurka and deeptemp/shallowtempo models use a different kind of normalization
        self.normalize = std_normalizer if 'dt_maz' in self.model_name \
                                           or 'deeptemp' in self.model_name \
                                           or 'deepsquare' in self.model_name \
                                           or 'shallowtemp' in self.model_name \
            else max_normalizer

        resource = _to_model_resource(model_name)
        print('resource', resource)
        try:
            file = _extract_from_package(resource)
        except Exception as e:
            print('Failed to find a model named \'{}\'. Please check the model name.'.format(model_name),
                  file=sys.stderr)
            raise e
        self.model = tf.keras.models.load_model(file)

    def estimate_tempo(self, data, interpolate=False):
        """
        Estimates the pre-dominant global tempo.

        :param data: features
        :param interpolate: if ``True``, compute prediction for each window, average predictions
        and then find the max value via quadratic interpolation.
        :return: a single tempo
        """
        prediction = self.estimate(data)
        averaged_prediction = np.average(prediction, axis=0)
        if interpolate:
            index, _ = self.quad_interpol_argmax(averaged_prediction)
        else:
            index = np.argmax(averaged_prediction)
        return self.to_bpm(index)

    def estimate(self, data):
        """
        Estimate a tempo distribution.
        Probabilities are indexed, starting with 30 BPM and ending with 286 BPM.

        :param data: features
        :return: tempo probability distribution
        """
        assert len(
            data.shape) == 4, 'Input data must be four dimensional. Actual shape was ' + str(data.shape)
        assert data.shape[1] == 40, 'Second dim of data must be 40. Actual shape was ' + \
            str(data.shape)
        assert data.shape[2] == 256, 'Third dim of data must be 256. Actual shape was ' + \
            str(data.shape)
        assert data.shape[3] == 1, 'Fourth dim of data must be 1. Actual shape was ' + \
            str(data.shape)
        norm_data = self.normalize(data)
        return self.model.predict(norm_data, norm_data.shape[0])


def _to_model_resource(model_name):
    file = model_name
    if not model_name.endswith('.h5'):
        file = file + '.h5'
    if not file.startswith('models/'):
        file = 'models/' + file
    return file


def _extract_from_package(resource):
    # check local cache
    cache_path = Path(Path.home(), '.tempocnn', resource)
    print('cache path', cache_path)
    if cache_path.exists():
        return str(cache_path)

    # ensure cache path exists
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    data = pkgutil.get_data('tempocnn', resource)
    if not data:
        data = _load_model_from_github(resource)

    # write to cache
    with open(cache_path, 'wb') as f:
        f.write(data)

    return str(cache_path)


def _load_model_from_github(resource):
    url = f"https://raw.githubusercontent.com/hendriks73/tempo-cnn/main/tempocnn/{resource}"
    logger.info(f"Attempting to download model file from main branch {url}")
    try:
        response = urllib.request.urlopen(url)
        return response.read()
    except HTTPError as e:
        # fall back to dev branch
        try:
            url = f"https://raw.githubusercontent.com/hendriks73/tempo-cnn/dev/tempocnn/{resource}"
            logger.info(
                f"Attempting to download model file from dev branch {url}")
            response = urllib.request.urlopen(url)
            return response.read()
        except Exception:
            pass

        raise FileNotFoundError(
            f"Failed to download model from {url}: {type(e).__name__}: {e}")


"""
Feature loading from audio files.

Specifically, tempo-cnn uses mel spectra with 40 bands ranging from
20 to 5000 Hz.
"""


def read_features(file, frames=256, hop_length=128, zero_pad=False):
    """
    Resample file to 11025 Hz, then transform using STFT with length 1024
    and hop size 512. Convert resulting linear spectrum to mel spectrum
    with 40 bands ranging from 20 to 5000 Hz.

    Since we require at least 256 frames, shorter audio excerpts are always
    zero padded.

    Specifically for tempogram 128 frames each can be added at the front and
    at the back in order to make the calculation of BPM values for the first
    and the last window possible.

    :param file: file
    :param frames: 256
    :param hop_length: 128 or shorter
    :param zero_pad: adds 128 zero frames both at the front and back
    :param normalize: normalization function
    :return: feature tensor for the whole file
    """
    y, sr = librosa.load(file, sr=11025)
    data = librosa.feature.melspectrogram(y=y, sr=11025, n_fft=1024, hop_length=512,
                                          power=1, n_mels=40, fmin=20, fmax=5000)
    data = np.reshape(data, (1, data.shape[0], data.shape[1], 1))

    # add frames/2 zero frames before and after the data
    if zero_pad:
        data = _add_zeros(data, frames)

    # zero-pad, if we have less than 256 frames to make sure we get some
    # result at all
    if data.shape[2] < frames:
        data = _ensure_length(data, frames)

    # convert data to overlapping windows,
    # each window is one sample (first dim)
    return _to_sliding_window(data, frames, hop_length)


def _ensure_length(data, length):
    padded_data = np.zeros((1, data.shape[1], length, 1), dtype=data.dtype)
    padded_data[0, :, 0:data.shape[2], 0] = data[0, :, :, 0]
    return padded_data


def _add_zeros(data, zeros):
    padded_data = np.zeros(
        (1, data.shape[1], data.shape[2] + zeros, 1), dtype=data.dtype)
    padded_data[0, :, zeros // 2:data.shape[2] +
                (zeros // 2), 0] = data[0, :, :, 0]
    return padded_data


def _to_sliding_window(data, window_length, hop_length):
    total_frames = data.shape[2]
    windowed_data = []
    for offset in range(0, ((total_frames - window_length) // hop_length + 1) * hop_length, hop_length):
        windowed_data.append(
            np.copy(data[:, :, offset:window_length + offset, :]))
    return np.concatenate(windowed_data, axis=0)


def get_hue(model, file_path):
    # initialize the model (may be re-used for multiple files)
    classifier = TempoClassifier(model_name)

    # read the file's features
    features = read_features(input_file)

    # estimate the global tempo
    tempo = classifier.estimate_tempo(features, interpolate=False)
    return tempo


if __name__ == "__main__":
    print('aloha from red_scan')
    model_name = 'cnn'
    input_file = 'soundbytes/SOMACLQ_1662489047.mp3'

    # initialize the model (may be re-used for multiple files)
    classifier = TempoClassifier(model_name)

    # read the file's features
    features = read_features(input_file)

    # estimate the global tempo
    tempo = classifier.estimate_tempo(features, interpolate=False)
    print(f"Estimated global tempo: {tempo}")
