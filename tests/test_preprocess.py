

import pandas as pd
import numpy as np
import cv2
import os
import sys  # import os
import shutil
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from labvision.images.basics import display
import particletracker as pt
import particletracker.preprocess.preprocessing_methods as pm


def test_subtract_mean_bkg():
    """Testing that mean bkg subtraction works in particle tracker"""
    
    temp_dir = "testdata/_temp"

    if os.path.exists(temp_dir):
        # Attempt to delete the folder before the test runs
        shutil.rmtree(temp_dir, ignore_errors=True)
    
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
    temp_dir = "testdata/_temp"
    if os.path.exists(temp_dir):
        # Attempt to delete the folder before the test runs
        shutil.rmtree(temp_dir, ignore_errors=True)


    parameters = {}
    parameters['preprocess'] = {'subtract_bkg': {'subtract_bkg_type': ['grayscale', ('mean', 'median', 'grayscale', 'red', 'green', 'blue')],
                                                 'subtract_bkg_filename': "testdata/bkg_test.png",
                                                 'subtract_bkg_blur_kernel': [3, 1, 15, 2],
                                                 'subtract_bkg_invert': [True, ('True', 'False')],
                                                 'subtract_bkg_norm': [True, ('True', 'False')]
                                                 }}
    parameters['crop'] = {'crop_box': None}
    parameters['config'] = {'_video_filename': "filename.mp4"}

    img = cv2.imread("testdata/bkg_test.png")[:, :, 0]
    new_img = pm.subtract_bkg(img, parameters=parameters)
    
    assert new_img[0, 0] == 0, "img bkg subtraction fails"
    assert new_img[300, 403] == 0, "img bkg subtraction fails"


def test_preprocess():
    """Testing the preprocessing methods

    This test loads up all the preprocessing methods and crudely tests that they work.
    colour_channel, grayscale, blur, median_blur, threshold, adaptive_threshold,
    erode, dilate, absolute_diff, subtract_bkg, gamma, brightness_contrast, distance, invert
    """
    temp_dir = "testdata/_temp"
    output_video = "testdata/colloids_annotate.mp4"
    output_df = "testdata/colloids.hdf5"

    if os.path.exists(temp_dir):
        # Attempt to delete the folder before the test runs
        shutil.rmtree(temp_dir, ignore_errors=True)

    pt.batchprocess("testdata/colloids.mp4", "testdata/test_preprocess.param")
    
    df = pd.read_hdf(output_df)
    assert os.path.exists(output_video), 'Preprocessing steps errored'
    
    os.remove(output_video)
    os.remove(output_df)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)