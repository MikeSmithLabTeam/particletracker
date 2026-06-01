import os
import cv2
import numpy as np
import pytest

from particletracker.preprocess import preprocessing_methods as pm
from particletracker.customexceptions import CustomError


def test_adaptive_threshold_generates_binary_output():
    img = np.tile(np.arange(0, 100, dtype=np.uint8), (100, 1))
    parameters = {
        'preprocess': {
            'adaptive_threshold': {
                'block_size': 15,
                'C': 5,
                'invert': False,
            }
        }
    }

    output = pm.adaptive_threshold(img, parameters=parameters, section='preprocess', call_num=None)

    assert output.shape == img.shape
    assert set(np.unique(output)).issubset({0, 255})


def test_blur_applies_gaussian_blur():
    img = np.zeros((11, 11), dtype=np.uint8)
    img[5, 5] = 255
    parameters = {
        'preprocess': {
            'blur': {'kernel': [3, 1, 5, 2]}
        }
    }

    output = pm.blur(img, parameters=parameters, call_num=None)

    assert output.shape == img.shape
    assert output[5, 5] < 255
    assert output[5, 5] > 0


def test_brightness_contrast_adjusts_intensity():
    img = np.full((3, 3), 100, dtype=np.uint8)
    parameters = {
        'preprocess': {
            'brightness_contrast': {
                'brightness': 20,
                'contrast': 1.5,
            }
        }
    }

    output = pm.brightness_contrast(img, parameters=parameters, section='preprocess', call_num=None)

    assert output[0, 0] == 170


def test_colour_channel_selects_the_requested_channel():
    img = np.zeros((2, 2, 3), dtype=np.uint8)
    img[:, :, 0] = 10
    img[:, :, 1] = 20
    img[:, :, 2] = 30
    parameters = {
        'preprocess': {
            'colour_channel': {'colour': 'red'}
        }
    }

    output = pm.colour_channel(img, parameters=parameters, section='preprocess', call_num=None)

    assert output.shape == img[:, :, 2].shape
    assert np.array_equal(output, img[:, :, 2])


def test_colour_channel_raises_for_invalid_option():
    img = np.zeros((2, 2, 3), dtype=np.uint8)
    parameters = {
        'preprocess': {
            'colour_channel': {'colour': 'yellow'}
        }
    }

    with pytest.raises(CustomError):
        pm.colour_channel(img, parameters=parameters, section='preprocess', call_num=None)


def test_dilation_expands_binary_regions():
    img = np.zeros((7, 7), dtype=np.uint8)
    img[3, 3] = 255
    parameters = {
        'preprocess': {
            'dilation': {'kernel': 3, 'iterations': 1}
        }
    }

    output = pm.dilation(img, parameters=parameters, section='preprocess', call_num=None)

    assert output[3, 3] == 255
    assert output[2, 3] == 255 or output[3, 2] == 255


def test_distance_returns_uint8_distance_transform():
    img = np.zeros((9, 9), dtype=np.uint8)
    img[3:6, 3:6] = 255
    parameters = {
        'preprocess': {
            'distance': {'normalise': True}
        }
    }

    output = pm.distance(img, parameters=parameters, section='preprocess', call_num=None)

    assert output.dtype == np.uint8
    assert output.max() > 0


def test_erosion_reduces_binary_regions():
    img = np.zeros((7, 7), dtype=np.uint8)
    img[2:5, 2:5] = 255
    parameters = {
        'preprocess': {
            'erosion': {'kernel': 3, 'iterations': 1}
        }
    }

    output = pm.erosion(img, parameters=parameters, section='preprocess', call_num=None)

    assert output[3, 3] == 255
    assert output[2, 2] == 0


def test_gamma_changes_pixel_values():
    img = np.full((3, 3), 64, dtype=np.uint8)
    parameters = {
        'preprocess': {
            'gamma': {'gamma': 200}
        }
    }

    output = pm.gamma(img, parameters=parameters, section='preprocess', call_num=None)

    assert output.dtype == np.uint8
    assert output[0, 0] != 64


def test_grayscale_converts_bgr_to_gray():
    img = np.zeros((2, 2, 3), dtype=np.uint8)
    img[:, :, 0] = 10
    img[:, :, 1] = 20
    img[:, :, 2] = 30

    output = pm.grayscale(img)

    assert output.shape == (2, 2)
    assert output.dtype == np.uint8


def test_invert_flips_pixel_values():
    img = np.array([[0, 255]], dtype=np.uint8)

    output = pm.invert(img)

    assert np.array_equal(output, np.array([[255, 0]], dtype=np.uint8))


def test_medianblur_removes_single_pixel_noise():
    img = np.zeros((5, 5), dtype=np.uint8)
    img[2, 2] = 255
    parameters = {
        'preprocess': {
            'medianblur': {'kernel': 3}
        }
    }

    output = pm.medianblur(img, parameters=parameters, section='preprocess', call_num=None)

    assert output[2, 2] == 0


def test_threshold_produces_binary_image():
    img = np.array([[50, 150], [200, 25]], dtype=np.uint8)
    parameters = {
        'preprocess': {
            'threshold': {'threshold': 100, 'invert': False}
        }
    }

    output = pm.threshold(img, parameters=parameters, section='preprocess', call_num=None)

    assert set(np.unique(output)).issubset({0, 255})


def test_fill_holes_fills_enclosed_hole():
    img = np.zeros((7, 7), dtype=np.uint8)
    img[1:6, 1:6] = 255
    img[3, 3] = 0

    output = pm.fill_holes(img)

    assert output[3, 3] == 255


def test_absolute_diff_computes_correct_difference():
    img = np.array([[100, 150]], dtype=np.uint8)
    parameters = {
        'preprocess': {
            'absolute_diff': {'value': 120, 'normalise': False}
        }
    }

    output = pm.absolute_diff(img, parameters=parameters, section='preprocess', call_num=None)

    assert output.shape == img.shape
    assert output.dtype == np.uint8
    assert not np.array_equal(output, img)


def test_subtract_bkg_mean_subtracts_image_mean():
    img = np.full((4, 4), 50, dtype=np.uint8)
    parameters = {
        'preprocess': {
            'subtract_bkg': {
                'subtract_bkg_type': ['mean', ('mean', 'median', 'grayscale', 'red', 'green', 'blue')],
                'subtract_bkg_filename': None,
                'subtract_bkg_blur_kernel': [3, 1, 5, 2],
                'subtract_bkg_invert': [False, ('True', 'False')],
                'subtract_bkg_norm': [False, ('True', 'False')],
            }
        }
    }

    output = pm.subtract_bkg(img, parameters=parameters)

    assert np.all(output == 0)


def test_subtract_bkg_file_background_uses_black_image(tmp_path):
    img = np.full((4, 4), 100, dtype=np.uint8)
    background_path = tmp_path / 'background.png'
    background = np.zeros((4, 4, 3), dtype=np.uint8)
    cv2.imwrite(str(background_path), background)

    parameters = {
        'preprocess': {
            'subtract_bkg': {
                'subtract_bkg_type': ['grayscale', ('mean', 'median', 'grayscale', 'red', 'green', 'blue')],
                'subtract_bkg_filename': 'background.png',
                'subtract_bkg_blur_kernel': [3, 1, 5, 2],
                'subtract_bkg_invert': [False, ('True', 'False')],
                'subtract_bkg_norm': [False, ('True', 'False')],
            }
        },
        'crop': {'crop_box': None},
        'config': {'_video_filename': str(tmp_path / 'video.mp4')},
    }

    output = pm.subtract_bkg(img, parameters=parameters)

    assert np.array_equal(output, img)
