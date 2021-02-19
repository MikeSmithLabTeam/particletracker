import cv2
import numpy as np

from ..general.parameters import  get_param_val, get_method_key
from ..video_crop import crop
from labvision.images import display


def adaptive_threshold(frame, parameters=None, call_num=None):
    '''Adaptive threshold

    Notes
    -----

    This applies an adaptive threshold. This differs from global threshold
    in that for each pixel the cutoff threshold is defined based on a block of local
    pixels around it. This enables you to cope with gradual changes in illumination
    across the image etc.

    options
    ~~~~~~~

    parameters['adaptive threshold']['block size'] : Size of local block of pixels to calculate threshold on
    parameters['adaptive threshold']['C'] : The mean-c value see here: http://homepages.inf.ed.ac.uk/rbf/HIPR2/adpthrsh.htm
    parameters['adaptive threshold']['ad_mode'] : inverts behaviour

    Parameters
    ----------

    frame: np.ndarray
        frame grayscale
    parameters: dict, optional
        parameters dictionary
    call_num: int or None
        number specifying the call number to this function. allows multiple calls

    Returns
    -------

    binary image with 255 above threshold else 0.

    '''
    method_key = get_method_key('adaptive_threshold', call_num=call_num)
    params = parameters['preprocess'][method_key]
    block = get_param_val(params['block_size'])
    const = get_param_val(params['C'])
    invert = get_param_val(params['ad_mode'])

    try:
        if invert == 1:
            out = cv2.adaptiveThreshold(frame,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block, const)
        else:
            out = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block, const)
        return out, False
    except Exception as e:
        print(e)
        print('Error in preprocessing_methods.adaptive_threshold')
        return frame, True



def blur(frame, parameters=None, call_num=None):
    ''' Gaussian blur

    Notes
    -----

    Applies a gaussian blur to the image (https://en.wikipedia.org/wiki/Gaussian_blur)
    Usually useful to apply before subtracting 2 images.

    options
    ~~~~~~~

    parameters['blur kernel'] specifies the dimensions of a square kernel

    Parameters
    ----------

    frame: np.ndarray
        frame
    parameters: dict, optional
        parameters dictionary
    call_num: int or None
        number specifying the call number to this function. allows multiple calls

    Returns
    -------

    blurred image

    '''
    
    method_key = get_method_key('blur', call_num=call_num)
    params = parameters['preprocess'][method_key]
    kernel = get_param_val(params['kernel'])
    
    try:
        out = cv2.GaussianBlur(frame, (kernel, kernel), 0)
        return out, False
    except Exception as e:
        print(e)
        print('Error in preprocessing_methods.blur - Check input is grayscale')
        return frame, True

def colour_channel(frame, parameters=None, call_num=None):
    """
    This function selects a particular colour channel, returning a
     grayscale image from a colour input frame
    """
    if np.size(np.shape(frame)) == 3:
        method_key = get_method_key('colour_channel', call_num=call_num)
        params = parameters['preprocess'][method_key]
        colour = params['colour']
        colour = colour.lower()
        
        if colour == 'red':
            index = 0
        elif colour == 'green':
            index = 1
        elif colour == 'blue':
            index = 2
        else:
            print('Error in processor.colour_channel - colour channgel must be red, green or blue')
            return frame[:,:,0], False
        return frame[:,:,index], False
    else:
        print('Error in preprocessing_methods.colour_channel - frame is not colour')
        return frame, True

def dilation(frame, parameters=None, call_num=None):
    ''' Morphological erosion

    Notes
    -----

    dilates a binary image. This means pixels are set to
    zero based on their connectivity with neighbours

    options
    ~~~~~~~

    parameters['resize scale'] : factor for scale operation

    Parameters
    ----------

    frame: np.ndarray
        frame
    parameters: dict, optional
        parameters dictionary
    call_num: int or None
        number specifying the call number to this function. allows multiple calls

    Returns
    -------

        binary frame

        '''
    
    method_key = get_method_key('dilation', call_num=call_num)
    params = parameters['preprocess'][method_key]
    kernel = get_param_val(params['dilation_kernel'])
    iterations = get_param_val(params['iterations'])

    kernel = np.ones((kernel, kernel))
    try:
        return cv2.dilate(frame, kernel, iterations=iterations), False
    except Exception as e:
        print(e)
        print('Error in preprocessing_methods.dilation')
        return frame, True

def distance(frame, parameters=None, call_num=None):
    ''' Perform a distance transform on frame

    Notes
    -----
    distance implements the opencv distance transform. This
    transform operates on a binary image. For each chosen white pixel
    it calculates the distance to the nearest black pixel. This
    distance is the value of the chosen pixel. Thus if operating on
    a white circle the distance transform is a maximum at the middle and
    1 at the perimeter.

    Parameters
    ----------

    frame: np.ndarray
        binary frame on which to perform process
    parameters: dict, optional
        parameters dictionary
    call_num: int or None
        number specifying the call number to this function. allows multiple calls

    Returns
    -------
    np.ndarray - The distance transform image.

    '''
    try:
        dist = cv2.distanceTransform(frame, cv2.DIST_L2, 5)
        dist = 255*dist/np.max(dist)
        return dist.astype(np.uint8), False
    except Exception as e:
        print(e)
        print('Error in preprocessing_methods.distance - input should be just 0 & 255 binary')
        return frame, True

