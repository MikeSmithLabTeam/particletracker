import os
import sys
import cv2
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import cv2
from particletracker.preprocess.preprocessing_methods import subtract_bkg
from labvision.images.basics import display


                    


def test_subtract_mean_bkg():
    """Testing that mean bkg subtraction works in particle tracker"""
    parameters = {}
    parameters['preprocess'] = {'subtract_bkg' : {'subtract_bkg_type':['mean',('mean','median','grayscale','red','green','blue')],
                                                'subtract_bkg_filename':None,
                                                'subtract_bkg_blur_kernel': [3,1,15,2],
                                                'subtract_bkg_invert':[True,('True','False')],
                                                'subtract_bkg_norm':[True,('True','False')]
                                                }}


    img = cv2.imread("testdata/bkg_test.png")
    new_img = subtract_bkg(img, parameters=parameters)
    assert new_img[179, 348, 0] == 65, "mean bkg subtraction fails"

def test_subtract_bkg_img():
    """Testing that mean bkg subtraction works in particle tracker"""
    parameters = {}
    parameters['preprocess'] = {'subtract_bkg' : {'subtract_bkg_type':['grayscale',('mean','median','grayscale','red','green','blue')],
                                                'subtract_bkg_filename':"bkg_test2.png",
                                                'subtract_bkg_blur_kernel': [3,1,15,2],
                                                'subtract_bkg_invert':[True,('True','False')],
                                                'subtract_bkg_norm':[True,('True','False')]
                                                }}


    img = cv2.imread("testdata/bkg_test.png")
    new_img = subtract_bkg(img, parameters=parameters)
    print(new_img[190,348, 0])
    #assert new_img[179, 348, 0] == 65, "mean bkg subtraction fails"



