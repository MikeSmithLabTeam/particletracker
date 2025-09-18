from cgi import parse_multipart
import cv2
import numpy as np
import os


import labvision.images.transforms as transforms
import labvision.images.morphological as morphological
import labvision.images.blurs as blurs
import labvision.images.thresholds as thresholds
import labvision.images.colours as colours


from ..general.parameters import param_parse, get_param_val, get_method_key
from ..crop import crop
from ..customexceptions import error_handling
from ..user_methods import *
from ..gui.file_io import img_name_wrangle


@error_handling
@param_parse
def adaptive_threshold(img, parameters=None, *args, **kwargs):
    '''
    Perform an adaptive threshold on a grayscale image

    Notes
    -----
    This applies OpenCVs adaptive threshold. This differs from global threshold
    in that for each pixel the cutoff threshold is defined based on a block of local
    pixels around it. This enables you to cope with gradual changes in illumination
    across the image etc.

    block_size
        Size of local block of pixels to calculate threshold on
    C
        The mean-c value see here: http://homepages.inf.ed.ac.uk/rbf/HIPR2/adpthrsh.htm
    invert
        Inverts behaviour (True or False)

    Args
    ----
    img
        This is must be a grayscale / single colour channel image
    parameters
        dictionary like object corresponding to specific method. See param_parse for details.


    Returns
    -------
        binary image with 255 above threshold else 0.
    '''
    bw_img = thresholds.adaptive_threshold(
        img, block_size=parameters['block_size'], constant=parameters['C'], invert=parameters['invert'])
    return bw_img


@error_handling
def blur(img, parameters=None, **kwargs):
    '''
    Performs a gaussian blur on the image

    Notes
    -----
    This applies OpenCVs gaussian blur to the image (https://en.wikipedia.org/wiki/Gaussian_blur)
    Usually useful to apply before subtracting 2 images.

    blur_kernel
        single integer n specifying the size of kernel (n,n) 

    Args
    ----
    img
        This must be a grayscale / single colour channel image
    parameters
        dictionary like object corresponding to specific method. See param_parse for details.

    Returns
    -------
        single colour channel image.

    '''
    method_key = get_method_key('blur', call_num=kwargs['call_num'])
    params = get_param_val(parameters['preprocess'][method_key]['kernel'])
    gray_img = blurs.gaussian_blur(img, kernel=(params, params))
    return gray_img


@error_handling
@param_parse
def brightness_contrast(img, parameters=None, *args, **kwargs):
    """Brightness and Contrast control

    This is implemented as g(x) = contrast * f(x) + brightness

    but with checks to make sure the values don't fall outside 0-255

    Args
    ----
    img
        This must be a grayscale / single colour channel image
    parameters
        dictionary like object corresponding to specific method. See param_parse for details.

    Returns
    -------
        single colour channel image.
    """

    return transforms.brightness_contrast(img, brightness=parameters['brightness'], contrast=parameters['contrast'])


@error_handling
@param_parse
def colour_channel(img, parameters=None, *args, **kwargs):
    '''
    This selects the specified colour channel of a colour image


    colour
        options are 'red', 'green', 'blue', We assume img has (blue, green, red) format which is OpenCVs default. 

    Args
    ----
    img
        This must be a colour / single colour channel image
    parameters
        dictionary like object corresponding to specific method. See param_parse for details.

    Returns
    -------
        Single colour channel image

    '''
    # Assumes frame has bgr format.
    if parameters['colour'] == 'red':
        index = 2
    elif parameters['colour'] == 'green':
        index = 1
    elif parameters['colour'] == 'blue':
        index = 0
    else:
        raise Exception
    return img[:, :, index]


@error_handling
@param_parse
def dilation(img, parameters=None, *args, **kwargs):
    '''
    Dilate a binary image

    This performs a dilation operation on a binary image. Dilation adds
    pixels to the edge of white regions according to the kernel and is
    useful for closing small holes or gaps.
    See an explanation -  https://en.wikipedia.org/wiki/Dilation_(morphology)



    dilation_kernel
        single integer n specifying dimension of kernel (n,n)
    iterations
        how many times to apply the operation


    Args
    ----
    img
        This must be a binary image (8 bit)
    parameters
        dictionary like object corresponding to specific method. See param_parse for details.

    Returns
    -------
        binary image 

    '''
    return morphological.dilate(img, kernel=parameters['kernel'], iterations=parameters['iterations'])


