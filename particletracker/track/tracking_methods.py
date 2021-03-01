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

def trackpy(frame,_, parameters=None, call_num=None):
    try:
        method_key = get_method_key('trackpy', call_num)
        df = tp.locate(frame, get_param_val(parameters[method_key]['size_estimate']), invert=get_param_val(parameters[method_key]['invert']))

        if get_param_val(parameters[method_key]['get_intensities']):
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
        return df
    except Exception as e:
        raise TrackpyError(e)
        


def hough(frame, _,parameters=None, call_num=None):
    '''
    Performs the opencv hough circles transform to locate
    circles in an image.

    :param frame:
    :param parameters:
    :param call_num:
    :return:
    '''
    try:
        method_key = get_method_key('hough', call_num)

        circles = np.squeeze(cv2.HoughCircles(
            frame,
            cv2.HOUGH_GRADIENT, 1,
            get_param_val(parameters[method_key]['min_dist']),
            param1=get_param_val(parameters[method_key]['p1']),
            param2=get_param_val(parameters[method_key]['p2']),
            minRadius=get_param_val(parameters[method_key]['min_rad']),
            maxRadius=get_param_val(parameters[method_key]['max_rad'])))

        try:
            circles_dict = {'x': circles[:, 0], 'y': circles[:, 1], 'r': circles[:, 2]}
        except:
            circles_dict={'x':[1],'y':[1],'r':[5]}


        if parameters[method_key]['get_intensities']:
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

        return df
    except Exception as e:
        raise HoughCirclesError(e)



def boxes(frame, _,parameters=None, call_num=None):
    '''
    boxes method finds contour of object but reduces the info to
    a rotated bounding box. Use for finding an angle of object or
    estimate of size. If you need to do something with the pixels
    use contours instead.
    '''
    try:
        method_key = get_method_key('boxes',call_num=call_num)
        params = parameters[method_key]
        get_intensities = get_param_val(params['get_intensities'])

        area_min = get_param_val(params['area_min'])
        area_max = get_param_val(params['area_max'])
        info = []
        contour_pts = _find_contours(frame)

        for index, contour in enumerate(contour_pts):
            area = int(cv2.contourArea(contour))
            if (area < area_max) and (area >= area_min):
                info_contour = _rotated_bounding_rectangle(contour)
                cx, cy = np.mean(info_contour[5], axis=0)
                angle = info_contour[2]
                width = info_contour[3]
                length = info_contour[4]
                box = info_contour[5]

                if get_intensities:
                    intensity = _find_intensity_inside_contour(contour, frame, parameters['get_intensities'])
                    info_contour = [cx, cy, angle, width, length, contour, box, intensity]
                else:
                    info_contour = [cx, cy, angle, width, length, contour, box]
                info.append(info_contour)

        if get_intensities:
            info_headings = ['x', 'y', 'theta', 'width', 'length', 'contours','box', 'intensities']
        else:
            info_headings = ['x', 'y', 'theta', 'width', 'length', 'contours','box']
        df = pd.DataFrame(data=info, columns=info_headings)
        return df
    except Exception as e:
        raise BoxesError(e)


def contours(pp_frame, frame, parameters=None, call_num=None):
    '''
    contours stores: the centroid cx, cy, area enclosed by contour,
    the bounding rectangle (not rotated) which is used with contour to generate
    mask so that you can extract pixels from original image
    and perform some analysis.
    '''
    try:
        sz = np.shape(frame)
        if np.shape(sz)[0] == 3:
            frame= cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        method_key = get_method_key('contours',call_num=call_num)
        params = parameters[method_key]
        get_intensities = get_param_val(params['get_intensities'])

        area_min = get_param_val(params['area_min'])
        area_max = get_param_val(params['area_max'])
        info = []

        contour_pts = _find_contours(pp_frame)

        for index, contour in enumerate(contour_pts):
            M = cv2.moments(contour)
            if M['m00'] > 0:
                area = cv2.contourArea(contour)
                if (area < area_max) & (area > area_min):
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])

                    box = cv2.boundingRect(contour)
                    if get_intensities:
                        intensity = _find_intensity_inside_contour(contour, frame, get_intensities)
                        info_contour = [cx, cy, area, contour, box, intensity]
                    else:
                        info_contour = [cx, cy, area, contour, box]
                    info.append(info_contour)

        if get_intensities:
            info_headings = ['x', 'y', 'area', 'contours', 'boxes', 'intensities']
        else:
            info_headings = ['x', 'y', 'area', 'contours', 'boxes']
        df = pd.DataFrame(data=info, columns=info_headings)

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
    



def _rotated_bounding_rectangle(contour):
    try:
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        dim = np.sort(rect[1])

        #[centrex, centrey, angle, length, width, box_corners]
        info = [rect[0][0], rect[0][1], rect[2], dim[0], dim[1], box]
        return info
    except Exception as e:
        print('Error in tracking_methods._rotated_bounding_rectangle')
        print(e)


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





