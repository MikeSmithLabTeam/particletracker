import numpy as np

from ..customexceptions.track_error import *
from ..user_methods import *

'''
---------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------
Intensity methods
These methods should receive a masked grayscale image and return a single numerical value
The methods are invoked by setting the "get_intensities" option in the appropriate
tracking algorithm.
-----------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------
'''

def mean_intensity(masked_img):
    
    try:
        mean_intensity =  np.mean(masked_img)
        return mean_intensity
    except Exception as e:
        raise MeanIntensityError