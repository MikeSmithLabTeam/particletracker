import numpy as np

from ..customexceptions import *
from ..user_methods import *

'''
---------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------
Intensity methods
These methods should receive a masked image and return a single numerical value
The methods are invoked by setting the "get_intensities" option in the appropriate
tracking algorithm.
-----------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------
'''
@error_handling
def mean_intensity(masked_img):
    mean_intensity =  np.mean(masked_img)
    return mean_intensity

@error_handling
def red_blue(masked_img):
    from labvision.images.basics import display
    red_img = masked_img[:,:,0]
    blue_img = masked_img[:,:,2]
    new_img = cv2.subtract(red_img, blue_img)
    display(new_img)
        
    