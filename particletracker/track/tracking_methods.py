import cv2
import numpy as np
import trackpy as tp
import pandas as pd

from ..general.parameters import get_param_val, get_method_key
from ..track import intensity_methods as im
from ..customexceptions.track_error import *
from ..user_methods import *


'''
--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------
Tracking Methods
--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------

'''

def trackpy(ppframe,frame, parameters=None):
    """
    Trackpy implementation

    Notes
    -----
    This method uses the trackpy python library which can be found here: 
    http://soft-matter.github.io/trackpy/v0.4.2/
    If you use this method in a research publication be sure to cite according to 
    the details given here:
    http://soft-matter.github.io/trackpy/v0.4.2/introduction.html

    using get_intensities will seriously slow down the processing so optimise
    everything else first.


    size_estimate
        An estimate of the objects to be tracked feature size in pixels
    invert
        Set True if looking for dark objects on bright background
    get_intensities
        If not False results in the software extracting a circular region around each particle of radius set by intensity radius and running a method in intensity_methods. Select the method by writing its name in the get_intensities box.


    Args
    ----
    ppframe
        The preprocessed frame upon which tracking is to be performed.
    frame
        The unprocessed frame on which get_intensities is run.
    parameters
        Nested dictionary specifying the tracking parameters
    
    
    Returns
    -------
        Dataframe containing data from a single frame


    """



    try:
        method_key = get_method_key('trackpy')
        df = tp.locate(ppframe, get_param_val(parameters[method_key]['size_estimate']), invert=get_param_val(parameters[method_key]['invert']))

        if get_param_val(parameters[method_key]['get_intensities']) != 'False':
            x = df['x'].to_numpy()
            y = df['y'].to_numpy()
            intensity = []
            for i in range(np.size(x)):
                xc = x[i]
                yc = y[i]
                rc = get_param_val(parameters[method_key]['intensity_radius'])

                try:
                    # Try because some circles overlap the edge giving meaningless answers
                    cut_out_frame = frame[int(yc - rc):int(yc + rc), int(xc - rc):int(xc + rc)]
                    h, w = cut_out_frame.shape[:2]
                    mask = _create_circular_mask(h, w)
                    masked_img = cut_out_frame.copy()
                    masked_img[~mask] = 0
                    value = getattr(im, get_param_val(parameters[method_key]['get_intensities']))(masked_img)
                except:
                    value = np.Nan

                intensity.append(value)
            df['intensities'] = np.array(intensity)
        if get_param_val(parameters[method_key]['show_output']):
            print(df.head(n=50))
        return df
    except Exception as e:
        raise TrackpyError(e)
        


def hough(ppframe, frame,parameters=None):
    '''
    Performs the opencv hough circles transform to locate circles in an image.

    Notes
    -----
    This method uses the opencv hough circles algorithm to look for circles in an image.
    It works well provided you constrain the radii searched to reasonably tight range. It
    is particularly good for tightly bunched large particles. To estimate the appropriate
    range of radii double left click on the image will give you a coordinate or you can use
    the circular crop tool to start off with about the right values. Set min dist that the 
    centre of two circles can approach (a bit less than diameter). You then need to use P1 
    and P2 which are different gradient terms associated with the image. P1 is usually bigger
    than P2. Annotation with circles will automatically pick up the radii from the tracking so
    can be used to help get the settings right.


    min_dist
        minimum distance in pixels between two particles
    min_rad
        minimum radius of particles in pixels
    max_rad
        maximum radius of particles in pixels
    p1
        Control parameter 
    p2
        Control parameter
    get_intensities
        If not False results in the software extracting a circular region around each particle of radius set by tracking and running a method in intensity_methods. Select the method by writing its name in the get_intensities box.


    Args
    ----
    ppframe
        The preprocessed frame upon which tracking is to be performed.
    frame
        The unprocessed frame on which get_intensities is run.
    parameters
        Nested dictionary specifying the tracking parameters
    
    
    Returns
    -------
        Dataframe containing data from a single frame
    '''
    try:
        method_key = get_method_key('hough')
        circles = np.squeeze(cv2.HoughCircles(
                    ppframe,
                    cv2.HOUGH_GRADIENT,
                    1,
                    get_param_val(parameters[method_key]['min_dist']),
                    param1=get_param_val(parameters[method_key]['p1']),
                    param2=get_param_val(parameters[method_key]['p2']),
                    minRadius=get_param_val(parameters[method_key]['min_rad']),
                    maxRadius=get_param_val(parameters[method_key]['max_rad'])))
        try:
            circles_dict = {'x': circles[:, 0], 'y': circles[:, 1], 'r': circles[:, 2]}
        except:
            circles_dict={'x':[np.nan],'y':[np.nan],'r':[np.nan]}
        
        if parameters[method_key]['get_intensities'] != 'False':
            
            intensity = []
            for i,_ in enumerate(circles_dict['x']):
                xc = circles_dict['x'][i]
                yc = circles_dict['y'][i]
                rc = circles_dict['r'][i]

                try:
                    #Try because some circles overlap the edge giving meaningless answers
                    cut_out_frame = frame[int(yc - rc):int(yc + rc), int(xc - rc):int(xc + rc)]
                    h,w= cut_out_frame.shape[:2]
                    mask = _create_circular_mask(h, w)
                    masked_img = cut_out_frame.copy()
                    masked_img[~mask] = 0
                    value = getattr(im, get_param_val(parameters[method_key]['get_intensities']))(masked_img)
                except:
                    value = np.Nan

                intensity.append(value)

            circles_dict['intensities']=np.array(intensity)

        
        df = pd.DataFrame(circles_dict)
        
        if get_param_val(parameters[method_key]['show_output']):
            print(df.head(n=50))

        return df
    except Exception as e:
        raise HoughCirclesError(e)