def erosion(frame, parameters=None, call_num=None):
    ''' Morphological erosion

    Notes
    -----

    erodes a binary image. This means pixels are set to
    zero based on their connectivity with neighbours

    options
    ~~~~~~~

    parameters['resize scale'] : factor for scale operation

    Parameters
    ----------

    frame: np.ndarray
        frame
    parameters: dict, optional
        parameters dictionary
    call_num: int or None
        number specifying the call number to this function. allows multiple calls

    Returns
    -------

        binary frame

        '''
    
    method_key = get_method_key('erosion', call_num=call_num)
    params = parameters['preprocess'][method_key]
    kernel = get_param_val(params['erosion_kernel'])
    iterations = get_param_val(params['iterations'])

    kernel = np.ones((kernel, kernel))
    try:
        return cv2.erode(frame, kernel, iterations=iterations), False
    except Exception as e:
        print(e)
        print('Error in preprocessing_methods.erosion')
        return frame, True

def gamma(image, parameters=None, call_num=None):
    ''' Gamma correction

    Notes
    -----

    generates a lookup table which maps the values 0-255 to 0-255
    however not in a linear way. The mapping follows a power law
    with exponent gamma/100.0.

    Parameters
    ----------

    frame: np.ndarray
        frame
    parameters: dict, optional
        parameters dictionary
    call_num: int or None
        number specifying the call number to this function. allows multiple calls

    Returns
    -------

    gamma corrected image

    '''
    method_key = get_method_key('gamma', call_num=call_num)
    params = parameters['preprocess'][method_key]

    gamma = get_param_val(params['gamma'])/100.0
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma

    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")

    try:
        return cv2.LUT(image, table), False
    except Exception as e:
        print(e)
        print('Error in preprocessing_methods.gamma')
        return frame, True

def grayscale(frame, parameters=None, call_num=None):
    ''' Convert colour frame to grayscale

    Notes
    -----
    Takes a colour image and applies opencvs colour to grayscale method
    cv2.cvtColor. Checks shape and dimensions of frame. Returns grayscale image
    regardless of whether input frame is colour or grayscale. If the colour depth
    is not 1 or 3 it errors.

    Parameters
    ----------

    frame: np.ndarray
        frame either colour or grayscale
    parameters: dict, optional
        parameters dictionary
    call_num: int or None
        number specifying the call number to this function. allows multiple calls

    Returns
    -------
    np.ndarray - The grayscale image

    '''
    method_key = get_method_key('grayscale', call_num=call_num)
    params = parameters['preprocess'][method_key]
        
    sz = np.shape(frame)
    
    if np.size(sz) == 2:
        #If the input is already grayscale send it back
        return frame, False
    else:
        try:
            frame= cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return frame, False
        except Exception as e:
            print(e)
            print('Error in preprocess.grayscale')
            return frame, True
    
def invert(frame, parameters=None, call_num=None):
    '''Inverts a binary frame

    Parameters
    ----------

    frame: np.ndarray
        Binary frame
    parameters: dict, optional
        parameters dictionary
    call_num: int or None
        number specifying the call number to this function. allows multiple calls

    Returns
    -------

    Inverted binary image

    '''
    try:
        return ~frame, False
    except Exception as e:
        print(e)
        print('Error in preprocessing_methods.flip')
        return frame, True



def medianblur(frame, parameters=None, call_num=None):
    '''Median blur

    Notes
    -----

    Applies a median blur to the image (https://en.wikipedia.org/wiki/Median_filter)
    Good for removing speckle noise

    options
    ~~~~~~~

    parameters['blur_kernel'] specifies the dimensions of a square kernel

    Parameters
    ----------

    frame: np.ndarray
        frame
    parameters: dict, optional
        parameters dictionary
    call_num: int or None
        number specifying the call number to this function. allows multiple calls

    Returns
    -------

    blurred image

    '''
    
    method_key = get_method_key('medianblur', call_num=call_num)
    params = parameters['preprocess'][method_key]
    kernel = get_param_val(params['kernel'])
    
    try:
        out = cv2.medianBlur(frame, kernel)
        return out, False
    except Exception as e:
        print(e)
        print('Error in preprocessing_methods.median_blur - Check input is grayscale')
        return frame, True