@error_handling
@param_parse
def distance(img, parameters=None, *args, **kwargs):
    '''
    Perform a distance transform on a binary image

    Notes
    -----
    Implements the opencv distance transform. This transform operates on a binary image. 
    For each chosen white pixel it calculates the distance to the nearest black pixel. This
    distance is the value of the chosen pixel. Thus if operating on
    a white circle the distance transform is a maximum at the middle and
    1 at the perimeter.

    See here for explanation : https://en.wikipedia.org/wiki/Distance_transform


    Args
    ----
    img
        This must be a binary image (8 bit)


    Returns
    -------
        Grayscale image

    '''
    img = transforms.distance(
        img, normalise=parameters['normalise']).astype(np.uint8)
    return img


@error_handling
@param_parse
def erosion(img, parameters=None, *args, **kwargs):
    '''
    Perform an erosion operation on a binary image


    Notes
    -----
    This performs an erosion operation on a binary image.
    This means pixels are set to zero based on their connectivity with neighbours
    Useful for separating objects and removing small pepper noise.

    See an explanation -  https://en.wikipedia.org/wiki/Erosion_(morphology)

    Parameters:

    erosion_kernel :   single integer n specifying dimension of kernel (n,n)
    iterations      :   how many times to apply the operation


    Args
    ----
    img
        This must be a binary image (8 bit)
    parameters
        dictionary like object corresponding to specific method. See param_parse for details.

    Returns
    -------
        binary image with 255 above threshold else 0.

    '''

    kernel = parameters['kernel']
    print(parameters['iterations'])
    return morphological.erode(img, kernel=kernel, iterations=parameters['iterations'])


@error_handling
@param_parse
def gamma(img, parameters=None, *args, **kwargs):
    '''
    Apply look up table to image with power gamma

    Notes
    -----
    This generates a lookup table which maps the values 0-255 to 0-255
    however not in a linear way. The mapping follows a power law
    with exponent gamma/100.0.

    gamma
        single float can be positive or negative. The true value applied is the displayed value / 100.

    Args
    ----
    img
        This is must be a grayscale / single colour channel image
    parameters
        dictionary like object corresponding to specific method. See param_parse for details.

    Returns
    -------
        grayscale image

    '''
    return transforms.gamma(img, gamma=parameters['gamma'])


@error_handling
def grayscale(img, *args, **kwargs):
    '''
    This converts a colour image to a grayscale image

    Args
    ----
    img
        This should be a colour image though won't error if given grayscale

    Returns
    -------
        grayscale image

    '''
    img = colours.bgr_to_gray(img)
    return img


@error_handling
def invert(img, *args, **kwargs):
    '''
    Invert image


    Notes
    -----    
    This inverts the supplied image. It will work with any kind of image (colour, grayscale, binary). The result
    for an 8bit image at each pixel is just 255 - currentvalue.


    Args
    ----
    img
        will receive any type of image

    Returns
    -------
        same as input image

    '''
    return ~img


@error_handling
@param_parse
def medianblur(img, parameters=None, *args, **kwargs):
    '''
    Performs a medianblur on the image. 

    Notes
    -----
    Setting each pixel to median value in the area specified by the kernel.

    kernel
        An integer value n that specifies kernel shape (n,n)

    Args
    ----
    img
        This is must be a grayscale / single colour channel image
    parameters
        dictionary like object corresponding to specific method. See param_parse for details.

    Returns
    -------
        grayscale image

    '''
    kernel = parameters['kernel']
    gray_img = blurs.median_blur(img, kernel=kernel)
    return gray_img


