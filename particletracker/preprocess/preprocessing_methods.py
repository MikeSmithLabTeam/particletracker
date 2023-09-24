from cgi import parse_multipart
import cv2
import numpy as np

from labvision.images import bgr_to_gray

from ..general.parameters import  param_parse, get_param_val, get_method_key
from ..crop import crop
from ..customexceptions import error_handling
from ..user_methods import *

@error_handling
@param_parse
def adaptive_threshold(frame, parameters=None, *args, **kwargs):
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
    ad_mode
        Inverts behaviour (True or False)

    Args
    ----
    frame
        This is must be a grayscale / single colour channel image
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        binary image with 255 above threshold else 0.
    '''
    if parameters['ad_mode']:
        out = cv2.adaptiveThreshold(frame,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, parameters['block_size'], parameters['C'])
    else:
        out = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, parameters['block_size'], parameters['C'])
    return out
    
@error_handling
@param_parse
def blur(frame, parameters=None, *args, **kwargs):
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
    frame
        This must be a grayscale / single colour channel image
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        single colour channel image.

    '''    
    out = cv2.GaussianBlur(frame, (parameters['kernel'], parameters['kernel']), 0)
    return out      


@error_handling
@param_parse
def brightness_contrast(frame, parameters=None, *args, **kwargs):
    """Brightness and Contrast control
    
    This is implemented as g(x) = contrast * f(x) + brightness
    
    but with checks to make sure the values don't fall outside 0-255"""

    return  cv2.convertScaleAbs(frame, alpha=parameters['contrast'], beta=parameters['brightness'])


@error_handling
@param_parse
def colour_channel(frame, parameters=None, *args, **kwargs):
    '''
    This selects the specified colour channel of a colour image
    
    
    colour
        options are 'red', 'green', 'blue', We assume frame has (blue, green, red) format which is OpenCVs default. 

    Args
    ----
    frame
        This must be a colour / single colour channel image
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        Single colour channel image

    '''
    #Assumes frame has bgr format.
    if parameters['colour'] == 'red':
        index = 2
    elif parameters['colour'] == 'green':
        index = 1
    elif parameters['colour'] == 'blue':
        index = 0
    else:
        raise Exception        
    return frame[:,:,index]
        
@error_handling
@param_parse
def dilation(frame, parameters=None, *args, **kwargs):
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
    frame
        This must be a binary image (8 bit)
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        binary image 

    '''
    return cv2.dilate(frame, parameters['dilation_kernel'], iterations=parameters['iterations'])

@error_handling       
def distance(frame, *args, **kwargs):
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
    frame
        This must be a binary image (8 bit)
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        Grayscale image

    '''
    dist = cv2.distanceTransform(frame, cv2.DIST_L2, 5)
    dist = 255*dist/np.max(dist)
    return dist.astype(np.uint8)

@error_handling
@param_parse
def erosion(frame, parameters=None, *args, **kwargs):
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
    frame
        This must be a binary image (8 bit)
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        binary image with 255 above threshold else 0.

    '''

    kernel = parameters['erosion_kernel']
    return cv2.erode(frame, np.ones((kernel, kernel)), iterations=iterations)
       
@error_handling
@param_parse
def gamma(image, parameters=None, *args, **kwargs):
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
    frame
        This is must be a grayscale / single colour channel image
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        grayscale image

    '''
    gamma = parameters['gamma']
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    if gamma == 0:
        gamma = 0.000001
    invGamma = 1.0 / gamma

    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")

    return cv2.LUT(image, table)

@error_handling
def grayscale(frame, *args, **kwargs):
    '''
    This converts a colour image to a grayscale image

    Args
    ----
    frame
        This should be a colour image though won't error if given grayscale
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        grayscale image

    '''
    sz = np.shape(frame)

    if np.size(sz) == 3:
        frame= cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return frame

@error_handling    
def invert(frame, *args, **kwargs):
    '''
    Invert image


    Notes
    -----    
    This inverts the supplied image. It will work with any kind of image (colour, grayscale, binary). The result
    for an 8bit image at each pixel is just 255 - currentvalue.


    Args
    ----
    frame
        will receive any type of image
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        same as input image

    '''
    return ~frame
           
@error_handling
@param_parse
def medianblur(frame, parameters=None, *args, **kwargs):
    '''
    Performs a medianblur on the image. 
    
    Notes
    -----
    Setting each pixel to median value in the area specified by the kernel.

    kernel
        An integer value n that specifies kernel shape (n,n)

    Args
    ----
    frame
        This is must be a grayscale / single colour channel image
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        grayscale image

    '''
    out = cv2.medianBlur(frame, parameters['kernel'])
    return out
        
