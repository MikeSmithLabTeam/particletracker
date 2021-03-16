import numpy as np
import scipy.spatial as sp
import trackpy as tp
import cv2
import os
import pandas as pd

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
    Angle assumes you want to calculate from x_column as x and y_column as y
    it uses tan2 so that -x and +y give a different result to +x and -y
    Angles are output in radians or degrees given by parameters['angle']['units']
    If you want to get the angle along a trajectory you need to run the running difference
    method on each column of x and y coords to create dx,dy then send this to angle.


    Parameters  :
    
    x_column    :   x component of the df for calculating angle
    y_column    :   y component of the df for calculating angle
    output_name :   New column name to store angle df
    units     :   'degrees' or 'radians'
    
    Inputs:

    df        :   The dfframe of all collected df
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dfframe of all df

    '''
    try:
        method_key = get_method_key('angle', call_num)
        columnx = parameters[method_key]['x_column']
        columny = parameters[method_key]['y_column']
        output_name = parameters[method_key]['output_name']
        units=get_param_val(parameters[method_key]['units'])

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
    Takes a column of df and classifies whether its values are within 
    the specified range. 

    Parameters  :

    column_name     :   input df column
    output_name     :   column name for classier
    lower_threshold :   min value to belong to classifier
    upper_threshold':   max value to belong to classifier
    
    Inputs:

    df        :   The entire stored dataframe
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dfframe of all df

    '''

    try:
        method_key = get_method_key('classify', call_num)
        column = parameters[method_key]['column_name']
        output_name=parameters[method_key]['output_name']
        lower_threshold_value = get_param_val(parameters[method_key]['lower_threshold'])
        upper_threshold_value = get_param_val(parameters[method_key]['upper_threshold'])

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


def contour_area(df, f_index=None, parameters=None, call_num=None):
    '''
    Calculate the area of a contour. 

    Parameters  :
    
    output_name :   New column name to store area df
    
    Inputs:

    df        :   The dfframe of all collected df
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dfframe of all df

    '''
    try:
        method_key = get_method_key('contour_area', call_num)
        output_name = parameters[method_key]['output_name']

        if output_name not in df.columns:
            df[output_name] = np.nan
        
        df_frame = df.loc[f_index]
        contours = df_frame[['contours']].values
        areas = []

        if np.shape(contours)[0] == 1:
            df_empty = np.isnan(contours[0])
            if np.all(df_empty):
                #0 contours
                return df
        
        for index, contour in enumerate(contours):
            areas.append(cv2.contourArea(contour[0]))

        df_frame[output_name] = np.array(areas)
        df.loc[f_index] = df_frame
        return df
    except Exception as e:
        raise ContourAreaError(e)

