import numpy as np
from pytest import param
import scipy.spatial as sp
import trackpy as tp
import cv2
import os
import subprocess
import pandas as pd
import scipy.optimize as opt

from labvision import audio, video
from moviepy.audio.io.AudioFileClip import AudioFileClip
from ..general.parameters import get_method_key, get_param_val, param_parse
from ..customexceptions import *
from ..user_methods import *
'''
-----------------------------------------------------------------------------------------------------
All these methods operate on single frames
-------------------------------------------------------------------------------------------------------
'''
@error_handling
@param_parse
def angle(df,  *args, f_index=None, parameters=None, **kwargs):
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
    if parameters['output_name'] not in df.columns:
        df[parameters['output_name']] = np.nan

    df_frame = df.loc[[f_index]]
    
    if parameters['units'] == 'degrees':
        df_frame[parameters['output_name']] = np.arctan2(df_frame[parameters['y_column']],df_frame[parameters['x_column']])*(180/np.pi)
    else:
        df_frame[parameters['output_name']] = np.arctan2(df_frame[parameters['y_column']],df_frame[parameters['x_column']])
    
    df.loc[[f_index]] = df_frame
    return df

@error_handling
@param_parse
def classify(df, *args, f_index=None, parameters=None, **kwargs):
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
    column = parameters['column_name']
    output_name=parameters['output_name']

    if output_name not in df.columns:
        df[output_name] = np.nan
    df_frame = df.loc[[f_index]]
    
    df_frame[output_name] = df_frame[column].apply(_classify_fn, lower_threshold_value=parameters['lower_threshold'], upper_threshold_value=parameters['upper_threshold'])
    df.loc[[f_index]]=df_frame
    
    return df


def _classify_fn(x, lower_threshold_value=None, upper_threshold_value=None):
    if (x > lower_threshold_value) and (x < upper_threshold_value):
        return True
    else:
        return False

