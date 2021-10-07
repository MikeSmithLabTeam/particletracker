from PyQt5.QtCore import center
import numpy as np
import scipy.spatial as sp
import trackpy as tp
import cv2
import os
import subprocess
import pandas as pd

from labvision import audio, video

from ..general.parameters import get_method_key, get_param_val
from ..customexceptions.postprocessor_error import *
from ..user_methods import *
'''
-----------------------------------------------------------------------------------------------------
All these methods operate on single frames
-------------------------------------------------------------------------------------------------------
'''

def angle(df, f_index=None, parameters=None, call_num=None):
    '''
    Angle calculates the angle specified by two components.

    Notes
    -----
    Usually angle is used following calculating the difference along x and y trajectories.
    It assumes you want to calculate from x_column as dx and y_column as dy
    it uses tan2 so that -dx and +dy give a different result to +dx and -dy
    Angles are output in radians or degrees given by parameters['angle']['units']


    Parameters
    ----------

    x_column
        x component for calculating angle
    y_column
        y component for calculating angle
    output_name
        New column name to store angle df
    units
        'degrees' or 'radians'

    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column

    '''
    try:
        params = parameters['postprocess']
        method_key = get_method_key('angle', call_num)
        columnx = params[method_key]['x_column']
        columny = params[method_key]['y_column']
        output_name = params[method_key]['output_name']
        units=get_param_val(params[method_key]['units'])

        if output_name not in df.columns:
            df[output_name] = np.nan

        df_frame = df.loc[f_index]

        if units == 'degrees':
            df_frame[output_name] = np.arctan2(df_frame[columny],df_frame[columnx])*(180/np.pi)
        else:
            df_frame[output_name] = np.arctan2(df_frame[columny],df_frame[columnx])

        df.loc[f_index] = df_frame

        return df
    except Exception as e:
        raise AngleError(e)

def classify(df, f_index=None, parameters=None, call_num=None):
    '''
    Classifies particles based on values in a particular column


    Notes
    -----
    Takes a column of data and classifies whether its values are within 
    the specified range. If it is a True is put next to that particle in
    that frame in a new classifier column. This can be used to select 
    subsets of particles for later operations.

    
    Parameters
    ----------
    column_name
        input data column
    output_name
        column name for classification (True or False)
    lower_threshold
        min value to belong to classifier
    upper_threshold
        max value to belong to classifier
    
    
    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column


    '''

    try:
        params = parameters['postprocess']
        method_key = get_method_key('classify', call_num)
        column = params[method_key]['column_name']
        output_name=params[method_key]['output_name']
        lower_threshold_value = get_param_val(params[method_key]['lower_threshold'])
        upper_threshold_value = get_param_val(params[method_key]['upper_threshold'])

        if output_name not in df.columns:
            df[output_name] = np.nan
        df_frame = df.loc[f_index]

        df_frame[output_name] = df_frame[column].apply(_classify_fn, lower_threshold_value=lower_threshold_value, upper_threshold_value=upper_threshold_value)
        df.loc[f_index]=df_frame

        return df
    except Exception as e:
        raise ClassifyError(e)


def _classify_fn(x, lower_threshold_value=None, upper_threshold_value=None):
    if (x > lower_threshold_value) and (x < upper_threshold_value):
        return True
    else:
        return False


def contour_boxes(df, f_index=None, parameters=None, call_num=None):
    """
    Contour boxes calculates the rotated minimum area bounding box

    Notes
    -----
    This method is designed to work with contours. It calculates the minimum
    rotated bounding rectangle that contains the contour. This is useful for 
    calculating the orientation of shapes.

    New Columns
    -----------
    'box_cx'    -   Centre of mass x coord of calculated box
    'box_cy'    -   Centre of mass y coord of calculated box
    'box_angle' -   the angle of the long axis of the box relative to the x axis 
    'box_length'-   Long dimension of box
    'box_width' -   Short dimension of box
    'box_area'  -   Area of box

    All values in units of pixels.

    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column
    """

    try:
        params = parameters['postprocess']
        method_key = get_method_key('contour_boxes', call_num)

        if 'box_cx' not in df.columns:
            df['box_cx'] = np.nan
            df['box_cy'] = np.nan
            df['box_angle'] = np.nan
            df['box_length'] = np.nan
            df['box_width'] = np.nan
            df['box_area'] = np.nan
            df['box_pts'] = np.nan

        df_frame = df.loc[f_index]
        contours = df_frame[['contours']].values

        box_cx = []
        box_cy = []
        box_angle = []
        box_length = []
        box_width = []
        box_area = []

        if np.shape(contours)[0] == 1:
            df_empty = np.isnan(contours[0])
            if np.all(df_empty):
                #0 contours
                return df

        for index, contour in enumerate(contours):
            info_contour = _rotated_bounding_rectangle(contour)
            cx, cy = np.mean(info_contour[5], axis=0)
            box_cx.append(cx)
            box_cy.append(cy)
            box_angle.append(info_contour[2])
            box_width.append(info_contour[3])
            box_length.append(info_contour[4])
            box_area.append(info_contour[3]*info_contour[4])
            if index == 0:
                box_pts=[info_contour[5]]
            else:
                box_pts.append(info_contour[5])

        df_frame['box_cx'] = box_cx
        df_frame['box_cy'] = box_cy
        df_frame['box_angle'] = box_angle
        df_frame['box_width'] = box_width
        df_frame['box_length'] = box_length
        df_frame['box_area'] = box_area
        df_frame['box_pts'] = box_pts

        df.loc[f_index] = df_frame

        return df
    except Exception as e:
        ContourBoxesError(e)

