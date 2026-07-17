from math import nan
import numpy as np
import scipy.spatial as sp
import trackpy as tp
import cv2
import os
import subprocess
import pandas as pd
import scipy.optimize as opt
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
import pyarrow as pa
import matplotlib.pyplot as plt
from tqdm import tqdm

from labvision import audio, video
from moviepy.audio.io.AudioFileClip import AudioFileClip
from ..general.parameters import param_parse
from ..general.contour_parsing import reconstruct_contour_pts
from ..customexceptions import *
import time

def time_it(func):
    def wrapper(*args, **kwargs):
        print(f"running {func.__name__}")
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"[{func.__name__}] took {end - start:.4f} seconds")
        return result
    return wrapper

arrow_bool = pd.ArrowDtype(pa.bool_())
arrowint8_type = pd.ArrowDtype(pa.list_(pa.int8()))
arrowint16_type = pd.ArrowDtype(pa.list_(pa.int16()))
arrowint32_type = pd.ArrowDtype(pa.list_(pa.int32()))
arrowf32_type = pd.ArrowDtype(pa.list_(pa.float32()))

"""
Postprocessing methods can have a number of decorators.
   
1) @error_handling:
Handles errors produced by each function
2)@param_parse:
The decorator @param_parse reduces params dictionary to the appropriate bit. If you need access to 
other section of params outside those relevant to function do not use and implement yourself.
"""


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
        if f_index in new_df.index:
            df.loc[f_index, parameters['new_column_name']] = new_df.loc[f_index]
        else:
            df.loc[f_index, parameters['new_column_name']] = np.nan
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
    
    contours = reconstruct_contour_pts(df[['contours']].values)

    box_cx = []
    box_cy = []
    box_angle = []
    box_length = []
    box_width = []
    box_area = []

    if not contours:
        return df

    box_pts = []

    for index, contour in enumerate(contours):
        info_contour = _rotated_bounding_rectangle(contour)
        cx, cy = np.mean(info_contour[5], axis=0)
        box_cx.append(cx)
        box_cy.append(cy)
        box_angle.append(info_contour[2])
        box_width.append(info_contour[3])
        box_length.append(info_contour[4])
        box_area.append(info_contour[3]*info_contour[4])
        #if index == 0:
        #    box_pts=[info_contour[5]]
        #else:
        #    box_pts.append(info_contour[5])
        box_pts.append(info_contour[5].flatten().tolist())

    df['box_cx'] = box_cx
    df['box_cy'] = box_cy
    df['box_angle'] = box_angle
    df['box_width'] = box_width
    df['box_length'] = box_length
    df['box_area'] = box_area
    df['box_pts'] = tuple(box_pts)
    
    return df

@error_handling
def _rotated_bounding_rectangle(contour):
    #Helper method
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = np.int32(box)
    dim = np.sort(rect[1])
    #[centrex, centrey, angle, length, width, box_corners]
    info = [rect[0][0], rect[0][1], rect[2], dim[0], dim[1], box]
    return info

@time_it
@error_handling
@param_parse
def hexatic_order(df, *args,  parameters=None, **kwargs):
    """
    Calculates the hexatic order parameter of each particle.
    """
    #df['hexatic_order_complex']=pd.Series(np.nan, index=df.index, dtype=object)
    df['hexatic_order_magnitude']=pd.Series(None, index=df.index)
    df['hexatic_order_phase']=pd.Series(None, index=df.index)
    df['number_of_neighbours']=pd.Series(None, index=df.index, dtype=np.uint8)
    
    method = parameters.get('method', 'delaunay')  # Default to Delaunay
    #method = parameters['method']
    cutoff = parameters['cutoff']
    
    f_index = kwargs['f_index']

    if f_index is None:
        #process all frames
        indices = list(set(df.index.values.tolist()))
    else:
        #Just process frame of interest
        indices=[f_index]

    for f_index in tqdm(indices, desc="Calculating Hexatic order"):
        points = df.loc[f_index, ['x', 'y']].to_numpy(dtype=np.float32)
        frame_indices = df.loc[f_index].index

        # Use the appropriate method to find neighbors
        if method == 'delaunay':
            neighbors_data = _find_delaunay_for_hexatic(points, cutoff)
        elif method == 'kdtree': #CAUTION: using KDTree could be problematic for hexatic because it looks past the first row of neighbours
            num_neighbors = 6 #int(parameters['neighbours'])
            neighbors_data = _find_kdtree_for_hexatic_parallel(points, cutoff)
        else:
            raise ValueError(f"Unknown method '{method}' for hexatic order calculation.")
        
        sum_exp_6j, num_neighbors = neighbors_data

        # Calculate the complex hexatic order parameter
        psi_6 = np.zeros(len(points), dtype=complex)
        valid_indices = num_neighbors > 0
        psi_6[valid_indices] = sum_exp_6j[valid_indices] / num_neighbors[valid_indices]       
        
        # Create a Series for each result and align it to the correct particle indices
        #df.loc[f_index, 'hexatic_order_complex'] = pd.Series(psi_6, index=frame_indices)
        df.loc[f_index, 'hexatic_order_magnitude'] = pd.Series(np.abs(psi_6), index=frame_indices)
        df.loc[f_index, 'hexatic_order_phase'] = pd.Series(np.angle(psi_6), index=frame_indices)
        df.loc[f_index, 'number_of_neighbours'] = pd.Series(num_neighbors, index=frame_indices, dtype=np.uint8)
    
    return df