def subtract_bkg(frame, parameters=None, call_num=None):
    ''' Subtract a bkg image

    Notes
    -----

    This function subtracts a background image from a grayscale frame.

    options:
    parameters['subtract bkg type'] == 'mean' : subtracts the mean intensity from image
                                    == 'img' : subtracts a pre-prepared background image.
                                            (See preprocessing > meanbkg_img.py)
    parameters['subtract bkg norm'] == True   : Stretches range of final image intensities 0-255


    Parameters
    ----------

    frame: np.ndarray
        frame either colour or grayscale
    parameters: dict, optional
        parameters dictionary
    call_num: int or None
        number specifying the call number to this function. allows multiple calls


    Returns
    -------

    image with background image subtracted

    '''
    
    method_key = get_method_key('subtract_bkg', call_num=call_num)
    params = parameters['preprocess'][method_key]
    
    try:
        if params['subtract_bkg_type'] == 'mean':
            mean_val = int(np.mean(frame))
            subtract_frame = mean_val * np.ones(np.shape(frame), dtype=np.uint8)
            frame2=frame
        elif params['subtract_bkg_type'] == 'img':
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

            #blur frames
            frame2, error = blur(frame, temp_params)
            frame2 = frame2.astype(np.uint8)
            subtract_frame, error = blur(subtract_frame, temp_params)
            subtract_frame =subtract_frame.astype(np.uint8)


    
        if get_param_val(params['subtract_bkg_invert']):
            frame2 = cv2.subtract(subtract_frame, frame2)
        else:
            frame2 = cv2.subtract(frame2, subtract_frame)

        if np.max(frame) == 0:
            frame2 = frame

        if params['subtract_bkg_norm']==True:
            frame2 = cv2.normalize(frame2, None, alpha=0, beta=255,
                                  norm_type=cv2.NORM_MINMAX)
    
        return frame2, False
    except Exception as e:
        print(e)
        print('Error in preprocessing_methods.subtract_bkg - if subtracting bkg img image must either have default name "moviename"_bkgimg.png or you must enter the entire path including file ending. The image must be the the same size and color depth as the images it is to be subtracted from')
        return frame, True

def threshold(frame, parameters=None, call_num=None):
    '''Apply a global image threshold

    Notes
    -----

    This takes a cutoff threshold value and returns white above and
    black below this value.

    options
    ~~~~~~
    parameters['threshold'] : sets the value of the cutoff threshold
    parameters['th_mode] : Can be used to invert the above behaviour

    Parameters
    ----------

    frame: np.ndarray
        frame grayscale
    parameters: dict, optional
        parameters dictionary
    call_num: int or None
        number specifying the call number to this function. allows multiple calls

    Returns
    -------

    binary image with 255 for pixel val > threshold else 0.

    '''
    method_key = get_method_key('threshold', call_num=call_num)
    params = parameters['preprocess'][method_key]
    threshold = get_param_val(params['threshold'])
    mode = get_param_val(params['th_mode'])
    
    try:
        ret, out = cv2.threshold(frame,threshold,255,mode)
        return out, False
    except Exception as e:
        print(e)
        print('Error in preprocessing_methods.threshold')
        return frame, True

def variance(frame, parameters=None, call_num=None):
    ''' Variance of an image

    Notes
    -----

    This function finds the mean value of image and then returns
    frame which is the absolute difference of each pixel from that value

    options
    ~~~~~~~

    
    parameters['variance norm'] == True: will stretch the range of the largest difference to 255

    Parameters
    ----------

    frame: np.ndarray
        frame either colour or grayscale
    parameters: dict, optional
        parameters dictionary
    call_num: int or None
        number specifying the call number to this function. allows multiple calls

    Returns
    -------

    image of absolute difference from mean

    '''
    
    method_key = get_method_key('variance', call_num=call_num)
    params = parameters['preprocess'][method_key]
    mean_val = int(get_param_val(params['value']))
    subtract_frame = mean_val*np.ones(np.shape(frame), dtype=np.uint8)       

    try:  
        #subtract_frame = subtract_frame.astype(np.uint8)

        frame1 = cv2.subtract(subtract_frame, frame)
        frame1 = cv2.normalize(frame1, frame1 ,0,255,cv2.NORM_MINMAX)
        frame2 = cv2.subtract(frame, subtract_frame)
        frame2 = cv2.normalize(frame2, frame2,0,255,cv2.NORM_MINMAX)
        frame = cv2.add(frame1, frame2)

        if params['variance_norm'] == True:
            frame = cv2.normalize(frame, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

        return frame, False
    except Exception as e:
        print(e)
        print('Error in preprocessing_methods.variance.')
        return frame, True

def resize(frame, parameters=None, call_num=None):
    ''' Resize an image

    Notes
    -----

    resizes an input image by the scale specified

    options
    ~~~~~~~

    parameters['resize scale'] : factor for scale operation

    Parameters
    ----------

    frame: np.ndarray
        frame
    parameters: dict, optional
        parameters dictionary
    call_num: int or None
        number specifying the call number to this function. allows multiple calls

    Returns
    -------

    Resized frame

    '''
    method_key = get_method_key('resize', call_num=call_num)
    params = parameters['preprocess'][method_key]

    scale = get_param_val(params['scale'])/100
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dim = (width, height)
    try:
        return cv2.resize(frame, dim), False
    except Exception as e:
        print(e)
        print('Error in preprocessing_methods.resize')
        return frame, True