@error_handling
@param_parse
def contour_boxes(df, *args, f_index=None, **kwargs):
    """
    Contour boxes calculates the rotated minimum area bounding box

    Notes
    -----
    This method is designed to work with contours. It calculates the minimum
    rotated bounding rectangle that contains the contour. This is useful for 
    calculating the orientation of shapes.


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

    if 'box_cx' not in df.columns:
        df['box_cx'] = np.nan
        df['box_cy'] = np.nan
        df['box_angle'] = np.nan
        df['box_length'] = np.nan
        df['box_width'] = np.nan
        df['box_area'] = np.nan
        df['box_pts'] = np.nan
    
    df_frame = df.loc[[f_index]]
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

    df.loc[[f_index]] = df_frame
    
    return df

@error_handling
def _rotated_bounding_rectangle(contour):
    #Helper method
    rect = cv2.minAreaRect(contour[0])
    box = cv2.boxPoints(rect)
    box = np.int32(box)
    dim = np.sort(rect[1])
    #[centrex, centrey, angle, length, width, box_corners]
    info = [rect[0][0], rect[0][1], rect[2], dim[0], dim[1], box]
    return info

@error_handling
@param_parse
def logic_AND(df, *args, f_index=None, parameters=None, **kwargs):
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
    
    column1 = parameters['column_name']
    column2 = parameters['column_name2']
    output_name = parameters['output_name']
    if output_name not in df.columns:
        df[output_name] = np.nan
    df_frame = df.loc[[f_index]]
    
    df_frame[output_name] = df_frame[column1] * df_frame[column2]
    df.loc[[f_index]] = df_frame
    
    return df

@error_handling
@param_parse
def logic_NOT(df, *args, f_index=None, parameters=None, **kwargs):
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
    column = parameters['column_name']
    output_name = parameters['output_name']
    
    if output_name not in df.columns:
        df[output_name] = np.nan
    df_frame = df.loc[[f_index]]

    df_frame[output_name] = ~df_frame[column]
    df.loc[[f_index]] = df_frame
    return df

@error_handling
@param_parse
def logic_OR(df, *args, f_index=None, parameters=None, **kwargs):
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
    column1 = parameters['column_name']
    column2 = parameters['column_name2']
    output_name = parameters['output_name']

    if output_name not in df.columns:
        df[output_name] = np.nan
    df_frame = df.loc[[f_index]]

    df_frame[output_name] = df_frame[column1] + df_frame[column2]
    df.loc[[f_index]] = df_frame
    return df

@error_handling
@param_parse
def magnitude(df, *args, f_index=None, parameters=None, **kwargs):
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
    column = parameters['column_name']
    column2 = parameters['column_name2']
    output_name = parameters['output_name']

    if output_name not in df.columns:
        df[output_name] = np.nan
    df_frame = df.loc[[f_index]]

    df_frame[output_name] = (df_frame[column]**2 + df_frame[column2]**2)**0.5
    df.loc[[f_index]] = df_frame
    
    return df

@error_handling
@param_parse
def neighbours(df, *args, f_index=None, parameters=None, **kwargs):
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
        https: // docs.scipy.org / doc / scipy / reference / generated / scipy.spatial.Delaunay.html
    neighbours
        max number of neighbours to find. This is only relevant for the kdtree.
    cutoff
        distance in pixels beyond which particles are no longer considered neighbours
 
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
    method = parameters['method']

    if 'neighbours' not in df.columns:
        df['neighbours'] = np.nan
    df_frame = df.loc[[f_index]]

    if method == 'delaunay':
        df_frame =_find_delaunay(df_frame, parameters=parameters)
    elif method == 'kdtree':
            df_frame =_find_kdtree(df_frame, parameters=parameters)     
    df.loc[[f_index]] = df_frame

    return df

def _find_kdtree(df, parameters=None):
    cutoff = parameters['cutoff']
    num_neighbours = int(parameters['neighbours'])
    points = df[['x', 'y']].values
    particle_ids = df[['particle']].values.flatten()
    tree = sp.KDTree(points)
    _, indices = tree.query(points, k=num_neighbours+1, distance_upper_bound=cutoff)
    neighbour_ids = []
    fill_val = np.size(particle_ids)
    for _, row in enumerate(indices):
        neighbour_ids.append([particle_ids[row[i+1]] for i in range(num_neighbours) if row[i+1] != fill_val])
    
    df.loc['neighbours'] = neighbour_ids
    return df

@error_handling
def _find_delaunay(df, parameters=None):
    cutoff = parameters['cutoff']
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
    
    df['neighbours']=indices
    return df

@error_handling
@param_parse
def voronoi(df, *args, f_index=None, **kwargs):
    """
    Calculate the voronoi network of particle.

    Notes
    -----

    The voronoi network is explained here: https://en.wikipedia.org/wiki/Voronoi_diagram
    This function also calculates the associated area of the voronoi cells.To visualise the result
    you can use "voronoi" in the annotation section.


    
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

    if 'voronoi' not in df.columns:
        df['voronoi'] = np.nan
        df['voronoi_area'] = np.nan

    df_frame = df.loc[[f_index]]

    points = df_frame[['x', 'y']].values
    vor = sp.Voronoi(points)
    df_frame['voronoi']=_get_voronoi_coords(vor)
    df_frame['voronoi_area']=_voronoi_props(vor)
    df.loc[[f_index]] = df_frame
    #print('voronoi ',df_frame['voronoi'].dtype)
    #print('voronoi ',df_frame['voronoi_area'].dtype)
    return df

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

@error_handling
@param_parse
def hexatic_order(df, *args, f_index=None, parameters=None, **kwargs):
    """
    Calculates the hexatic order parameter of each particle. Neighbours are 
    calculated using the Delaunay network with a cutoff distance defined by "cutoff"
    parameter.

    Parameters
    ----------
    cutoff
        Distance threshold for calculation of neighbors

    Args
    ----
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
    threshold = parameters['cutoff']

    if 'hexatic_order' not in df.columns:
        df['hexatic_order'] = np.nan
        df['number_of_neighbours'] = np.nan #Change name to indicate associated with hexatic methoc

    df_frame = df.loc[[f_index]]
    points = df_frame[['x', 'y']].values
    list_indices, point_indices = sp.Delaunay(points).vertex_neighbor_vertices
    repeat = list_indices[1:] - list_indices[:-1]
    vectors = points[point_indices] - np.repeat(points, repeat, axis=0)
    angles = np.angle(vectors[:, 0] + 1j*vectors[:, 1])
    length_filters = np.linalg.norm(vectors, axis=1) < threshold
    summands = np.exp(6j*angles)
    summands *= length_filters
    list_indices -= 1

    # sum the angles and count neighbours for each particle
    stacked = np.cumsum((summands, length_filters), axis=1)[:, list_indices[1:]]
    stacked[:, 1:] = np.diff(stacked, axis=1)
    neighbors = stacked[1, :]
    indxs = neighbors != 0
    orders = np.zeros_like(neighbors)
    orders[indxs] = stacked[0, indxs] / neighbors[indxs]
    
    df_frame['hexatic_order'] = orders
    df_frame['number_of_neighbours'] = np.real(neighbors)
    df.loc[[f_index]] = df_frame
   
    return df

@error_handling
@param_parse
def absolute(df, *args, f_index=None, parameters=None, **kwargs):
    """Returns new column with absolute value of input column

    Parameters
    ----------
    column_name : name of column containing input values

    Args
    ----
    df
        The dataframe for all data
    f_index
        Integer for the frame in twhich calculations need to be made
    parameters
        Nested dict object
    call_num

    Returns
    -------
    df with additional column containing absolute value of input_column.
    New column is named "column_name" + "_abs"