@error_handling
def subtract_bkg(frame, parameters=None, call_num=None):
    '''
    Subtract a background


    This method doesn't use param_parse because it needs access to 
    the complete parameters dictionary. param_parse only passes the bit
    defined for each method.

    Notes
    -----
    This function will subtract a background from the image. It has several 
    options: mean will subtract the average value from the image. img will subtract a preprepared
    background img from the img. Before subtracting the background image it is blurred according to
    the settings. 
    
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
    frame
        This must be a grayscale / single colour channel image
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        grayscale image

'''
    method_key = get_method_key('subtract_bkg', call_num=call_num)
    params = parameters['preprocess'][method_key]

    bkgtype = get_param_val(params['subtract_bkg_type'])
    if  bkgtype == 'mean':
        mean_val = int(np.mean(frame))
        subtract_frame = mean_val * np.ones(np.shape(frame), dtype=np.uint8)
        frame2=frame
    elif bkgtype == 'median':
        median_val = int(np.median(frame))
        subtract_frame = median_val * np.ones(np.shape(frame), dtype=np.uint8)
        frame2=frame
    else:
        # This option subtracts the previously created image which is added to dictionary.
        #These parameters are fed to the blur function
        temp_params = {}
        temp_params['preprocess'] = {
            'blur': {'kernel': get_param_val(params['subtract_bkg_blur_kernel'])}}
        #Load bkg img
        if params['subtract_bkg_filename'] is None:
            name = parameters['experiment']['video_filename']
            bkg_frame = cv2.imread(name[:-4] + '_bkgimg.png')#,cv2.IMREAD_GRAYSCALE)
        else:
            bkg_frame = cv2.imread(params['subtract_bkg_filename'])#,cv2.IMREAD_GRAYSCALE)
        
        if bkgtype == 'grayscale':
            subtract_frame = bgr_to_gray(bkg_frame)
        elif bkgtype == 'red':
            subtract_frame = bkg_frame[:,:,2]
        elif bkgtype == 'green':
            subtract_frame = bkg_frame[:,:,1]
        elif bkgtype == 'blue':
            subtract_frame = bkg_frame[:,:,0]

        subtract_frame = crop(subtract_frame, parameters['crop'])
        
        frame2 = blur(frame, temp_params)
        frame2 = frame2.astype(np.uint8)
        subtract_frame  = blur(subtract_frame, temp_params)
        subtract_frame =subtract_frame.astype(np.uint8)

    if get_param_val(params['subtract_bkg_invert']):
        frame2 = cv2.subtract(subtract_frame, frame2)
    else:
        frame2 = cv2.subtract(frame2, subtract_frame)

    if np.max(frame) == 0:
        frame2 = frame

    if get_param_val(params['subtract_bkg_norm'])==True:
        frame2 = cv2.normalize(frame2, None, alpha=0, beta=255,
                            norm_type=cv2.NORM_MINMAX)

    return frame2

@error_handling
@param_parse
def threshold(frame, parameters=None, *args, **kwargs):
    '''
    Apply a global threshold

    This applies OpenCVs threshold. This sets pixels to 255 or 0 depending on whether
    they are above or below the given value.
    
    threshold
        Threshold value to determine whether pixels are black or white
    th_mode
        True or False to specify whether above threshold is white or black.

    
    Args
    ----
    frame
        This is must be a grayscale / single colour channel image
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        grayscale image

    '''
    ret, out = cv2.threshold(frame,parameters['threshold'],255,int(parameters['th_mode']))
    return out

@error_handling
def fill_holes(frame, *args, **kwargs):
    '''
    Fills holes in a binary image.

    Notes
    -----
    This function uses a combination of flood fills to fill in enclosed holes in 
    objects in a binary image.

    Args
    ----
    frame
        This is must be a binary image
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        binary image

    '''

    im_floodfill = frame.copy()
    h, w = frame.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    cv2.floodFill(im_floodfill, mask, (0,0), 255)
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)
    out = frame | im_floodfill_inv
    return out

@error_handling   
@param_parse    
def absolute_diff(frame, parameters=None, *args, **kwargs):
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
    frame
        This is must be a grayscale / single colour channel image
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        grayscale image
    '''
    mean_val = int(parameters['value'])
    subtract_frame = mean_val*np.ones(np.shape(frame), dtype=np.uint8)         

    frame1 = cv2.subtract(subtract_frame, frame)
    frame1 = cv2.normalize(frame1, frame1 ,0,255,cv2.NORM_MINMAX)
    frame2 = cv2.subtract(frame, subtract_frame)
    frame2 = cv2.normalize(frame2, frame2,0,255,cv2.NORM_MINMAX)
    frame = cv2.add(frame1, frame2)

    if parameters['normalise'] == True:
        frame = cv2.normalize(frame, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    return frame
       