@time_it
@error_handling
@param_parse
def _hexatic_order(df, *args, parameters=None, **kwargs):
    """
    Calculates the hexatic order parameter of each particle.
    Optimized to bypass Pandas indexing overhead and handle duplicate frame indices.
    """
    method = parameters.get('method', 'delaunay')
    cutoff = parameters['cutoff']
    f_index = kwargs.get('f_index', None)

    if f_index is None:
        # Using unique() ensures we loop over each frame ID exactly once
        indices = sorted(df.index.unique())
    else:
        indices = [f_index]

    # Pre-allocate lists to hold results per frame
    all_magnitudes = []
    all_phases = []
    all_neighbors = []

    for f in tqdm(indices, desc="Calculating Hexatic order"):
        frame_data = df.loc[f]
        
        # Guard against single-particle frames (Pandas returns a Series instead of a DataFrame)
        if isinstance(frame_data, pd.Series):
            points = frame_data[['x', 'y']].to_numpy(dtype=np.float32).reshape(1, 2)
        else:
            points = frame_data[['x', 'y']].to_numpy(dtype=np.float32)

        # 1. Compute neighbors using vectorized helper functions
        if method == 'delaunay':
            neighbors_data = _find_delaunay_for_hexatic_vectorized(points, cutoff)
        elif method == 'kdtree':
            neighbors_data = _find_kdtree_for_hexatic_parallel(points, cutoff)
        else:
            raise ValueError(f"Unknown method '{method}'")
        
        sum_exp_6j, num_neighbors = neighbors_data

        # 2. Calculate complex hexatic order parameter
        psi_6 = np.zeros(len(points), dtype=complex)
        valid = num_neighbors > 0
        psi_6[valid] = sum_exp_6j[valid] / num_neighbors[valid] 
        
        # Append raw NumPy arrays
        all_magnitudes.append(np.abs(psi_6))
        all_phases.append(np.angle(psi_6))
        all_neighbors.append(num_neighbors.astype(np.uint8))

    # 3. Handle data assignment safely
    if f_index is None:
        # If processing the ENTIRE dataframe, we can concatenate everything
        # and assign it using raw values, ignoring index alignment completely.
        df['hexatic_order_magnitude'] = np.concatenate(all_magnitudes)
        df['hexatic_order_phase'] = np.concatenate(all_phases)
        df['number_of_neighbours'] = np.concatenate(all_neighbors)
    else:
        # If processing just ONE specific frame, assign to that slice directly
        df.loc[f_index, 'hexatic_order_magnitude'] = all_magnitudes[0]
        df.loc[f_index, 'hexatic_order_phase'] = all_phases[0]
        df.loc[f_index, 'number_of_neighbours'] = all_neighbors[0]
    
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

def _find_kdtree_for_hexatic_parallel(points, cutoff, workers=-1):
    num_points = len(points)
    tree = sp.KDTree(points)
    
    # 1. Query all points in parallel.
    # Returns a list of lists of neighbors within the cutoff.
    neighbors_list = tree.query_ball_point(points, r=cutoff, workers=workers)
    
    # 2. Reconstruct flat arrays for vectorized math
    # We need to build (i, j) index pairs
    i_indices = np.repeat(np.arange(num_points), [len(lst) for lst in neighbors_list])
    j_indices = np.concatenate(neighbors_list)
    
    # 3. Filter out self-matches (where i == j)
    mask = i_indices != j_indices
    i_indices = i_indices[mask]
    j_indices = j_indices[mask]
    
    if len(i_indices) == 0:
        return np.zeros(num_points, dtype=complex), np.zeros(num_points, dtype=int)
    
    # 4. Compute displacements, angles, and exponents for ALL valid pairs at once
    disp = points[j_indices] - points[i_indices]
    angles = np.arctan2(disp[:, 1], disp[:, 0])
    exp_6j = np.exp(6j * angles)
    
    # 5. Map the calculations back to particle IDs using fast bincount
    sum_exp_6j = np.bincount(i_indices, weights=exp_6j.real, minlength=num_points) + \
                 1j * np.bincount(i_indices, weights=exp_6j.imag, minlength=num_points)
    
    num_neighbors = np.bincount(i_indices, minlength=num_points)
    
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