def _rotated_bounding_rectangle(contour):
    #Helper method

    try:
        rect = cv2.minAreaRect(contour[0])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        dim = np.sort(rect[1])
        #[centrex, centrey, angle, length, width, box_corners]
        info = [rect[0][0], rect[0][1], rect[2], dim[0], dim[1], box]
        return info
    except Exception as e:
        print('Error in tracking_methods._rotated_bounding_rectangle')
        print(e)

def logic_AND(df, f_index=None, parameters=None, call_num=None):
    '''
    Applys a logical and operation to two columns of boolean values.


    column_name
        input data column
    column_name2
        input data column
    output_name
        column name for the result
          
    
    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column


    '''

    try:
        params = parameters['postprocess']
        method_key = get_method_key('logic_AND', call_num)
        column1 = params[method_key]['column_name']
        column2 = params[method_key]['column_name2']
        output_name = params[method_key]['output_name']
        if output_name not in df.columns:
            df[output_name] = np.nan
        df_frame = df.loc[f_index]

        df_frame[output_name] = df_frame[column1] * df_frame[column2]
        df.loc[f_index] = df_frame

        return df
    except Exception as e:
        raise LogicAndError(e)


def logic_NOT(df, f_index=None, parameters=None, call_num=None):
    '''
    Apply a logical not operation to a column of boolean values.

    Parameters
    ----------
    column_name
        input data column
    column_name2
        input data column
    output_name
        column name for the result
        
    
    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column


    '''


    try:
        params = parameters['postprocess']
        method_key = get_method_key('logic_NOT', call_num)
        column = params[method_key]['column_name']
        output_name = params[method_key]['output_name']
        if output_name not in df.columns:
            df[output_name] = np.nan
        df_frame = df.loc[f_index]

        df_frame[output_name] = ~df_frame[column]
        df.loc[f_index] = df_frame
        return df
    except Exception as e:
        raise LogicNotError(e)


def logic_OR(df, f_index=None, parameters=None, call_num=None):
    '''
    Apply a logical or operation to two columns of boolean values.

    Parameters
    ----------
    column_name
        input data column
    column_name2
        input data column
    output_name
        column name for the result
        
    
    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column


    '''


    try:
        params = parameters['postprocess']
        method_key = get_method_key('logic_OR', call_num)
        column1 = params[method_key]['column_name']
        column2 = params[method_key]['column_name2']
        output_name = params[method_key]['output_name']

        if output_name not in df.columns:
            df[output_name] = np.nan
        df_frame = df.loc[f_index]

        df_frame[output_name] = df_frame[column1] + df_frame[column2]
        df.loc[f_index] = df_frame
        return df
    except  Exception as e:
        raise LogicOrError(e)




def magnitude(df, f_index=None, parameters=None, call_num=None):
    '''
    Calculates the magnitude of 2 input columns (x^2 + y^2)^0.5 = r
    
    Parameters
    ----------
    column_name     :   First column
    column_name     :   Second column
    output_name     :   Column name for magnitude df
    
    
    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column


    '''
    try:
        params = parameters['postprocess']
        method_key=get_method_key('magnitude', call_num)
        column = params[method_key]['column_name']
        column2 = params[method_key]['column_name2']
        output_name = params[method_key]['output_name']

        if output_name not in df.columns:
            df[output_name] = np.nan
        df_frame = df.loc[f_index]

        df_frame[output_name] = (df_frame[column]**2 + df_frame[column2]**2)**0.5
        df.loc[f_index] = df_frame
        return df
    except Exception as e:
        raise MagnitudeError(e)


