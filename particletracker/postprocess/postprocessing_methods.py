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
All these methods operate on all frames simultaneously
-------------------------------------------------------------------------------------------------------
'''
def angle(data, f_index=None, parameters=None, call_num=None):
    '''
    Angle assumes you want to calculate from x_column as x and y_column as y
    it uses tan2 so that -x and +y give a different result to +x and -y
    Angles are output in radians or degrees given by parameters['angle']['units']
    If you want to get the angle along a trajectory you need to run the running difference
    method on each column of x and y coords to create dx,dy then send this to angle.


    Parameters  :
    
    x_column    :   x component of the data for calculating angle
    y_column    :   y component of the data for calculating angle
    output_name :   New column name to store angle data
    units     :   'degrees' or 'radians'
    
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''
    try:
        method_key = get_method_key('angle', call_num)
        columnx = parameters[method_key]['x_column']
        columny = parameters[method_key]['y_column']
        output_name = parameters[method_key]['output_name']
        data[output_name] = np.arctan2(data[columnx]/data[columny])
        return data
    except Exception as e:
        raise AngleError(e)


def contour_area(data, f_index=None, parameters=None, call_num=None):
    '''
    Calculate the area of a contour. 

    Parameters  :
    
    output_name :   New column name to store area data
    
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''
    try:
        method_key = get_method_key('contour_area', call_num)
        output_name = parameters[method_key]['output_name']
        contours = data['contours'].tolist()
        areas = []
        for contour in contours:
            areas.append(cv2.contourArea(contour))

        data[output_name] = np.array(areas)
        return data
    except Exception as e:
        raise ContourAreaError(e)

def difference(data, f_index=None, parameters=None, call_num=None):
    '''
    Difference in frames of a column of dataframe.
    The differences are calculated at separations equal
    to span along the column. Where this is not possible
    or at both ends of column, the value np.Nan is inserted.
    
    Parameters  :
    
    column_name     :   Column name to calculate differences on
    output_name     :   Name to give to calculated data'x_diff',
    span            :   Gap in frames to calculate difference on
    
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''
    try:
        method_key = get_method_key('difference', call_num)
        span = get_param_val(parameters[method_key]['span'])
        column = parameters[method_key]['column_name']
        output_name = parameters[method_key]['output_name']
        data.index.name = 'index'
        data = data.sort_values(['particle', 'frame'])
        data[output_name] = data[column].diff(periods=span)
        data['nan'] = data['particle'].diff(periods=span).astype(bool)

        data[output_name][data['nan'] == True] = np.NaN
        data.drop(labels='nan',axis=1)
        return data
    except Exception as e:
        raise DifferenceError(e)

def magnitude(data, f_index=None, parameters=None, call_num=None):
    '''
    Calculates the magnitude of 2 input columns (x^2 + y^2)^0.5 = r

    Parameters  :
    
    column_name     :   First column
    column_name     :   Second column
    output_name     :   Column name for magnitude data
    
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''
    try:
        method_key=get_method_key('magnitude', call_num)
        column = parameters[method_key]['column_name']
        column2 = parameters[method_key]['column_name2']
        output_name = parameters[method_key]['output_name']
        data[output_name] = (data[column]**2 + data[column2]**2)**0.5
        return data
    except Exception as e:
        raise MagnitudeError(e)

def max(data, f_index=None, parameters=None, call_num=None):
    '''
    Max of a columns values. Returns the max of a particle's trajectory values to a new
    column. The value is repeated next to all entries for that trajectory
    Calculates the magnitude of 2 input columns (x^2 + y^2)^0.5 = r

    Parameters  :
    
    column_name     :   First column
    output_name     :   Column name for max data
    
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''
    try:
        method_key = get_method_key('max', call_num)
        column = parameters[method_key]['column_name']
        output_name = parameters[method_key]['output_name']
        temp=data.groupby('particle')[column].transform('max')
        data[output_name] = temp
        return data
    except Exception as e:
        raise MaxError(e)

def mean(data, f_index=None, parameters=None, call_num=None):
    '''
     Mean of a columns values. Returns the mean of a particle's trajectory values to a new
    column. The value is repeated next to all entries for that trajectory

    Parameters  :
    
    column_name     :   Input column name
    output_name     :   Column name for max data
    
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''
    
    try:
        method_key = get_method_key('mean', call_num)
        column = parameters[method_key]['column_name']
        output_name = parameters[method_key]['output_name']
        temp=data.groupby('particle')[column].transform('mean')
        data[output_name] = temp
        return data
    except Exception as e:
        raise MeanError(e)

def median(data, f_index=None, parameters=None, call_num=None):
    '''
     Median of a columns values. Returns the median of a particle's trajectory values to a new
    column. The value is repeated next to all entries for that trajectory

    Parameters  :
    
    column_name     :   Input column name
    output_name     :   Column name for max data
    
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''
    
    try:
        method_key = get_method_key('median', call_num)
        column = parameters[method_key]['column_name']
        output_name = parameters[method_key]['output_name']
        temp=data.groupby('particle')[column].transform('median')
        data[output_name] = temp
        return data
    except Exception as e:
        raise MedianError(e)