@time_it
@error_handling
@param_parse
def neighbours(df, *args, parameters=None, **kwargs):
    f_index = kwargs.get('f_index')
    method = parameters['method']
    
    # Ensure columns exist with correct Arrow Extension types
    if 'neighbours' not in df.columns:
        df['neighbours'] = pd.Series(None, index=df.index, dtype=arrowint32_type)
        df['neighbour_dists'] = pd.Series(None, index=df.index, dtype=arrowf32_type)

    # --- CASE 2: Multi-Frame Path ---
    #Split dataframe into frame sized chunks
    grouped = df.groupby(level=0)
    arrow_ids_chunks = []
    arrow_dists_chunks = []
    
    for frame_id, frame_df in tqdm(grouped, desc="Calculating neighbours"):
        if method == 'delaunay':
            arrow_ids, arrow_dists = _find_delaunay_optimized(frame_df, parameters)
        elif method == 'kdtree':
            arrow_ids, arrow_dists = _find_kdtree_optimized(frame_df, parameters)
        
        arrow_ids_chunks.append(arrow_ids)
        arrow_dists_chunks.append(arrow_dists)

    # Fast chunk concatenation
    final_ids_arrow = pa.chunked_array(arrow_ids_chunks)
    final_dists_arrow = pa.chunked_array(arrow_dists_chunks)
    
    df['neighbours'] = pd.Series(final_ids_arrow.combine_chunks(), index=df.index, dtype=arrowint32_type)
    df['neighbour_dists'] = pd.Series(final_dists_arrow.combine_chunks(), index=df.index, dtype=arrowf32_type)
        
    return df


def _find_kdtree_optimized(df, parameters):
    cutoff = parameters['cutoff']
    num_neighbours = int(parameters['neighbours'])
    
    points = df[['x', 'y']].values
    particle_ids = df['particle'].values
    n_points = len(points)
    
    # 1. Query the KDTree
    tree = sp.KDTree(points)
    distances, indices = tree.query(points, k=num_neighbours + 1, distance_upper_bound=cutoff, workers=-1)
    
    # Strip query-self columns
    distances = distances[:, 1:]
    indices = indices[:, 1:]
    
    # 2. Vectorized Masking
    valid_masks = indices < n_points
    
    # 3. Flatten the data completely to true 1D arrays
    # This prevents PyArrow from seeing any multi-dimensional data structures
    flat_indices = indices[valid_masks]
    flat_dists = distances[valid_masks]
    
    # Map raw indices to actual particle IDs globally in 1D
    flat_mapped_ids = particle_ids[flat_indices]
    
    # 4. Compute row offsets (where each particle's list starts and ends)
    row_counts = np.sum(valid_masks, axis=1)
    offsets = np.insert(np.cumsum(row_counts), 0, 0).astype(np.int32)
    
    # 5. Build native PyArrow ListArrays natively from 1D data structures
    # (Bypasses pa.array completely, maintaining ultra-low RAM and maximum speed)
    pa_ids = pa.ListArray.from_arrays(pa.array(offsets), pa.array(flat_mapped_ids, type=pa.int32()))
    pa_dists = pa.ListArray.from_arrays(pa.array(offsets), pa.array(flat_dists, type=pa.float32()))
    
    return pa_ids, pa_dists



