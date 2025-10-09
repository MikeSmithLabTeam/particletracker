from math import nan
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
from ..general.parameters import param_parse
from ..general.dataframes import df_single, df_range
from ..customexceptions import *
from ..user_methods import *

"""
Postprocessing methods can have a number of decorators.
   
1) @error_handling:
Handles errors produced by each function
2)@param_parse:
The decorator @param_parse reduces params dictionary to the appropriate bit. If you need access to 
other section of params outside those relevant to function do not use and implement yourself.
3)df_single or df_range:
Some postprocessing methods need range of dataframe and some just need one frame.  In postprocessing you don't need logic specifying whether to read the full or partial dataframe as this is handled by the decorator on the postprocessing_methods. The decorator  or @df_multiple chop down the dataframes passed to the methods."""


'''
-----------------------------------------------------------------------------------------------------
All these methods operate on single frames
-------------------------------------------------------------------------------------------------------
'''

@error_handling
@param_parse
def absolute(df, *args,  parameters=None, **kwargs):
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
    
    df[column_name + '_abs'] = np.abs(df[column_name]) 
    return df

'''
------------------------------------------------------------------------------------------------
This function allows you to load data into a column opposite each frame number
-------------------------------------------------------------------------------------------------
'''
@error_handling
@param_parse
def add_frame_data(df,  parameters=None, *args, **kwargs):
    '''
    Add frame data allows you to manually add a new column of df to the dfframe. 
    
    Notes
    -----
    This is done by creating a .csv file and reading it in within the gui. 
    The file should have one column with the data for 
    each frame listed on the correct line. 

    Parameters
    ----------
    new_column_name
        Name for column to which data is to be imported.    
    data_filename
        filename with extension for the df to be loaded. 
    data_path
        folder where the file is located
    
    
    Args
    ----

    df_full
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
    f_index = kwargs['f_index']
    df[parameters['new_column_name']] = np.nan
    
    if f_index is None:
        #process all frames
        indices = list(set(df.index.values.tolist()))
    else:
        #Just process frame of interest
        indices=[f_index]
    
    datapath = parameters['data_path']
    filename = os.path.join(datapath,parameters['data_filename'])
    if '.csv' not in filename:
        filename = filename + '.csv'
    new_df = pd.read_csv(filename, header=None).squeeze("columns")

    for f_index in indices:
        df.loc[f_index, parameters['new_column_name']] = new_df[new_df.index == f_index]
    return df

@error_handling
@param_parse
def angle(df,  *args,  parameters=None, **kwargs):
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
    
    if parameters['units'] == 'degrees':
        df[parameters['output_name']] = np.arctan2(df[parameters['y_column']],df[parameters['x_column']])*(180/np.pi)
    else:
        df[parameters['output_name']] = np.arctan2(df[parameters['y_column']],df[parameters['x_column']])
    return df

@error_handling
@param_parse
def classify(df, *args,  parameters=None, **kwargs):
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
    
    df[output_name] = df[column].apply(_classify_fn, lower_threshold_value=parameters['lower_threshold'], upper_threshold_value=parameters['upper_threshold'])
    return df


def _classify_fn(x, lower_threshold_value=None, upper_threshold_value=None):
    if (x > lower_threshold_value) and (x < upper_threshold_value):
        return True
    else:
        return False

@error_handling
@param_parse
def contour_boxes(df, *args,  **kwargs):
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
    
    contours = df[['contours']].values

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
            return df_empty

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

    df['box_cx'] = box_cx
    df['box_cy'] = box_cy
    df['box_angle'] = box_angle
    df['box_width'] = box_width
    df['box_length'] = box_length
    df['box_area'] = box_area
    df['box_pts'] = box_pts
    print('boxes', df)
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
def hexatic_order(df, *args,  parameters=None, **kwargs):
    """
    Calculates the hexatic order parameter of each particle.
    """
    df['hexatic_order_complex']=pd.Series(np.nan, index=df.index, dtype=object)
    df['hexatic_order_magnitude']=pd.Series(np.nan, index=df.index, dtype=object)
    df['hexatic_order_phase']=pd.Series(np.nan, index=df.index, dtype=object)
    df['number_of_neighbours']=pd.Series(np.nan, index=df.index, dtype=object)
    
    method = parameters.get('method', 'delaunay')  # Default to Delaunay
    cutoff = parameters['cutoff']
    
    f_index = kwargs['f_index']

    if f_index is None:
        #process all frames
        indices = list(set(df.index.values.tolist()))
    else:
        #Just process frame of interest
        indices=[f_index]

    for f_index in indices:
        points = df[['x', 'y']].loc[f_index].values
        frame_indices = df.loc[f_index].index

        # Use the appropriate method to find neighbors
        if method == 'delaunay':
            neighbors_data = _find_delaunay_for_hexatic(points, cutoff)
        elif method == 'kdtree':
            num_neighbors = int(parameters['neighbours'])
            neighbors_data = _find_kdtree_for_hexatic(points, cutoff, num_neighbors)
        else:
            raise ValueError(f"Unknown method '{method}' for hexatic order calculation.")
        
        sum_exp_6j, num_neighbors = neighbors_data

        # Calculate the complex hexatic order parameter
        psi_6 = np.zeros(len(points), dtype=complex)
        valid_indices = num_neighbors > 0
        psi_6[valid_indices] = sum_exp_6j[valid_indices] / num_neighbors[valid_indices]       
        
        # Create a Series for each result and align it to the correct particle indices
        df.loc[f_index, 'hexatic_order_complex'] = pd.Series(psi_6, index=frame_indices)
        df.loc[f_index, 'hexatic_order_magnitude'] = pd.Series(np.abs(psi_6), index=frame_indices)
        df.loc[f_index, 'hexatic_order_phase'] = pd.Series(np.angle(psi_6), index=frame_indices)
        df.loc[f_index, 'number_of_neighbours'] = pd.Series(num_neighbors, index=frame_indices)
    
    return df

def _find_delaunay_for_hexatic(points, cutoff):
    tri = sp.Delaunay(points)
    sum_exp_6j = np.zeros(len(points), dtype=complex)
    num_neighbors = np.zeros(len(points), dtype=int)

    for i in range(len(points)):
        p = points[i]
        neighbors_indices = tri.vertex_neighbor_vertices[1][tri.vertex_neighbor_vertices[0][i]:tri.vertex_neighbor_vertices[0][i+1]]
        
        for neighbor_idx in neighbors_indices:
            neighbor_p = points[neighbor_idx]
            distance = np.linalg.norm(p - neighbor_p)
            
            if distance < cutoff:
                angle = np.arctan2(neighbor_p[1] - p[1], neighbor_p[0] - p[0])
                sum_exp_6j[i] += np.exp(6j * angle)
                num_neighbors[i] += 1
    
    return sum_exp_6j, num_neighbors

def _find_kdtree_for_hexatic(points, cutoff, num_neighbors):
    tree = sp.KDTree(points)
    distances, indices = tree.query(points, k=num_neighbors + 1, distance_upper_bound=cutoff)
    
    sum_exp_6j = np.zeros(len(points), dtype=complex)
    num_neighbors = np.zeros(len(points), dtype=int)

    for i in range(len(points)):
        p = points[i]
        for j in range(1, len(indices[i])): # Skip the first element which is the particle itself
            neighbor_idx = indices[i][j]
            distance = distances[i][j]
            
            # KDTree query returns a fill value for points beyond the cutoff, so we check for that
            if distance < cutoff and neighbor_idx < len(points):
                neighbor_p = points[neighbor_idx]
                angle = np.arctan2(neighbor_p[1] - p[1], neighbor_p[0] - p[0])
                sum_exp_6j[i] += np.exp(6j * angle)
                num_neighbors[i] += 1
                
    return sum_exp_6j, num_neighbors

@error_handling
@param_parse
def logic_AND(df, *args,  parameters=None, **kwargs):
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
    
    df[output_name] = df[column1] * df[column2]
    return df

@error_handling
@param_parse
def logic_NOT(df, *args,  parameters=None, **kwargs):
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

    df[output_name] = ~df[column]
    return df

@error_handling
@param_parse
def logic_OR(df, *args,  parameters=None, **kwargs):
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

    df[output_name] = df[column1] + df[column2]
    return df

@error_handling
@param_parse
def magnitude(df, *args,  parameters=None, **kwargs):
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

    df[output_name] = (df[column]**2 + df[column2]**2)**0.5  
    return df

@error_handling
@param_parse
def neighbours(df, *args,  parameters=None, **kwargs):
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
    df['neighbours'] = pd.Series(np.nan, index=df.index, dtype=object)
    df['neighbour_dists'] = pd.Series(np.nan, index=df.index, dtype=object)

    method = parameters['method']

    f_index = kwargs['f_index']
    if f_index is None:
        #process all frames
        indices = list(set(df.index.values.tolist()))
    else:
        #Just process frame of interest
        indices=[f_index]
    
    for f_index in indices:
        if method == 'delaunay':
            df.loc[f_index,['neighbours', 'neighbour_dists']] =_find_delaunay(df.loc[f_index], parameters=parameters)
        elif method == 'kdtree':
            df.loc[f_index,['neighbours', 'neighbour_dists']] =_find_kdtree(df.loc[f_index], parameters=parameters)     
    return df

def _find_kdtree(df, parameters=None):
    cutoff = parameters['cutoff']
    num_neighbours = int(parameters['neighbours'])
    points = df[['x', 'y']].values
    particle_ids = df[['particle']].values.flatten()
    tree = sp.KDTree(points)
    
    # Query for the `num_neighbours` nearest particles, with the specified cutoff
    # The first neighbor is always the particle itself, so we query k+1.
    distances, indices = tree.query(points, k=num_neighbours + 1, distance_upper_bound=cutoff)
    
    neighbour_ids = []
    neighbour_dists = []

    for i in range(len(points)):
        # Filter out invalid neighbors (fill value) and the particle itself (index 0)
        valid_mask = indices[i, 1:] < len(points)
        
        # Get neighbor IDs using advanced indexing
        current_neighbor_ids = particle_ids[indices[i, 1:][valid_mask]].tolist()
        neighbour_ids.append(current_neighbor_ids)
        
        # Get corresponding distances
        current_neighbor_dists = distances[i, 1:][valid_mask].tolist()
        neighbour_dists.append(current_neighbor_dists)

    df['neighbours'] = neighbour_ids
    df['neighbour_dists'] = neighbour_dists
    return df

@error_handling
def _find_delaunay(df, parameters=None):
    cutoff = parameters['cutoff']
    points = df[['x', 'y']].values
    particle_ids = df[['particle']].values.flatten()
    tess = sp.Delaunay(points)
    list_indices, point_indices = tess.vertex_neighbor_vertices

    neighbour_ids_list = []
    neighbour_dists_list = []
    
    for i in range(len(points)):
        p1 = points[i]
        
        # Get the neighbor indices for particle i from the Delaunay output
        delaunay_neighbors = point_indices[list_indices[i]:list_indices[i+1]]
        
        current_neighbor_ids = []
        current_neighbor_dists = []
        
        # Iterate over the Delaunay neighbors and apply the cutoff
        for neighbor_idx in delaunay_neighbors:
            p2 = points[neighbor_idx]
            dist = np.linalg.norm(p1 - p2)
            
            if dist < cutoff:
                current_neighbor_ids.append(int(particle_ids[neighbor_idx]))
                current_neighbor_dists.append(float(dist))

        neighbour_ids_list.append(current_neighbor_ids)
        neighbour_dists_list.append(current_neighbor_dists)
    
    df['neighbours'] = neighbour_ids_list
    df['neighbour_dists'] = neighbour_dists_list
    
    return df



@error_handling
@param_parse
def voronoi(df, *args,  **kwargs):
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
    df['voronoi']=pd.Series(np.nan, index=df.index, dtype=object)
    df['voronoi_area']=pd.Series(np.nan, index=df.index, dtype=object)
    f_index = kwargs['f_index']

    if f_index is None:
        #process all frames
        indices = list(set(df.index.values.tolist()))
    else:
        #Just process frame of interest
        indices=[f_index]

    for f_index in indices:
        points = df[['x', 'y']].loc[f_index].values
        frame_indices = df.loc[f_index].index

        vor = sp.Voronoi(points)
        df.loc[f_index, 'voronoi'] = pd.Series(_get_voronoi_coords(vor), index=frame_indices)
        df.loc[f_index, 'voronoi_area']=_voronoi_props(vor)
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



@error_handling
@param_parse
def real_imag(df, *args, parameters=None, **kwargs):
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

    df[column_name + '_re'] = np.real(df[column_name])
    df[column_name + '_im'] = np.imag(df[column_name])
    df[column_name + '_mag'] = np.absolute(df[column_name])
    df[column_name + '_ang'] = np.angle(df[column_name])
    return df

@error_handling
def audio_frequency(df, *args,  parameters=None, **kwargs):
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

    filename = parameters['config']['_video_filename']
    
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

    df['audio_frequency'] = peak
    return df

@error_handling
@param_parse
def duty_to_acceleration(df,  parameters=None, *args, **kwargs):
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
    try:
        filepath = parameters['calibration_filepath']
        calibration_data = pd.read_csv(str(filepath))
        path, name = filepath.rsplit('/', 1)
        fit_params = np.loadtxt(str(path)+"/calibration_fit_param.txt")
    except OSError as e:
        raise Exception

    func = lambda x,a,b,c,d,e, : a*x**4 + b*x**3 + c*x**2 + d*x + e

    peak_freq = df['audio_frequency']
    duty = (peak_freq.iloc[0] - 1000) / 15
    cal_arr = calibration_data.to_numpy()
    duty_data = cal_arr[:,0]
    duty_interp = np.linspace(np.min(duty_data), np.max(duty_data), 10000)
    acc_interp = func(duty_interp, *fit_params)
    duty_idx, = np.where(np.round(duty_interp,1)==np.round(duty,1))
    acceleration = np.round(acc_interp[duty_idx[0]], 2)
    
    df['duty_cycle'] = duty
    df['acceleration'] = acceleration
    return df

'''
---------------------------------------------------------------------------------------------
All these methods depend on information from other frames. ie they won't work unless
multiple frames have been processed and you are using part.
---------------------------------------------------------------------------------------------
'''

@error_with_hint("HINT: this func only works in the gui when locked. Span must be an odd value.")
@param_parse
def difference(df,  parameters=None, *args, **kwargs):
    '''
    Calculates the centered finite difference of a particle's values and
    returns the result for a specific frame index.
    '''
    column = parameters['column_name']
    output_name = parameters['output_name']
    span = parameters['span']

    if output_name not in df.columns:
        df[output_name]=np.nan

    # Create a MultiIndex for proper grouping and sorting
    df_temp = df.set_index('particle', append=True).sort_index().reorder_levels(['particle', 'frame'])

    # Ensure span is an odd number for a centered difference
    if span % 2 == 0:
        raise ValueError("Span for centered difference must be odd.")
    half_span = span // 2

    # Calculate the centered finite difference
    shifted_forward = df_temp.groupby(level='particle')[column].shift(-half_span)
    shifted_backward = df_temp.groupby(level='particle')[column].shift(half_span)

    # Store the calculated difference in a new column
    diff_values = shifted_forward - shifted_backward

    # Add the rate to a new column
    df_temp[output_name] = diff_values
    df = df_temp
    df.reset_index(level='particle', inplace=True)    
    
    return df
    

@error_with_hint("HINT: This method will not work in the gui unless you lock the link stage.")
@param_parse
def mean(df,  parameters=None, *args, **kwargs):
    '''
    Calculates the rolling mean of a particle's values and returns the result
    for a specific frame index.
    '''
    column = parameters['column_name']
    output_name = parameters['output_name']
    span = parameters['span']

    if output_name not in df.columns:
        df[output_name]=np.nan

    # Create a MultiIndex for proper grouping and sorting 
    df_temp = df.set_index('particle', append=True).sort_index().reorder_levels(['particle', 'frame'])

    # Calculate the rolling mean and store it in a temporary Series
    rolling_mean_series = df_temp.groupby(level='particle')[column].rolling(
        window=span, center=True).mean().reset_index(level=0, drop=True)
    # Re-index the series to match the original DataFrame and add it
    df_temp[output_name] = rolling_mean_series
    df = df_temp
    df.reset_index(level='particle', inplace=True)
    return df

@error_with_hint("HINT: This method will not work in the gui unless you lock the link stage.")
@param_parse
def median(df,  parameters=None, *args, **kwargs):
    '''
    Calculates the rolling median of a particle's values and returns the result
    for a specific frame index.
    '''
    column = parameters['column_name']
    output_name = parameters['output_name']
    span = parameters['span']

    if output_name not in df.columns:
        df[output_name]=np.nan

    # Create a MultiIndex for proper grouping and sorting 
    df_temp = df.set_index('particle', append=True).sort_index().reorder_levels(['particle', 'frame'])

    # Calculate the rolling mean and store it in a temporary Series
    rolling_mean_series = df_temp.groupby(level='particle')[column].rolling(
        window=span, center=True).median().reset_index(level=0, drop=True)
    
    # Re-index the series to match the original DataFrame and add it
    df_temp[output_name] = rolling_mean_series
    df = df_temp

    df.reset_index(level='particle', inplace=True)
    return df
      
 


@error_with_hint("HINT: this func only works in the gui when locked. Span must be an odd value.")
@param_parse
def rate(df,  parameters=None, *args, **kwargs):
    '''
    Rate of change of a particle property with frame.
    '''
    column = parameters['column_name']
    output_name = parameters['output_name']
    span = parameters['span']
    fps = parameters['fps']

    if output_name not in df.columns:
        df[output_name]=np.nan

    # Create a MultiIndex for proper grouping and sorting
    df_temp = df.set_index('particle', append=True).sort_index().reorder_levels(['particle', 'frame'])

    # Ensure span is an odd number for a centered difference
    if span % 2 == 0:
        raise ValueError("Span for centered difference must be odd.")
    half_span = span // 2

    # Calculate the centered finite difference
    shifted_forward = df_temp.groupby(level='particle')[column].shift(-half_span)
    shifted_backward = df_temp.groupby(level='particle')[column].shift(half_span)

    # Store the calculated difference in a new column
    diff_values = shifted_forward - shifted_backward

    # Calculate the time difference (span / fps)
    time_diff = span / fps

    # Calculate the rate of change
    rate_of_change = diff_values / time_diff

    # Add the rate to a new column
    df_temp[output_name] = rate_of_change  
    df = df_temp
    df.reset_index(level='particle', inplace=True)

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




