import numpy as np
import cv2
from labvision.images.basics import display

def bgr_2_grayscale(img):
    """Converts a BGR image to grayscale"""
    sz = np.shape(img)
    if np.shape(sz)[0] == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if np.shape(sz)[0] == 2:
        print('Image is already grayscale')
        return img

def stack_3(img):
    """Stacks a grayscale image to 3 depths so that coloured objects
    can be drawn on top"""
    im = np.dstack((img, img, img))
    return im

def get_depth(img):
    shp = np.shape(img)
    if len(shp) == 2:
        return 1
    else:
        return shp[2]

def grayscale_2_bgr(img):
    if len(np.shape(img)) == 3:
        return img
    else:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

def hstack(*args):
    """
    Stacks images horizontally

    If image depths are mismatched then converts grayscale images to bgr before stacking
    """
    depths = [get_depth(im) for im in args]
    gray = [d == 1 for d in depths]
    if all(gray):
        return np.hstack(args)
    else:
        ims = [grayscale_2_bgr(im) for im in args]
        return np.hstack(ims)

def bgr_to_rgb(img):
    '''BGR or RGB that is the question. Opencv
    and PyQT have a different answer so convert
    the opencv images prior to sending to
    PyQT so that gui and exported things look
    the same.'''
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)