def _find_delaunay_optimized(df, parameters):
    cutoff = parameters['cutoff']
    points = df[['x', 'y']].values
    particle_ids = df['particle'].values
    
    tess = sp.Delaunay(points)
    list_indices, point_indices = tess.vertex_neighbor_vertices

    neighbour_ids_list = []
    neighbour_dists_list = []
    
    for i in range(len(points)):
        p1 = points[i].astype(float)
        delaunay_neighbors = point_indices[list_indices[i]:list_indices[i+1]]
        
        if len(delaunay_neighbors) == 0:
            neighbour_ids_list.append([])
            neighbour_dists_list.append([])
            continue
            
        p2 = points[delaunay_neighbors].astype(float)
        dists = np.linalg.norm(p1 - p2, axis=1)
        valid_mask = dists < cutoff
        
        neighbour_ids_list.append(particle_ids[delaunay_neighbors[valid_mask]].astype(int).tolist())
        neighbour_dists_list.append(dists[valid_mask].astype(float).tolist())
        
    return neighbour_ids_list, neighbour_dists_list

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
    'voronoi_counts' -  How many coords part of a voronoi cell used for reconstruction by annotation


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
    df['voronoi'] = pd.Series([[]] * len(df), index=df.index, dtype=object)
    df['voronoi_counts'] = pd.Series(0, index=df.index, dtype='int64')
    df['voronoi_area'] = pd.Series(np.nan, index=df.index, dtype=float)
    
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

        flat_coords, counts = _get_voronoi_coords(vor)
        
        # Map them back into your frame slices
        df.loc[f_index, 'voronoi'] = pd.Series(flat_coords, index=frame_indices, dtype=object)
        df.loc[f_index, 'voronoi_counts'] = pd.Series(counts, index=frame_indices, dtype='int64')
        df.loc[f_index, 'voronoi_area'] = _voronoi_props(vor)
    return df

def _get_voronoi_coords(vor):
    voronoi_coords = []
    voronoi_counts = []
    
    for index, point in enumerate(vor.points):
        region = vor.point_region[index]
        region_pt_indices = vor.regions[region]
        
        if -1 in region_pt_indices or len(region_pt_indices) == 0:
            # Infinite boundary cells get empty list and 0 vertices
            voronoi_coords.append([])
            voronoi_counts.append(0)
        else:
            region_pt_coords = vor.vertices[region_pt_indices] # Shape (V, 2)
            
            # FIX: Flatten the (V, 2) array into a 1D list [x1, y1, x2, y2...]
            voronoi_coords.append(region_pt_coords.flatten().tolist())
            voronoi_counts.append(len(region_pt_coords)) # Store V (number of vertices)
            
    return voronoi_coords, voronoi_counts

def _old_get_voronoi_coords(vor):
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




def _find_min_id(phi_array,peak_positions):
    """Calculates the id of the crystal to which all particles in the array belong. It implements wrapping so that a phi of 2.8 will find a peak at say -2.8"""
    low_peaks = len(peak_positions[peak_positions<-np.pi])
    num_peaks = len(peak_positions[peak_positions<np.pi]) - low_peaks
    min_id = np.argmin(np.abs(phi_array[:,None] - peak_positions), axis=1) - low_peaks 
    
    min_id[min_id < 0] = min_id[min_id < 0] + num_peaks
    
    min_id[min_id >= num_peaks] = min_id[min_id >= num_peaks] - num_peaks
    return min_id

def crystal_ID_plot(df, parameters):
    '''
    return df with extra column containing crystal ID
    '''
    peak_height = parameters['peak_height']
    smoothing = parameters['smoothing']

    phi = df['hexatic_order_phase']

    hist, bin_edges=np.histogram(phi, bins = 50, range=(-np.pi,np.pi)) # increasing one side allows one edge peak to be identified
    bins = 0.5*(bin_edges[:-1] + bin_edges[1:])

    pad_width = 10
    padded_hist = np.pad(hist, pad_width=pad_width, mode='wrap')

    smoothed_data = gaussian_filter1d(padded_hist, sigma=smoothing)
    padded_peaks, properties = find_peaks(smoothed_data, height=peak_height)
    peaks = padded_peaks

    #dont include in particle tracker
    bin_width = bins[1] - bins[0]
    left_bins = bins[-pad_width:] - (len(bins) * bin_width)
    right_bins = bins[:pad_width] + (len(bins) * bin_width)
    padded_bins = np.concatenate([left_bins, bins, right_bins])

    
    plt.plot(padded_bins, padded_hist, label = 'padded data')
    plt.plot(padded_bins, smoothed_data, 'g-', label = 'smoothed')
    plt.plot(bins, hist, 'x', label = 'Histogram')
    plt.plot(padded_bins[peaks], padded_hist[peaks], 'ro', label = 'peak selected if inside pi')
    plt.xlabel('Hexatic_order_phase [deg]')
    plt.ylabel('n')
    plt.legend()

    
    plt.axvline(-np.pi, color='r', linestyle = '--')
    plt.axvline(np.pi, color='r', linestyle = '--')
    plt.show()