"""
    column_name = parameters['column_name']

    if column_name + '_abs' not in df.columns:
        df[column_name + '_abs'] = np.nan
          
    df_frame = df.loc[[f_index]]
    
    df_frame[column_name + '_abs'] = np.abs(df_frame[column_name])
    df.loc[[f_index]] = df_frame    
    #print('absolute ',df_frame[column_name + '_abs'].dtype)    
    return df

@error_handling
@param_parse
def real_imag(df, *args, f_index=None, parameters=None, **kwargs):
    """
    Extracts the real, imaginary, complex magnitude and complex angle from a complex number and puts them in
    new columns. Mainly useful for subsequent annotation with dynamic colour map.

    Parameters
    ----------
    column_name : name of column containing complex values

    Args
    ----
    df
        The dataframe for all data
    f_index
        Integer for the frame in twhich calculations need to be made
    parameters
        Nested dict object
    call_num

    Returns
    -------
    df with 3 additional columns containing real, imaginary and complex angle
    New columns are called "column_name" + "_Re" or "_Im" or "_Ang"

    """
    column_name = parameters['column_name']

    if column_name + '_re' not in df.columns:
        df[column_name + '_re'] = np.nan
        df[column_name + '_im'] = np.nan
        df[column_name + '_mag'] = np.nan
        df[column_name + '_ang'] = np.nan
    
    df_frame = df.loc[[f_index]]
    
    df_frame[column_name + '_re'] = np.real(df_frame[column_name])
    df_frame[column_name + '_im'] = np.imag(df_frame[column_name])
    df_frame[column_name + '_mag'] = np.absolute(df_frame[column_name])
    df_frame[column_name + '_ang'] = np.angle(df_frame[column_name])

    df.loc[[f_index]] = df_frame
    return df

@error_handling
def audio_frequency(df, *args, f_index=None, parameters=None, **kwargs):
    """
    Decodes the audio frequency in our videos. We use this to 
    encode information about the acceleration being applied to a video
    directly into the audio channel. This enables us to get the info back out

    Args
    ----
        df ([type]): [description]
        f_index ([type], optional): [description]. Defaults to None.
        parameters ([type], optional): [description]. Defaults to None.
        call_num ([type], optional): [description]. Defaults to None.

    Returns
    -------
        pd.DataFrame: tracking dataframe with data added
""" 
    #Audio encoding frequency
    bitrate=48000

    filename = parameters['experiment']['video_filename']
    
    #Get audio from video for one frame
    if os.path.exists("out.wav"):
        os.remove("out.wav")
        command = f"ffmpeg -i {filename} -ar 48000 -ss {0.02*f_index} -to {0.02*(f_index+1)} -vn out.wav"
    subprocess.call(command, shell=True, stderr=subprocess.DEVNULL)

    #convert to array
    audio_arr = audio.extract_wav("out.wav")[:,0]
    peak = audio.fourier_transform_peak(audio_arr,1/bitrate)
    
    if 'audio_frequency' not in df.columns:
        df['audio_frequency'] = -1.0

    df_frame = df.loc[[f_index]]
    df_frame['audio_frequency'] = peak
    df.loc[f_index] = df_frame
    return df

@error_handling
@param_parse
def duty_to_acceleration(df, f_index=None, parameters=None, *args, **kwargs):
    """
    Calculates dimensionless acceleration values of the system. Takes audio frequency 
    from function: 'audio_frequency' and calculates duty cycle. Acceleration determined
    from calibration data file supplied by user (must be .csv). Fitting of duty vs acceleration
    is performed externally.
    
    Function fits a 4th order polynomial to acceleration calibration data using calibration_fit()
    from particletracker.general.calibration_fitting.py. This function reads the fit parameters
    from the output of calibration_fit() and uses them to interpolate duty cycle values into 
    dimensionless accelerations.

    Calibration data and fit params saved to "Z:/shaker/config"
    
    Args
    ----
        df ([type]): [description]
        f_index ([type], optional): [description]. Defaults to None.
        parameters ([type], optional): [description]. Defaults to None.
        call_num ([type], optional): [description]. Defaults to None.

    Returns
    -------
        [type]: [description]