def neighbours(df, f_index=None, parameters=None, call_num=None):
    '''
    Find the nearest neighbours of a particle

    Notes
    -----
    Neighbours uses two different methods to find the nearest neighbours: a kdtree (https://en.wikipedia.org/wiki/K-d_tree) 
    or a delaunay method (https://en.wikipedia.org/wiki/Delaunay_triangulation) to locate the neighbours
    of particles in a particular frame. It returns the indices of the particles
    found to be neighbours in a list. You can also select a cutoff distance above which
    two particles are no longer considered to be neighbours. To visualise the result
    you can use "networks" in the annotation section.


    Parameters
    ----------
    method
        'delaunay' or 'kdtree'
    neighbours
        max number of neighbours to find. This is only relevant for the kdtree.
    cutoff
        distance in pixels beyond which particles are no longer considered neighbours

    New Columns
    -----------

    'neighbours'    -   A list of particle indices which are neighbours

    
    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column


    '''
    try:
        #https: // docs.scipy.org / doc / scipy / reference / generated / scipy.spatial.Delaunay.html
        params = parameters['postprocess']
        method_key = get_method_key('neighbours', call_num)
        method = get_param_val(params[method_key]['method'])

        if 'neighbours' not in df.columns:
            df['neighbours'] = np.nan
        df_frame = df.loc[f_index]

        if method == 'delaunay':
            df_frame =_find_delaunay(df_frame, parameters=params)
        elif method == 'kdtree':
             df_frame =_find_kdtree(df_frame, parameters=params)
        df.loc[f_index] = df_frame

        return df
    except Exception as e:
        raise NeighboursError(e)


def _find_kdtree(df, parameters=None):
    method_key = get_method_key('neighbours')
    cutoff = get_param_val(parameters[method_key]['cutoff'])
    num_neighbours = int(get_param_val(parameters[method_key]['neighbours']))
    points = df[['x', 'y']].values
    particle_ids = df[['particle']].values.flatten()
    tree = sp.KDTree(points)
    _, indices = tree.query(points, k=num_neighbours+1, distance_upper_bound=cutoff)
    neighbour_ids = []
    fill_val = np.size(particle_ids)
    for index, row in enumerate(indices):
        neighbour_ids.append([particle_ids[row[i+1]] for i in range(num_neighbours) if row[i+1] != fill_val])
    df.loc[:, ['neighbours']] = neighbour_ids
    return df

def _find_delaunay(df, parameters=None, call_num=None):
    method_key = get_method_key('neighbours')
    cutoff = get_param_val(parameters[method_key]['cutoff'])
    points = df[['x', 'y']].values
    particle_ids = df[['particle']].values.flatten()
    tess = sp.Delaunay(points)
    list_indices, point_indices = tess.vertex_neighbor_vertices

    neighbour_ids = [point_indices[a:b].tolist() for a, b in zip(list_indices[:-1], list_indices[1:])]
    dist = sp.distance.squareform(sp.distance.pdist(points))

    neighbour_dists = [(dist[i, row]<cutoff).tolist() for i, row in enumerate(neighbour_ids)]
    indices = []
    for index, row in enumerate(neighbour_ids):
        indices.append([particle_ids[neighbour_ids[index][j]] for j,dummy in enumerate(row) if neighbour_dists[index][j]])
    df.loc[:, ['neighbours']] = indices
    return df

def voronoi(df, f_index=None, parameters=None, call_num=None):
    """
    Calculate the voronoi network of particle.

    Notes
    -----
    The voronoi network is explained here: https://en.wikipedia.org/wiki/Voronoi_diagram
    This function also calculates the associated area of the voronoi cells.To visualise the result
    you can use "voronoi" in the annotation section.

    New Columns
    -----------
    'voronoi'       -   The voronoi coordinates that surround a particle
    'voronoi_area'  -   The area of the voronoi cell associated with a particle


    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column
    """

    try:
        params = parameters['postprocess']
        method_key = get_method_key('voronoi')

        if 'voronoi' not in df.columns:
            df['voronoi'] = np.nan
            df['voronoi_area'] = np.nan

        df_frame = df.loc[f_index]

        points = df_frame[['x', 'y']].values
        vor = sp.Voronoi(points)
        df_frame['voronoi']=_get_voronoi_coords(vor)
        df_frame['voronoi_area']=_voronoi_props(vor)
        df.loc[f_index] = df_frame

        return df
    except Exception as e:
        raise VoronoiError(e)

