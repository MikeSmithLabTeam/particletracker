import cv2
import numpy as np

from labvision.images import display

from ..general.parameters import  get_param_val, get_method_key
from ..crop import crop
from ..customexceptions.preprocessor_error import *
from ..user_methods import *

def adaptive_threshold(frame, parameters=None, call_num=None):
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
    
    try:
        method_key = get_method_key('adaptive_threshold', call_num=call_num)
        params = parameters['preprocess'][method_key]
        block = get_param_val(params['block_size'])
        const = get_param_val(params['C'])
        invert = get_param_val(params['ad_mode'])

    
        if invert:
            out = cv2.adaptiveThreshold(frame,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block, const)
        else:
            out = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block, const)
        return out
    except Exception as e:
        raise AdaptiveThresholdError(e)

def blur(frame, parameters=None, call_num=None):
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
    
    try:
        method_key = get_method_key('blur', call_num=call_num)
        params = parameters['preprocess'][method_key]
        kernel = get_param_val(params['kernel'])
       
        out = cv2.GaussianBlur(frame, (kernel, kernel), 0)
        return out
    except Exception as e:
        raise BlurError(e)
        

def colour_channel(frame, parameters=None, call_num=None):
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

    try:
        if np.size(np.shape(frame)) == 3:
            method_key = get_method_key('colour_channel', call_num=call_num)
            params = get_param_val(parameters['preprocess'][method_key])
            colour = get_param_val(params['colour'])
        
            #Assumes frame has bgr format.
            if colour == 'red':
                index = 2
            elif colour == 'green':
                index = 1
            elif colour == 'blue':
                index = 0
            else:
                raise Exception        
        return frame[:,:,index]
    except Exception as e:
        raise ColorChannelError(e)
        

def dilation(frame, parameters=None, call_num=None):
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
    try:
        method_key = get_method_key('dilation', call_num=call_num)
        params = parameters['preprocess'][method_key]
        kernel = get_param_val(params['dilation_kernel'])
        iterations = get_param_val(params['iterations'])

        kernel = np.ones((kernel, kernel))
    
        return cv2.dilate(frame, kernel, iterations=iterations)
    except Exception as e:
        raise DilationError(e)
        
def distance(frame, parameters=None, call_num=None):
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
    try:
        dist = cv2.distanceTransform(frame, cv2.DIST_L2, 5)
        dist = 255*dist/np.max(dist)
        return dist.astype(np.uint8)
    except Exception as e:
        raise DistanceError(e)
     

def erosion(frame, parameters=None, call_num=None):
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
    try:
        method_key = get_method_key('erosion', call_num=call_num)
        params = parameters['preprocess'][method_key]
        kernel = get_param_val(params['erosion_kernel'])
        iterations = get_param_val(params['iterations'])

        kernel = np.ones((kernel, kernel))
    
        return cv2.erode(frame, kernel, iterations=iterations)
    except Exception as e:
        raise ErosionError(e)
        

def gamma(image, parameters=None, call_num=None):
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
    try:
        method_key = get_method_key('gamma', call_num=call_num)
        params = parameters['preprocess'][method_key]

        gamma = get_param_val(params['gamma'])
        # build a lookup table mapping the pixel values [0, 255] to
        # their adjusted gamma values
        invGamma = 1.0 / gamma

        table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")

    
        return cv2.LUT(image, table)
    except Exception as e:
        raise GammaError(e)

def grayscale(frame, parameters=None, call_num=None):
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
    
    try:
        method_key = get_method_key('grayscale', call_num=call_num)
        params = parameters['preprocess'][method_key]
        
        sz = np.shape(frame)
    
        if np.size(sz) == 3:
            frame= cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return frame
    except Exception as e:
          raise GrayscaleError(e) 
    
def invert(frame, parameters=None, call_num=None):
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
    try:
        return ~frame
    except Exception as e:
        raise InvertError(e)
        

def medianblur(frame, parameters=None, call_num=None):
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
    try:
        method_key = get_method_key('medianblur', call_num=call_num)
        params = parameters['preprocess'][method_key]
        kernel = get_param_val(params['kernel'])
        out = cv2.medianBlur(frame, kernel)
        return out
    except Exception as e:
        raise MedianError(e)
        

def subtract_bkg(frame, parameters=None, call_num=None):
    '''
    Subtract a background


    Notes
    -----
    This function will subtract a background from the image. It has several 
    options: mean will subtract the average value from the image. img will subtract a preprepared
    background img from the img. Before subtracting the background image it is blurred according to
    the settings.


    

    subtract_bkg_type
        Type of background substraction to be performed. Options are are 'mean' or 'img'. 
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
        This is must be a grayscale / single colour channel image
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        grayscale image

    '''
    
    try:
        method_key = get_method_key('subtract_bkg', call_num=call_num)
        params = parameters['preprocess'][method_key]
    
        bkgtype = get_param_val(params['subtract_bkg_type'])
        if  bkgtype == 'mean':
            mean_val = int(np.mean(frame))
            subtract_frame = mean_val * np.ones(np.shape(frame), dtype=np.uint8)
            frame2=frame
        elif bkgtype == 'image':
            # This option subtracts the previously created image which is added to dictionary.
            #These parameters are fed to the blur function
            temp_params = {}
            temp_params['preprocess'] = {
                'blur': {'kernel': get_param_val(params['subtract_bkg_blur_kernel'])}}
            #Load bkg img
            if params['subtract_bkg_filename'] is None:
                name = parameters['experiment']['video_filename']
                subtract_frame = cv2.imread(name[:-4] + '_bkgimg.png',cv2.IMREAD_GRAYSCALE)
            else:
                subtract_frame = cv2.imread(params['subtract_bkg_filename'],cv2.IMREAD_GRAYSCALE)
         
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
    except Exception as e:
        print(e)
        raise SubtractBkgError(e)
       

def threshold(frame, parameters=None, call_num=None):
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
    try:
        method_key = get_method_key('threshold', call_num=call_num)
        params = parameters['preprocess'][method_key]
        threshold = get_param_val(params['threshold'])
        mode = get_param_val(params['th_mode'])
        if mode:
            ret, out = cv2.threshold(frame,threshold,255,1)
        else:
            ret, out = cv2.threshold(frame,threshold,255,0)
        return out
    except Exception as e:
        raise ThresholdError(e)
       
def absolute_diff(frame, parameters=None, call_num=None):
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
    variance_norm
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
    try:    
        method_key = get_method_key('variance', call_num=call_num)
        params = parameters['preprocess'][method_key]
        mean_val = int(get_param_val(params['value']))
        subtract_frame = mean_val*np.ones(np.shape(frame), dtype=np.uint8)         

        frame1 = cv2.subtract(subtract_frame, frame)
        frame1 = cv2.normalize(frame1, frame1 ,0,255,cv2.NORM_MINMAX)
        frame2 = cv2.subtract(frame, subtract_frame)
        frame2 = cv2.normalize(frame2, frame2,0,255,cv2.NORM_MINMAX)
        frame = cv2.add(frame1, frame2)

        if get_param_val(params['variance_norm']) == True:
            frame = cv2.normalize(frame, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

        return frame
    except Exception as e:
        raise AbsDiffError(e)
        