def contour_boxes(df, f_index=None, parameters=None, call_num=None):

    try:
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

    Parameters  :

    column_name     :   input df column
    column_name2    :   input df column 2
    output_name     :   column name for classier
        
    Inputs:

    df        :   The dfframe of all collected df
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dfframe of all df

    '''
    
    try:
        method_key = get_method_key('logic_AND', call_num)
        column1 = parameters[method_key]['column_name']
        column2 = parameters[method_key]['column_name2']
        output_name = parameters[method_key]['output_name']
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

    Parameters  :

    column_name     :   input df column
    output_name     :   column name for classier
        
    Inputs:

    df        :   The dfframe of all collected df
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dfframe of all df

    '''

       
    try:
        method_key = get_method_key('logic_NOT', call_num)
        column = parameters[method_key]['column_name']
        output_name = parameters[method_key]['output_name']
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

    Parameters  :

    column_name     :   input df column
    column_name2     :   input df column 2
    output_name     :   column name for classier
        
    Inputs:

    df        :   The dfframe of all collected df
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dfframe of all df

    '''

    
    try:
        method_key = get_method_key('logic_OR', call_num)
        column1 = parameters[method_key]['column_name']
        column2 = parameters[method_key]['column_name2']
        output_name = parameters[method_key]['output_name']

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

    Parameters  :
    
    column_name     :   First column
    column_name     :   Second column
    output_name     :   Column name for magnitude df
    
    Inputs:

    df        :   The dfframe of all collected df
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dfframe of all df

    '''
    try:
        method_key=get_method_key('magnitude', call_num)
        column = parameters[method_key]['column_name']
        column2 = parameters[method_key]['column_name2']
        output_name = parameters[method_key]['output_name']
        
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
    Neighbours uses either a kdtree or a delaunay method to locate the neighbours
    of particles in a particular frame. It returns the indices of the particles
    found to be neighbours in a list. You can also select a cutoff distance above which
    two particles are no longer considered to be neighbours. The kdtree essentially finds
    those particles closest. The delaunay method is explained here: https://en.wikipedia.org/wiki/Delaunay_triangulation

    Parameters  :

    method     :   'delaunay' or 'kdtree'
    neighbours     :   max number of neighbours to find. This is only relevant for the kdtree.
    output_name     :   column name for classier
        
    Inputs:

    df        :   The dfframe of all collected df
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dfframe of all df

    '''
    try:
        #https: // docs.scipy.org / doc / scipy / reference / generated / scipy.spatial.Delaunay.html
        method_key = get_method_key('neighbours', call_num)
        method = get_param_val(parameters[method_key]['method'])
        
        if 'neighbours' not in df.columns:
            df['neighbours'] = np.nan
        df_frame = df.loc[f_index]

        if method == 'delaunay':
            df_frame =_find_delaunay(df_frame, parameters=parameters)
        elif method == 'kdtree':
             df_frame =_find_kdtree(df_frame, parameters=parameters)     
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
    try:
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


'''
---------------------------------------------------------------------------------------------
All these methods depend on information from other frames. ie they won't work unless
multiple frames have been processed and you are using part.
---------------------------------------------------------------------------------------------
'''
def difference(df, f_index=None, parameters=None, call_num=None):
    '''
    Difference in frames of a column of dfframe.
    The differences are calculated at separations equal
    to span along the column. Where this is not possible
    eg at both ends of column, the value np.Nan is inserted.
    
    Parameters  :
    
    column_name     :   Column name to calculate differences on
    output_name     :   Name to give to calculated df'x_diff',
    span            :   Gap in frames to calculate difference on
    
    Inputs:

    df        :   The dfframe of all collected df
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dfframe of all df

    '''
    try:    
        method_key = get_method_key('difference', call_num)
        column = parameters[method_key]['column_name']
        output_name = parameters[method_key]['output_name']
        span = get_param_val(parameters[method_key]['span'])
    
        if output_name not in df.columns:
            df[output_name] = np.nan

        start=f_index-span - 1
        if start < 0:
            start = 0
        
        df_frames = df.loc[start:f_index,[column,'particle']]
        df_output=df_frames.groupby('particle')[column].diff(periods=span).transform(lambda x:x).to_frame(name=output_name)
        df.loc[f_index,[output_name]]=df_output.loc[f_index]
    
        return df
    except Exception as e:
        raise DifferenceError(e)

def mean(df, f_index=None, parameters=None, call_num=None):
    '''
    Rolling Mean of a column of values. Returns the mean of a particle's values to a new
    column.

    Parameters  :
    
    column_name     :   Input column name
    output_name     :   Column name for max df
    span            :   number of frames over which to calculate rolling mean
    
    Inputs:

    df        :   The dfframe of all collected df
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all df

    '''
    

    try:
        method_key = get_method_key('mean', call_num)
        column = parameters[method_key]['column_name']
        output_name = parameters[method_key]['output_name']
        span = get_param_val(parameters[method_key]['span'])

        if output_name not in df.columns:
            df[output_name] = np.nan

        start=f_index-span - 1
        if start < 0:
            start = 0
        
        df_frames = df.loc[start:f_index,[column,'particle']]
        df_output=df_frames.groupby('particle')[column].rolling(span).mean().transform(lambda x:x).to_frame(name=output_name)
        df.loc[f_index,[output_name]]=df_output.loc[f_index]
        return df
    except Exception as e:
        raise MeanError(e)

def median(df, f_index=None, parameters=None, call_num=None):
    '''
    Median of a columns values. Returns the median of a particle's values to a new
    column.

    Parameters  :
    
    column_name     :   Input column name
    output_name     :   Column name for median df
    span            :   number of frames over which to calculate rolling median
    
    Inputs:

    df        :   The dfframe of all collected df
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dfframe of all df

    '''
    
    try:
        method_key = get_method_key('median', call_num)
        column = parameters[method_key]['column_name']
        output_name = parameters[method_key]['output_name']
        span = get_param_val(parameters[method_key]['span'])
       
        if output_name not in df.columns:
            df[output_name] = np.nan

        start=f_index-span - 1
        if start < 0:
            start = 0
        
        df_frames = df.loc[start:f_index,[column,'particle']]
        df_output=df_frames.groupby('particle')[column].rolling(span).median().transform(lambda x:x).to_frame(name=output_name)
        df.loc[f_index,[output_name]]=df_output.loc[f_index]
    
        return df
    except Exception as e:
        raise MedianError(e)


def rate(df, f_index=None, parameters=None, call_num=None):
    '''
    Rate of change of df in a column. Rate function takes an input column and calculates the
    rate of change of the quantity. It takes into account
    the fact that particles go missing from frames. Where this
    is the case the rate = change in quantity between observations
    divided by the gap between observations.
    Nans are inserted at end and beginning of particle trajectories
    where calc is not possible.

    We sort by particle and then calculate diffs. This leads to differences
    between pairs of particles above one another in dfframe. We then backfill
    these slots with Nans.

    Parameters  :

    column_name     :   Input column names
    output_name     :   Output column name
    fps             :   numerical value indicating the number of frames per second
    span            :   number of frames over which to calculate rolling difference
    
    
    Inputs:

    df        :   The dfframe of all collected df
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dfframe of all df

    '''
    try:
        method_key = get_method_key('rate', call_num)
        column = parameters[method_key]['column_name']
        output_name = parameters[method_key]['output_name']
        span = get_param_val(parameters[method_key]['span'])
        fps= parameters[method_key]['fps']

        if output_name not in df.columns:
            df[output_name] = np.nan

        start=f_index-span - 1
        if start < 0:
            start = 0
        
        df_frames = df.loc[start:f_index,[column,'particle']]
        df_output=df_frames.groupby('particle')[column].diff(periods=span).transform(lambda x:x).to_frame(name=output_name)
        df.loc[f_index,[output_name]]=df_output.loc[f_index]*float(fps)

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
    Allows you to manually add a new column of df to the dfframe. The df
    is df which has a single value per frame. This is done by creating a .csv
    or .xlsx file and reading it in within the gui. The file should have two columns
    The first column should have a complete list of all the frame numbers starting at zero
    The second column should have the df for each frame listed. It can either be a .csv 
    or a .xlsx file.

    Parameters  :
    df_filename       :   Filename with extension for the df to be loaded.
    new_column_name     :   Name for column to which df is to be imported.    

    Inputs:

    df        :   The dfframe of all collected df
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dfframe of all df. 

    '''
    try:
        method_key = get_method_key('add_frame_data', call_num)
        datapath = parameters[method_key]['data_path']

        if '.csv' in parameters[method_key]['data_filename']:
            filename = os.path.join(datapath,parameters[method_key]['data_filename'])
            new_df = pd.read_csv(filename, header=None)
        elif '.xlsx' in parameters[method_key]['data_filename']:
            new_df = pd.read_excel(parameters[method_key]['data_filename'],squeeze=True)
        else:
            print('Unknown file type')
        df[parameters[method_key]['new_column_name']] = new_df
    
        return df
    except  Exception as e:
        raise AddFrameDataError(e)
    