def min(data, f_index=None, parameters=None, call_num=None):
    '''
     Minimum of a columns values. Returns the minimum of a particle's trajectory values to a new
    column. The value is repeated next to all entries for that trajectory

    Parameters  :
    
    column_name     :   Input column name
    output_name     :   Column name for max data
    
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''
    try:
        method_key = get_method_key('min', call_num)
        column = parameters[method_key]['column_name']
        output_name = parameters[method_key]['output_name']
        temp=data.groupby('particle')[column].transform('min')
        data[output_name] = temp
        return data
    except Exception as e:
        raise MinError(e)

def rate(data, f_index=None, parameters=None, call_num=None):
    '''
    Rate of change of data in a column. Rate function takes an input column and calculates the
    rate of change of the quantity. It takes into account
    the fact that particles go missing from frames. Where this
    is the case the rate = change in quantity between observations
    divided by the gap between observations.
    Nans are inserted at end and beginning of particle trajectories
    where calc is not possible.

    We sort by particle and then calculate diffs. This leads to differences
    between pairs of particles above one another in dataframe. We then backfill
    these slots with Nans.

    Parameters  :

    column_name     :   Input column names
    output_name     :   Output column name
    fps             :   numerical value indicating the number of frames per second
    method          :   finite_difference
    
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''
    try:
        method_key = get_method_key('rate', call_num)
        column = parameters[method_key]['column_name']
        output_name = parameters[method_key]['output_name']

        data = data.sort_values(['particle', 'index'])
        #Change and time over which change happened
        data['temp_diff'] = data[column].diff()
        data['nan'] = data['particle'].diff().astype(bool)
        data['temp_diff'][data['nan'] == True] = np.NaN
        data['time'] = (1/parameters[method_key]['fps'])*data.index
        data['dt']=data['time'].diff()
        #Put Nans in values crossing particles.
        data[data['dt'] < 0]['dt'] == np.NaN
        data[output_name] = data['temp_diff'] / data['dt']
        #remove temporary columns
        data.drop(labels=['nan','temp_diff','dt'], axis=1)
        return data
    except Exception as e:
        raise RateError(e)

def _classify_fn(x, lower_threshold_value=None, upper_threshold_value=None):
    if (x > lower_threshold_value) and (x < upper_threshold_value):
        return True
    else:
        return False
    
def classify_most(data, f_index=None, parameters=None, call_num=None):
    '''
    Takes a columns of boolean values and for each particle returns the 
    most common value. ie Particle 1: True, True, False, True, True becomes 
    True, True, True, True, True. Particle 2: False, True, False, False, False
    becomes False, False, False, False, False. This is useful because measurements
    fluctuate and so you want to colour code particles that generally are or are 
    not something.
    
    Parameters  :

    column_name     :    input column name
    output_name     :    output column name
   
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''
    
    try:
        method_key = get_method_key('classify_most', call_num)
        column = parameters[method_key]['column_name']
        output_name=parameters[method_key]['output_name']
        temp=data.groupby('particle')[column].transform('median')
        data[output_name] = temp
        return data
    except Exception as e:
        raise ClassifyMostError(e)

def classify(data, f_index=None, parameters=None, call_num=None):
    '''
    Takes a column of data and classifies the data. 

    Parameters  :

    column_name     :   input data column
    output_name     :   column name for classier
    lower_threshold :   min value to belong to classifier
    upper_threshold':   max value to belong to classifier
    
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''

    try:
        method_key = get_method_key('classify', call_num)
        column = parameters[method_key]['column_name']
        output_name=parameters[method_key]['output_name']
        lower_threshold_value = get_param_val(parameters[method_key]['lower_threshold'])
        upper_threshold_value = get_param_val(parameters[method_key]['upper_threshold'])
        data[output_name] = data[column].apply(_classify_fn, lower_threshold_value=lower_threshold_value, upper_threshold_value=upper_threshold_value)
        return data
    except Exception as e:
        raise ClassifyError(e)

def logic_NOT(data, f_index=None, parameters=None, call_num=None):
    '''
    Apply a logical not operation to a column of boolean values.

    Parameters  :

    column_name     :   input data column
    output_name     :   column name for classier
        
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''

       
    try:
        method_key = get_method_key('logic_NOT', call_num)
        column = parameters[method_key]['column_name']
        output_name = parameters[method_key]['output_name']
        data[output_name] = ~data[column]
    except Exception as e:
        raise LogicNotError(e)

def logic_AND(data, f_index=None, parameters=None, call_num=None):
    '''
    Applys a logical and operation to two columns of boolean values.

    Parameters  :

    column_name     :   input data column
    column_name2    :   input data column 2
    output_name     :   column name for classier
        
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''

    
    
    try:
        method_key = get_method_key('logic_AND', call_num)
        column1 = parameters[method_key]['column_name']
        column2 = parameters[method_key]['column_name2']
        output_name = parameters[method_key]['output_name']
        data[output_name] = data[column1] * data[column2]
    except Exception as e:
        raise LogicAndError(e)