@error_handling
def subtract_bkg(img, *args, parameters=None, call_num=None, **kwargs):
    '''
    Subtract a background

    This method doesn't use @param_parse because it needs access to 
    the complete parameters dictionary. @param_parse only passes the bit
    defined for each method.

    Notes
    -----
    This function will subtract a background from the image. It has several 
    options: mean / median will subtract the mean / median value from the image. 
    img will subtract a preprepared background img from the img. Before subtracting the background image it is blurred according to the settings. 

    N.B. You must apply either a grayscale or color_channel method before the subtract_bkg method. 
    The software subtracts the mean image value, grayscale or color_channel version of the background image which you select from the current image.

    subtract_bkg_type
        Type of background substraction to be performed. Options are are 'mean' or 'grayscale','red','green','blue'. 
    subtract_bkg_filename
        filename of background image. If None it will look for a file named moviefilename_bkgimg.png. Otherwise it looks for the filename specified. The filename is assumed to be in the same directory as the movie. Alternatively specify the full path to the file. 
    subtract_bkg_blur_kernel
        An integer n specifying the kernel size (n,n) to be used in blurring bkg image
    subtract_bkg_invert
        Subtract bkg from image or image from background.
    subtract_bkg_norm
        Stretch range of outputted intensities on resultant image to fill 0-255 - True or False               


    Args
    ----
    img
        This must be a grayscale / single colour channel image
    parameters
        dictionary like object corresponding to specific method. See param_parse for details.

    Returns
    -------
        grayscale image

'''
    method_key = get_method_key('subtract_bkg', call_num=call_num)
    params = parameters['preprocess'][method_key]

    bkgtype = get_param_val(params['subtract_bkg_type'])
    if bkgtype == 'mean':
        mean_val = int(np.mean(img))
        subtract_img = mean_val * np.ones(np.shape(img), dtype=np.uint8)
        img2 = img
    elif bkgtype == 'median':
        median_val = int(np.median(img))
        subtract_img = median_val * np.ones(np.shape(img), dtype=np.uint8)
        img2 = img
    else:
        # This option subtracts the previously created image which is added to dictionary.
        # These parameters are fed to the blur function
        temp_params = {}
        temp_params['preprocess'] = {
            'blur': {'kernel': get_param_val(params['subtract_bkg_blur_kernel'])}}
        # Load bkg img
        name = parameters['config']['_video_filename']
        if params['subtract_bkg_filename'] is None:
            path, filename_stub, _ = img_name_wrangle(name)
            bkg_img = cv2.imread(os.path.join(
                path, filename_stub + '_bkgimg.png'))
        else:
            path, _ = os.path.split(name)
            bkg_img = cv2.imread(os.path.join(
                path, params['subtract_bkg_filename']))

        if bkgtype == 'grayscale':
            subtract_img = colours.bgr_to_gray(bkg_img)
        elif bkgtype == 'red':
            subtract_img = bkg_img[:, :, 2]
        elif bkgtype == 'green':
            subtract_img = bkg_img[:, :, 1]
        elif bkgtype == 'blue':
            subtract_img = bkg_img[:, :, 0]

        subtract_img = crop(subtract_img, parameters['crop'])
        img2 = blur(img, temp_params, call_num=None)
        img2 = img2.astype(np.uint8)
        subtract_img = blur(subtract_img, temp_params, call_num=None)
        subtract_img = subtract_img.astype(np.uint8)

    if get_param_val(params['subtract_bkg_invert']):
        img2 = cv2.subtract(subtract_img, img2)
    else:
        img2 = cv2.subtract(img2, subtract_img)

    if np.max(img) == 0:
        img2 = img

    if get_param_val(params['subtract_bkg_norm']):
        img2 = cv2.normalize(img2, None, alpha=0, beta=255,
                             norm_type=cv2.NORM_MINMAX)

    return img2


@error_handling
@param_parse
def threshold(img, parameters=None, *args, **kwargs):
    '''
    Apply a global threshold

    This applies OpenCVs threshold. This sets pixels to 255 or 0 depending on whether
    they are above or below the given value.

    threshold
        Threshold value to determine whether pixels are black or white
    invert
        True or False to specify whether above threshold is white or black.


    Args
    ----
    img
        This is must be a grayscale / single colour channel image
    parameters
        dictionary like object corresponding to specific method. See param_parse for details.

    Returns
    -------
        binary image

    '''
    bw_img = thresholds.threshold(
        img, value=parameters['threshold'], invert=parameters['invert'])
    return bw_img


@error_handling
def fill_holes(bw_img, *args, **kwargs):
    '''
    Fills holes in a binary image.

    Notes
    -----
    This function uses a combination of flood fills to fill in enclosed holes in 
    objects in a binary image.

    Args
    ----
    img
        This is must be a binary image
    parameters
        dictionary like object corresponding to specific method. See param_parse for details.

    Returns
    -------
        binary image

    '''
    bw_img = morphological.fill_holes(bw_img)
    return bw_img


@error_handling
@param_parse
def absolute_diff(gray_img, parameters=None, *args, **kwargs):
    '''
    Calculates the absolute difference of pixels from a reference value

    Notes
    -----
    This function returns the magnitude of the difference in intensity of a pixel relative 
    to a specified value. This is often useful in brightfield microscopy if you have objects 
    slightly above and below the focal plane as one set will look darker than the background 
    and the other set will look brighted than the background.

    value
        The value to take the absolute difference relative to
    normalise
        Stretch the intensity values to the full range 0-255, True or False

    Args
    ----
    gray_img
        This is must be a grayscale / single colour channel image
    parameters
        dictionary like object corresponding to specific method. See param_parse for details.

    Returns
    -------
        grayscale image
    '''

    gray_img = transforms.absolute_diff(
        gray_img, value=parameters['value'], normalise=parameters['normalise'])
    return gray_img