@time_it
@error_handling
@param_parse
def crystal_id(df, *args, parameters=None, **kwargs):
    #print('inside crystal id')
    if 'crystal_id' not in df.columns:
        df['crystal_id'] = np.nan #pd.Series(np.nan, index=df.index, dtype='Int64')
    
    f_index = kwargs['f_index']
    if f_index is None:
        #process all frames
        indices = list(set(df.index.values.tolist()))
    else:
        #Just process frame of interest
        indices=[f_index]
    
    for f_index in indices:
        df.loc[f_index,['crystal_id']] =_crystal_id(df.loc[f_index], parameters=parameters)
    return df


def _crystal_id(df, *args, parameters=None, **kwargs):
    """Crystal ID finds clusters of a particular phase in the hexatic order parameter and assigns them an id.
    It returns a series which labels each particle according to which crystal it is a part of.
    
    params:

    peak_height = min height of a peak to be detected
    smoothing: width of gaussian in smoothing out peaks in the histogram used for detection.

    return df with extra column containing crystal ID
    """

    n_bins = 50
    pad_width = 10
    peak_height = parameters['peak_height']
    smoothing = parameters['smoothing']
    debug = parameters['debug']

    phi = df['hexatic_order_phase'].to_numpy(dtype=np.float32, na_value=np.nan)

    hist, bin_edges=np.histogram(phi, bins = n_bins, range=(-np.pi,np.pi)) # increasing one side allows one edge peak to be identified
    bins = 0.5*(bin_edges[:-1] + bin_edges[1:])

    padded_hist = np.pad(hist, pad_width=pad_width, mode='wrap')
    right_bins = bins[:pad_width] + (len(bins) * (bins[1]-bins[0]))
    left_bins = bins[-pad_width:] - (len(bins) * (bins[1]-bins[0]))
    padded_bins = np.concatenate([left_bins ,bins, right_bins])

    smoothed_data = gaussian_filter1d(padded_hist, sigma=smoothing)
    padded_peaks, properties = find_peaks(smoothed_data, height=peak_height)
    #peaks = (padded_peaks - pad_width)
    peaks=padded_peaks

    phi_array = np.array(phi)
    df['crystal_id'] = _find_min_id(phi_array, padded_bins[peaks])

    #plotting(df)
    if debug:
        crystal_ID_plot(df, parameters)

    return df  

@time_it
@error_handling
@param_parse
def boundary_and_tj_id(df, *args, parameters=None, **kwargs):
    """
    Identify particles with neighbours in differrent crystals.
    requires hexatic_order, Neighbours(~20) and crystal_id to have been run.    

    Parameters
    ----------
    min_neighours_gb 
        minimum number of 2 different crystal in a particles neighbourhood, to be assigned GB
    min_neighbours_tj
        min number of 3 different crystals in a neighbourhood for a particle to be considered a triple junction.
    
    Args
    ----
    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)

    Returns
    -------
        updated dataframe including new columns "is_boundary" and "is_triple_junction", boolean denoting GB and TJ particles. 

    """
    #print('inside boundary id')
    #define new columns
    if 'is_triple_junction' not in df.columns:
        df['is_boundary'] = pd.Series(np.nan, index=df.index, dtype=bool)
        df['is_triple_junction'] = pd.Series(np.nan, index=df.index, dtype=bool)

    f_index = kwargs['f_index']
    if f_index is None:
        #process all frames
        indices = list(set(df.index.values.tolist()))
    else:
        #Just process frame of interest
        indices=[f_index]
    
    for f_index in indices:
        df.loc[f_index,['is_boundary', 'is_triple_junction']] =_boundary_and_tj_id(df.loc[f_index], parameters=parameters)
    return df