def _get_voronoi_coords(vor):
    voronoi_coords = []
    for index, point in enumerate(vor.points):
        region = vor.point_region[index]
        region_pt_indices = vor.regions[region]
        if -1 in region_pt_indices:
            voronoi_coords.append(np.nan)
        else:
            region_pt_coords = vor.vertices[region_pt_indices]
            voronoi_coords.append(region_pt_coords)
    return voronoi_coords

def _voronoi_props(vor):
    area = np.zeros(vor.npoints)
    perimeter = np.zeros(vor.npoints)
    for i, reg_num in enumerate(vor.point_region):
        indices = vor.regions[reg_num]
        if -1 in indices: # some regions can be opened
            area[i] = np.inf
            #perimeter[i] = np.inf
        else:
            area[i] = sp.ConvexHull(vor.vertices[indices]).volume
            #perimeter[i] = sp.ConvexHull(vor.vertices[indices]).area
    return area



def _get_class_subset(df, f, parameters, method=None):
    classifier_column= parameters[method]['classifier_column']
    if classifier_column is None:
        subset_df = df.df.loc[f]
    else:
        classifier = parameters[method]['classifier']
        temp = df.df.loc[f]
        subset_df = temp[temp[classifier_column] == classifier]
    return subset_df


def remove_masked(df, f_index=None, parameters=None, call_num=None):
    '''
    Remove masked objects
    
    Notes
    -----
    The Hough circles tracking method can find circles with centres 
    outside the masked area. This method enables you to remove those 
    points from the data.
    
    Parameters
    ----------
    column_name
        Input column names
    output_name
        Output column name
    fps
        numerical value indicating the number of frames per second
    span
        number of frames over which to calculate rolling difference
    
    
    
    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe


    '''
    try:
        params = parameters['postprocess']
        method_key = get_method_key('remove_masked', call_num)

        mask_method_list = list(parameters['crop']['crop_method'])
        if 'crop_box' in mask_method_list: mask_method_list.remove('crop_box')

        contour_list = []
        contour_list.append(_contour_from_mask(parameters['crop'][mask_method_list[0]],mask_method_list[0]))

        df_frame = df.loc[f_index]
        points = df_frame[['x','y']].apply(tuple, axis=1).values
        mask = np.array([_point_inside_mask(point, contour_list) for point in points])
        for column in df_frame.columns:
            df_frame[column] = df_frame[column].where(mask)
        df.loc[f_index] = df_frame
        df.dropna(how='all',inplace=True)
        return df
    except Exception as e:
        raise RemoveMaskedError(e)

def _contour_from_mask(mask_pts, mask_type):
    if mask_type == 'mask_rectangle':
        x1 = mask_pts[0][0]
        x2 = mask_pts[1][0]
        y1 = mask_pts[0][1]
        y2 = mask_pts[1][1]

        contour = [np.array([[x1,y1],[x1,y2],[x2,y2],[x2, y1]])]
    elif mask_type == 'mask_ellipse':
        pass
    elif mask_type == 'mask_circle':
        pass
    elif mask_type == 'mask_polygon':
        pass
    else:
        print('Error unrecognised mask type')
        raise Exception
    return contour

def _point_inside_mask(point, mask_contour_list):
    inside = False
    for contour in mask_contour_list:

        result = cv2.pointPolygonTest(contour[0], point, False)
        if result != -1:
            inside = True
    return inside


