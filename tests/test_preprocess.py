
from labvision.images.basics import display
import particletracker.preprocess.preprocessing_methods as pm
import pandas as pd
import numpy as np
import cv2
import os
import sys  # import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def test_subtract_mean_bkg():
    """Testing that mean bkg subtraction works in particle tracker"""
    parameters = {}
    parameters['preprocess'] = {'subtract_bkg': {'subtract_bkg_type': ['mean', ('mean', 'median', 'grayscale', 'red', 'green', 'blue')],
                                                 'subtract_bkg_filename': None,
                                                 'subtract_bkg_blur_kernel': [3, 1, 15, 2],
                                                 'subtract_bkg_invert': [True, ('True', 'False')],
                                                 'subtract_bkg_norm': [True, ('True', 'False')]
                                                 }}

    img = cv2.imread("testdata/bkg_test.png")
    new_img = pm.subtract_bkg(img, parameters=parameters)
    assert new_img[179, 348, 0] == 65, "mean bkg subtraction fails"


def test_subtract_bkg_img():
    """Testing that bkg_img subtraction works in particle tracker"""
    parameters = {}
    parameters['preprocess'] = {'subtract_bkg': {'subtract_bkg_type': ['grayscale', ('mean', 'median', 'grayscale', 'red', 'green', 'blue')],
                                                 'subtract_bkg_filename': "testdata/bkg_test.png",
                                                 'subtract_bkg_blur_kernel': [3, 1, 15, 2],
                                                 'subtract_bkg_invert': [True, ('True', 'False')],
                                                 'subtract_bkg_norm': [True, ('True', 'False')]
                                                 }}
    parameters['crop'] = {'crop_box': None}

    img = cv2.imread("testdata/bkg_test2.png")[:, :, 0]
    new_img = pm.subtract_bkg(img, parameters=parameters)
    
    assert new_img[0, 0] == 0, "img bkg subtraction fails"
    assert new_img[198, 403] == 243, "img bkg subtraction fails"