"""
    if 'acceleration' not in df.columns:
        df['duty_cycle'] = np.nan
        df['acceleration'] = np.nan
    
    df_frame = df.loc[[f_index]] 

    try:
        filepath = parameters['calibration_filepath']
        calibration_data = pd.read_csv(str(filepath))
        path, name = filepath.rsplit('/', 1)
        fit_params = np.loadtxt(str(path)+"/calibration_fit_param.txt")
    except OSError as e:
        raise Exception

    func = lambda x,a,b,c,d,e, : a*x**4 + b*x**3 + c*x**2 + d*x + e

    peak_freq = df_frame['audio_frequency']
    duty = (peak_freq.iloc[0] - 1000) / 15
    cal_arr = calibration_data.to_numpy()
    duty_data = cal_arr[:,0]
    duty_interp = np.linspace(np.min(duty_data), np.max(duty_data), 10000)
    acc_interp = func(duty_interp, *fit_params)
    duty_idx, = np.where(np.round(duty_interp,1)==np.round(duty,1))
    acceleration = np.round(acc_interp[duty_idx[0]], 2)
    
    df_frame['duty_cycle'] = duty
    df_frame['acceleration'] = acceleration
    df.loc[f_index] = df_frame
    return df

'''
---------------------------------------------------------------------------------------------
All these methods depend on information from other frames. ie they won't work unless
multiple frames have been processed and you are using part.
---------------------------------------------------------------------------------------------
'''

@error_handling
@param_parse
def difference(df, f_index=None, parameters=None, *args, **kwargs):
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
    column = parameters['column_name']
    output_name = parameters['output_name']
    span = parameters['span']

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
    #print('difference ',df[output_name].dtype)
    return df

@error_handling
@param_parse
def mean(df, f_index=None, parameters=None, *args, **kwargs):
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
    column = parameters['column_name']
    output_name = parameters['output_name']
    span = parameters['span']

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
    #print('mean ',df_output[output_name].dtype)
    return df

@error_handling
@param_parse
def median(df, f_index=None, parameters=None, *args, **kwargs):
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
    column = parameters['column_name']
    output_name = parameters['output_name']
    span = parameters['span']

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
    #print('median ',df_output[output_name].dtype)
    return df

@error_handling
@param_parse
def rate(df, f_index=None, parameters=None, *args, **kwargs):
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
    column = parameters['column_name']
    output_name = parameters['output_name']
    span = parameters['span']
    fps= parameters['fps']

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
    #print('rate ',df_output[output_name].dtype)
    return df


'''
------------------------------------------------------------------------------------------------
This function allows you to load data into a column opposite each frame number
-------------------------------------------------------------------------------------------------
'''
@error_handling
@param_parse
def add_frame_data(df, f_index=None, parameters=None, *args, **kwargs):
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
    datapath = parameters['data_path']
    filename = os.path.join(datapath,parameters['data_filename'])
    if '.csv' not in filename:
        filename = filename + '.csv'
    new_df = pd.read_csv(filename, header=None).squeeze("columns")
    df[parameters['new_column_name']] = new_df
    #print('add_frame_data ',df[parameters['new_column_name']].dtype)
    return df

def get_duty_cycle():
    """The shaker amplitude in our experiments is encoded into the audio of our video frames. We
    do this in units of the duty_cycle. This is extracted using a fft. The value of the duty_cycle is 
    written in a column for each frame number."""
    pass

def calibrate_acceleration():
    """Our experiments use a proxy known as the duty cycle to control the amplitude 
    of the shaking applied. A calibration curve is measured which converts each duty cycle
    to its corresponding value of gamma in g. This function assumes that the calibration file "shaker1_accelerometer......txt"
    is stored in a folder called "Calibrations" which is in the same folder as the video. The calibration file should have two columns
    duty_cycle, acceleration.
    """
    pass