def hexatic_order(df, f_index=None, parameters=None, call_num=None):
    """
    Calculates the hexatic order parameter of each particle


    Parameters
    ----------
    threshold
        Distance threshold for calculation of neighbors


    Args
    ----------
    df
        The dataframe for all data
    f_index
        Integer for the frame in twhich calculations need to be made
    parameters
        Nested dict object
    call_num

    Returns
    -------
    df with additional column

    """



    try:
        params = parameters['postprocess']
        method_key = get_method_key('hexatic_order', call_num)
        threshold = get_param_val(params[method_key]['threshold'])

        if 'hexatic_order' not in df.columns:
            df['hexatic_order'] = np.nan
            df['number_of_neighbors'] = np.nan

        df_frame = df.loc[f_index]
        points = df_frame[['x', 'y']].values
        list_indices, point_indices = sp.Delaunay(points).vertex_neighbor_vertices
        repeat = list_indices[1:] - list_indices[:-1]
        vectors = points[point_indices] - np.repeat(points, repeat, axis=0)
        angles = np.angle(vectors[:, 0] + 1j*vectors[:, 1])
        length_filteres = np.linalg.norm(vectors, axis=1) < threshold
        summands = np.exp(6j*angles)
        summands *= length_filteres
        list_indices -= 1
        # sum the angles and count neighbours for each particle
        stacked = np.cumsum((summands, length_filteres), axis=1)[:, list_indices[1:]]
        stacked[:, 1:] = np.diff(stacked, axis=1)
        neighbors = stacked[1, :]
        indxs = neighbors != 0
        orders = np.zeros_like(neighbors)
        orders[indxs] = stacked[0, indxs] / neighbors[indxs]
        df_frame['hexatic_order'] = orders
        df_frame['number_of_neighbors'] = neighbors
        df.loc[f_index] = df_frame
        return df


    except Exception as e:
        raise HexaticOrderError(e)


def audio_frequency(df, f_index=None, parameters=None, call_num=None):
    from moviepy.editor import AudioFileClip
    try:
        filename = parameters['experiment']['video_filename']
        command = f"ffmpeg -i {filename} -ar 48000 -ss {0.02*f_index} -to {0.02*(f_index+1)} -vn out.wav"
        if os.path.exists("out.wav"):
            os.remove("out.wav")
        subprocess.call(command, shell=True, stderr=subprocess.DEVNULL)
        audio_arr = AudioFileClip("out.wav").to_soundarray(fps=48000, nbytes=2)[:, 0]
        ft = np.abs(np.fft.fft(audio_arr, n=len(audio_arr)))
        freq = np.fft.fftfreq(len(audio_arr), 1/48000)
        peak = int(abs(freq[np.argmax(ft)]))
        if 'audio_frequency' not in df.columns:
            df['audio_frequency'] = -1.0
        df_frame = df.loc[f_index]
        df_frame['audio_frequency'] = peak
        df.loc[f_index] = df_frame
        return df
    except Exception as e:
        raise AudioFrequencyError(e)

'''
---------------------------------------------------------------------------------------------
All these methods depend on information from other frames. ie they won't work unless
multiple frames have been processed and you are using part.
---------------------------------------------------------------------------------------------
'''
def difference(df, f_index=None, parameters=None, call_num=None):
    '''
    Difference of a particles values on user selected column. 

    Notes
    -----
    Returns the difference of a particle's values on a particular column at span separation in frames to a new column. Please be aware
    this is the difference between current frame and frame - span for each particle.
    
    Parameters
    ----------
    column_name
        Input column name
    output_name
        Column name for median data
    span
        number of frames over which to calculate rolling median
    
    
    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column

    '''
    try:
        params = parameters['postprocess']
        method_key = get_method_key('difference', call_num)
        column = params[method_key]['column_name']
        output_name = params[method_key]['output_name']
        span = get_param_val(params[method_key]['span'])

        if output_name not in df.columns:
            df[output_name] = np.nan

        start=f_index-span - 1
        if start < 0:
            start = 0

        finish=f_index + span + 1
        if finish > df.index.max():
            finish = df.index.max()

        df_frames = df.loc[start:finish,[column,'particle']]
        df_diff=df_frames.groupby('particle')[column].diff(periods=span).transform(lambda x:x).to_frame(name=output_name)
        df.loc[f_index,[output_name]]=df_diff.loc[f_index]

        return df
    except Exception as e:
        raise DifferenceError(e)


def mean(df, f_index=None, parameters=None, call_num=None):
    '''
    Rolling mean of a particles values. 

    Notes
    -----
    Returns the rolling mean of a particle's values to a new column. Useful
    to reduce fluctuations or tracking inaccuracies. The value of the mean is
    placed at the centre of the rolling window. i.e [2,4,6,8,4] with window 3 would result
    in [NaN, 4, 6, 6, Nan].
    
    Parameters
    ----------
    column_name
        Input column name
    output_name
        Column name for mean data
    span
        number of frames over which to calculate rolling mean
    
    
    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column


    '''


    try:
        params = parameters['postprocess']
        method_key = get_method_key('mean', call_num)
        column = params[method_key]['column_name']
        output_name = params[method_key]['output_name']
        span = get_param_val(params[method_key]['span'])

        if output_name not in df.columns:
            df[output_name] = np.nan

        start=f_index-span - 1
        if start < 0:
            start = 0

        finish=f_index + span + 1
        if finish > df.index.max():
            finish = df.index.max()

        df_frames = df.loc[start:finish,[column,'particle']]
        df_output=df_frames.groupby('particle')[column].rolling(span, center=True).mean().transform(lambda x:x).to_frame(name=output_name)
        df_output.reset_index('particle', inplace=True)
        df.loc[f_index,[output_name]]=df_output.loc[f_index]
        return df
    except Exception as e:
        raise MeanError(e)