def contours(pp_frame, frame, parameters=None):
    '''
    Implementation of OpenCVs contours.


    Notes
    -----
    To use contours you must have preprocessed the image to produce a black and white
    binary image with separated object. Contours stores: the centroid x, y, area enclosed by contour,
    the bounding rectangle (not rotated) which is used with contour to generate
    mask so that you can extract pixels from original image
    and perform some analysis.


    area_min
        Minimum contour area to store object
    area_max
        Maximum contour area to store object
    aspect_min
        Minimum contour aspect ratio to store object
    aspect_max
        Maximum contour aspect ratio to store object
    get_intensities
        If not False results in the software extracting a region around each particle. Pixels outside the contour are masked. The remaining particle image is processed using get_intensities method. Select the method by writing its name in the get_intensities box.


    Args
    ----
    ppframe
        The preprocessed frame upon which tracking is to be performed.
    frame
        The unprocessed frame on which get_intensities is run.
    parameters
        Nested dictionary specifying the tracking parameters
    
    
    Returns
    -------
        Dataframe containing data from a single frame

    '''
    try:  
        method_key = get_method_key('contours')
        params = parameters[method_key]
        get_intensities = (get_param_val(params['get_intensities']) != 'False')
    
        sz = np.shape(frame)
        if np.shape(sz)[0] == 3:
            frame= cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)       

        area_min = get_param_val(params['area_min'])
        area_max = get_param_val(params['area_max'])
        aspect_min = get_param_val(params['aspect_min'])
        aspect_max = get_param_val(params['aspect_max'])
        info = []
        
        contour_pts = _find_contours(pp_frame)
        for index, contour in enumerate(contour_pts):
            M = cv2.moments(contour)
            if M['m00'] > 0:
                area = cv2.contourArea(contour)
                
                if (area < area_max) & (area > area_min):
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])

                    rect = cv2.minAreaRect(contour)
                    (x, y), (w, h), angle = rect
                    aspect = max(w,h)/min(w,h)

                    if (aspect <= aspect_max) & (aspect >= aspect_min):  
                        if get_intensities:
                            intensity = _find_intensity_inside_contour(contour, frame, get_intensities)
                            info_contour = [cx, cy, area, contour, intensity]
                        else:
                            info_contour = [cx, cy, area, contour]
                        info.append(info_contour)

        if get_intensities:
            info_headings = ['x', 'y', 'area', 'contours', 'intensities']
        else:
            info_headings = ['x', 'y', 'area', 'contours']
        df = pd.DataFrame(data=info, columns=info_headings)

        if get_param_val(parameters[method_key]['show_output']):
            print(df.head(n=50))
        return df
    except Exception as e:
        raise ContoursError(e)

'''
------------------------------------------------------------------------
Supporting functions
------------------------------------------------------------------------
'''
def _create_circular_mask(h, w, center=None, radius=None):
    if center is None: # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = dist_from_center <= radius
    return mask
    


def _find_contours(img, hierarchy=False):
    """
    contours is a tuple containing (img, contours)
    """
    # work for any version of opencv

    try:
        im, contours, hier = cv2.findContours(
            img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    except:
        contours, hier = cv2.findContours(
            img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if hierarchy:
        return contours, hier
    else:
        return contours
    

def _draw_contours(img, contours, col=(0,0,255), thickness=1):
    """

    :param img:
    :param contours:
    :param col: Can be a defined colour in colors.py or a list of tuples(3,1) of colors of length contours
    :param thickness: -1 fills the contour.
    :return:
    """
    try:
        if thickness == -1:
            thickness = cv2.FILLED

        if (np.size(np.shape(col)) == 0) | (np.size(np.shape(col)) == 1):
            img = cv2.drawContours(img, [contours], -1, col, thickness)
        else:
            for i, contour in enumerate(contours):
                img = cv2.drawContours(img, contour, -1, col[i], thickness)
        return img
    except Exception as e:
        print('Error in tracking_methods._draw_contours')
        print(e)


def _find_intensity_inside_contour(contour, frame, intensity_method):
    try:
        #find bounding rectangle
        x,y,w,h = cv2.boundingRect(contour)
        cut_out_frame = frame[y:y+h,x:x+w]
        shifted_contour = contour - [x,y]
        mask = np.zeros((h,w,3))
        mask = _draw_contours(mask, shifted_contour,col=(255,255,255),thickness=-1)
        cut_out_frame[~(mask[:,:,0] > 0)] = 0
        value = getattr(im, intensity_method)(cut_out_frame)
        return value
    except Exception as e:
        print('Error in tracking_methods._find_intensity_inside_contour')
        print(e)