def logic_OR(data, f_index=None, parameters=None, call_num=None):
    '''
    Apply a logical or operation to two columns of boolean values.

    Parameters  :

    column_name     :   input data column
    column_name2     :   input data column 2
    output_name     :   column name for classier
        
    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data

    '''

    
    try:
        method_key = get_method_key('logic_OR', call_num)
        column1 = parameters[method_key]['column_name']
        column2 = parameters[method_key]['column_name2']

        output_name = parameters[method_key]['output_name']
        data[output_name] = data[column1] + data[column2]
    except  Exception as e:
        raise LogicOrError(e)

def subtract_drift(data, f_index=None, parameters=None, call_num=None):
    '''
    subtract drift from an x,y coordinate trajectory.

    Parameters  :

    No Parameters

    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data. The input data is automatically pulled from x, y
    The output data is placed in columns x_drift, y_drift

    '''
    
    try:
        method_key = get_method_key('subtract_drift', call_num)
        drift = tp.motion.compute_drift(data)
        drift_corrected = tp.motion.subtract_drift(data.copy(), drift)
        drift_corrected.index.name = 'index'
        drift_corrected=drift_corrected.sort_values(['particle','index'])
        data[['x_drift','y_drift']] = drift_corrected[['x','y']]
        return data
    except Exception as e:
        raise SubtractDriftError(e)

def add_frame_data(data, f_index=None, parameters=None, call_num=None):
    '''
    Allows you to manually add a new column of data to the dataframe. The data
    is data which has a single value per frame. This is done by creating a .csv
    or .xlsx file and reading it in within the gui. The file should have two columns
    The first column should have a complete list of all the frame numbers starting at zero
    The second column should have the data for each frame listed. It can either be a .csv 
    or a .xlsx file.

    Parameters  :
    data_filename       :   Filename with extension for the data to be loaded.
    new_column_name     :   Name for column to which data is to be imported.    

    Inputs:

    data        :   The dataframe of all collected data
    f_index     :   Integer specifying the frame for which calculations need to be made.
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    updated dataframe of all data. 

    '''
    try:
        method_key = get_method_key('add_frame_data', call_num)
        datapath = parameters[method_key]['data_path']

        if '.csv' in parameters[method_key]['data_filename']:
            filename = os.path.join(datapath,parameters[method_key]['data_filename'])
            new_data = pd.read_csv(filename, header=None)
        elif '.xlsx' in parameters[method_key]['data_filename']:
            new_data = pd.read_excel(parameters[method_key]['data_filename'],squeeze=True)
        else:
            print('Unknown file type')
        data[parameters[method_key]['new_column_name']] = new_data
        return data
    except  Exception as e:
        raise AddFrameDataError(e)
    

'''
--------------------------------------------------------------------------------------------------------------
All methods below here need to be run on each frame sequentially.
---------------------------------------------------------------------------------------------------------------
'''

def _every_frame(data, f_index):
    if f_index is None:
        frame_numbers = data['frame'].values
        start=np.min(frame_numbers)
        stop=np.max(frame_numbers)
    else:
        start=f_index
        stop=f_index+1
    return range(start, stop, 1)
    
def neighbours(df, f_index=None, parameters=None, call_num=None,):
    try:
        #https: // docs.scipy.org / doc / scipy / reference / generated / scipy.spatial.Delaunay.html
        method_key = get_method_key('neighbours', call_num)
        method = get_param_val(parameters[method_key]['method'])
        df['neighbours'] = np.NaN
        for f in _every_frame(df, f_index):
            df_temp = df.loc[f]

            if method == 'delaunay':
                df_temp =_find_delaunay(df_temp, parameters=parameters)
            elif method == 'kdtree':
                df_temp =_find_kdtree(df_temp, parameters=parameters)
            df.loc[f] = df_temp
        return df
    except Exception as e:
        raise NeighboursError(e)


def _find_kdtree(df, parameters=None):
    method_key = get_method_key('neighbours')
    cutoff = get_param_val(parameters[method_key]['cutoff'])
    num_neighbours = get_param_val(parameters[method_key]['neighbours'])
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

def _get_class_subset(data, f, parameters, method=None):
    classifier_column= parameters[method]['classifier_column']
    if classifier_column is None:
        subset_df = data.df.loc[f]
    else:
        classifier = parameters[method]['classifier']
        temp = data.df.loc[f]
        subset_df = temp[temp[classifier_column] == classifier]
    return subset_df