def _boundary_and_tj_id(df, *args, parameters=None, **kwargs):
    """
    Identify particles with neighbours in differrent crystals.
    requires hexatic_order, Neighbours(~20) and crystal_id to have been run.    

    Parameters
    ----------
    min_neighours_gb 
        minimum number of 2 different crystal in a particles neighbourhood, to be assigned GB
    min_neighbours_tj
        min number of 3 different crystals in a neighbourhood for a particle to be considered a triple junction.
    
    Args
    ----
    df
        The dataframe in which all data is stored
    f_index
        Integer specifying the frame for which calculations need to be made.
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)

    Returns
    -------
        updated dataframe including new columns "is_boundary" and "is_triple_junction", boolean denoting GB and TJ particles. 

    """

    #define parameters
    min_neighbours_gb = parameters['min_neighbours_gb']
    min_neighbours_tj = parameters['min_neighbours_tj']

    
    # build lookup array to map particle ID to crystal ID
    lookup_series = df.set_index("particle")["crystal_id"] + 1 #plus one to make all crystal numbers above 0
    max_id = df["particle"].max()
    #print("max_id = ", max_id)
    full_lookup = np.zeros(max_id + 2, dtype=int)
    full_lookup[lookup_series.index] = lookup_series.values
    # Set the dummy particle's crystal_id to 0 (indicating no crystal)
    full_lookup[-1] = 0

    # convert neighbours column to list
    neighbor_lists = df["neighbours"].to_numpy()
    num_particles = len(df)
    max_neighbors = max(len(n) for n in neighbor_lists)
    #create matrix of neighbour ids, -1 in empty spaces points to dummy particle with crystal_id 0
    neighbors_matrix = np.full((num_particles, max_neighbors), -1, dtype=int)
    #populate matrix with neighbour ids
    for i, n in enumerate(neighbor_lists):
        neighbors_matrix[i, : len(n)] = n

    # create new array with neigbours crystal ID rather than particle ID
    neighbor_crystals = full_lookup[neighbors_matrix]

    # add particles own crystal to the first column
    own_crystals = (df["crystal_id"].to_numpy()[:, np.newaxis] + 1).astype(int)
    full_neighborhood = np.hstack((own_crystals, neighbor_crystals))
    
    max_val = np.max(full_neighborhood)
    if max_val < 1:
        max_val = 1
        
    crystal_id_values = np.arange(1, max_val + 1)
    counts = np.vstack([np.bincount(row, minlength=crystal_id_values[-1] + 1)[crystal_id_values] for row in full_neighborhood])

    df['is_boundary'] = np.sum(counts >= min_neighbours_gb, axis=1) >= 2
    df['is_triple_junction'] = np.sum(counts >= min_neighbours_tj, axis=1) >= 3

    return df



def _boundary_and_tj_id_fast(df, *args, parameters=None, **kwargs):
    min_neighbours_gb = parameters['min_neighbours_gb']
    min_neighbours_tj = parameters['min_neighbours_tj']
    
    # 1. Use standard types for the mapping to avoid the ExtensionArray '_hasna' bug
    # Zip native numpy/python types instead of the Series object directly
    particles = df['particle'].to_numpy(dtype=np.int64)
    crystals = df['crystal_id'].to_numpy(dtype=np.int64)
    crystal_map = dict(zip(particles, crystals))
    
    # 2. Explode using a clean slice of the original dataframe
    exploded = df[['particle', 'neighbours']].explode('neighbours')
    
    # Drop any rows where a particle has no neighbors (None/NaN)
    exploded = exploded.dropna(subset=['neighbours'])
    
    # 3. Force neighbor IDs to clean int64 so the dictionary map can read them seamlessly
    exploded['neighbours'] = exploded['neighbours'].astype(np.int64)
    
    # 4. Map the neighbor particles to their crystal IDs
    exploded['neighbor_crystal'] = exploded['neighbours'].map(crystal_map)
    
    # Drop any neighbors that couldn't be mapped (like your -1 dummy pointers)
    valid_neighbors = exploded.dropna(subset=['neighbor_crystal'])
    
    # 5. Group by particle and neighbor crystal to count occurrences per crystal
    counts_per_grain = valid_neighbors.groupby(['particle', 'neighbor_crystal']).size().reset_index(name='count')
    
    # --- APPLY YOUR SIMPLIFIED DEFINITIONS ---
    
    # Boundary: Must have >= min_neighbours_gb in at least 2 different crystals
    gb_condition = counts_per_grain['count'] >= min_neighbours_gb
    gb_counts = counts_per_grain[gb_condition].groupby('particle').size()
    gb_particles = gb_counts[gb_counts >= 2].index
    
    # Triple Junction: Must have >= min_neighbours_tj in at least 3 different crystals
    tj_condition = counts_per_grain['count'] >= min_neighbours_tj
    tj_counts = counts_per_grain[tj_condition].groupby('particle').size()
    tj_particles = tj_counts[tj_counts >= 3].index
    
    # 6. Map results back safely using the original data type
    df['is_boundary'] = df['particle'].isin(gb_particles)
    df['is_triple_junction'] = df['particle'].isin(tj_particles)
    
    return df