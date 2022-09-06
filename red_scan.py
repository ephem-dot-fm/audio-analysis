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


if __name__ == "__main__":
    model_name = 'cnn'

    # initialize the model (may be re-used for multiple files)
    classifier = TempoClassifier(model_name)
    print('object: ', classifier, 'model name: ',
          classifier.model_name, 'resource: ', classifier.model)