def median(df, f_index=None, parameters=None, call_num=None):
    '''
    Median of a particles values. 

    Notes
    -----
    Returns the median of a particle's values to a new column. Useful 
    before classification to answer to which group a particle's properties
    usually belong. The value of the median is
    placed at the centre of the rolling window. i.e [2,4,4,8,4] with window 3 would result
    in [NaN, 4, 4, 4, Nan].
    
    Parameters
    ----------
    column_name
        Input column name
    output_name
        Column name for median data
    span
        number of frames over which to calculate rolling median
    
    
    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column


    '''

    try:
        params = parameters['postprocess']
        method_key = get_method_key('median', call_num)
        column = params[method_key]['column_name']
        output_name = params[method_key]['output_name']
        span = get_param_val(params[method_key]['span'])

        if output_name not in df.columns:
            df[output_name] = np.nan

        start=f_index-span + 1
        if start < 0:
            start = 0

        finish=f_index + span + 1
        if finish > df.index.max():
            finish = df.index.max()


        df_frames = df.loc[start:finish,[column,'particle']]
        df_output=df_frames.groupby('particle')[column].rolling(span, center=True).median().transform(lambda x:x).to_frame(name=output_name)
        df_output.reset_index('particle', inplace=True)
        df.loc[f_index,[output_name]]=df_output.loc[f_index]

        return df
    except Exception as e:
        raise MedianError(e)


def rate(df, f_index=None, parameters=None, call_num=None):
    '''
    Rate of change of a particle property with frame
    
    Notes
    -----
    Rate function takes an input column and calculates the
    rate of change of the quantity. Nans are inserted at end and 
    beginning of particle trajectories where calc is not possible. The 
    rate is calculated from diff between current frame and frame - span.
    
    Parameters
    ----------
    column_name
        Input column names
    output_name
        Output column name
    fps
        numerical value indicating the number of frames per second
    span
        number of frames over which to calculate rolling difference
    
    
    
    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column


    '''
    try:
        params = parameters['postprocess']
        method_key = get_method_key('rate', call_num)
        column = params[method_key]['column_name']
        output_name = params[method_key]['output_name']
        span = get_param_val(params[method_key]['span'])
        fps= params[method_key]['fps']

        if output_name not in df.columns:
            df[output_name] = np.nan

        start=f_index-span - 1
        if start < 0:
            start = 0

        finish=f_index + span + 1
        if finish > df.index.max():
            finish = df.index.max()


        df_frames = df.loc[start:finish,[column,'particle']]
        df_output=df_frames.groupby('particle')[column].diff(periods=span).transform(lambda x:x).to_frame(name=output_name)
        df.loc[f_index,[output_name]]=df_output.loc[f_index] / (float(span)/float(fps))
        return df
    except Exception as e:
        raise RateError(e)





'''
------------------------------------------------------------------------------------------------
This function allows you to load data into a column opposite each frame number
-------------------------------------------------------------------------------------------------
'''
def add_frame_data(df, f_index=None, parameters=None, call_num=None):
    '''
    Add frame data allows you to manually add a new column of df to the dfframe. 
    
    Notes
    -----
    This is done by creating a .csv file and reading it in within the gui. 
    The file should have one column with the data for 
    each frame listed on the correct line. 

    Parameters
    ----------
    data_filename
        filename with extension for the df to be loaded. Assumes file is in same directory as video
    new_column_name
        Name for column to which data is to be imported.    

    
    Args
    ----

    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key

    Returns
    -------
        updated dataframe including new column


    '''
    try:
        params = parameters['postprocess']
        method_key = get_method_key('add_frame_data', call_num)
        datapath = params[method_key]['data_path']
        filename = os.path.join(datapath,params[method_key]['data_filename'])
        if '.csv' not in filename:
            filename = filename + '.csv'
        new_df = pd.read_csv(filename, header=None, squeeze=True)
        df[params[method_key]['new_column_name']] = new_df

        return df
    except  Exception as e:
        raise AddFrameDataError(e)







