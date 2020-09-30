import numpy as np
from ParticleTrackingGui.general.parameters import get_method_key, get_param_val
import scipy.spatial as sp
import trackpy as tp

'''
-----------------------------------------------------------------------------------------------------
All these methods operate on all frames simultaneously
-------------------------------------------------------------------------------------------------------
'''

def difference(data, f_index=None, parameters=None, call_num=None):
    '''Difference in time of a column of dataframe.

    Notes
    -----

    The differences are calculated at separations equal
    to span along the column. Where this is not possible
    or at both ends of column, the value np.Nan is inserted.

    Returns
    -------

    Dataframe with new column of rolling differences named according to outputname in PARAMETERS

    '''

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

def rate(data, f_index=None, parameters=None, call_num=None):
    '''Rate of change of data in a column

    Notes
    -----

    rate function takes an input column and calculates the
    rate of change of the quantity. It takes into account
    the fact that particles go missing from frames. Where this
    is the case the rate = change in quantity between observations
    divided by the gap between observations.
    Nans are inserted at end and beginning of particle trajectories
    where calc is not possible.

    We sort by particle and then calculate diffs. This leads to differences
    between pairs of particles above one another in dataframe. We then backfill
    these slots with Nans.

    Returns
    -------

    Pandas dataframe with new column named according to outputname in PARAMETERS

    '''

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

def magnitude(data, f_index=None, parameters=None, call_num=None):
    ''' Calculates the magnitude of 2 input columns (x^2 + y^2)^0.5 = r

    Notes
    -----

    Combines 2 columns according to (x**2 + y**2)**0.5

    Returns
    -------

    Pandas dataframe with new column named according to outputname in PARAMETERS

    '''

    method_key=get_method_key('magnitude', call_num)
    columns = parameters[method_key]['column_names']
    output_name = parameters[method_key]['output_name']
    column_data=data[[columns[0],columns[1]]]
    if np.size(columns) == 2:
        data[output_name] = (column_data[columns[0]]**2 + column_data[columns[1]]**2)**0.5
    elif np.size(columns) == 3:
        data[output_name] = (column_data[columns[0]]**2 + column_data[columns[1]]**2 + column_data[columns[2]]**2)**0.5
    return data

def angle(data, f_index=None, parameters=None, call_num=None):
    '''Angle between 2 sets of data at a given time

    Notes
    -----

    Angle assumes you want to calculate from column_data[0] as x and column_data[1] as y
    it uses tan2 so that -x and +y give a different result to +x and -y
    Angles are output in radians or degrees given by parameters['angle']['units']
    If you want to get the angle along a trajectory you need to run the running difference
    method on each column of x and y coords to create dx,dy then send this to angle.

    Returns
    -------

    dataframe with new angle column.

    '''

    method_key = get_method_key('angle', call_num)
    columns = parameters[method_key]['column_names']
    output_name = parameters[method_key]['output_name']
    data[output_name] = np.arctan2(data[columns[0]]/data[data[columns[1]]])
    return data


def mean(data, f_index=None, parameters=None, call_num=None):
    ''' Mean of a columns values

    Notes
    -----

    Returns the mean of a particle's trajectory values to a new
    column. The value is repeated next to all entries for that trajectory

    :return: dataframe with new column defined in output_name of parameters

    '''

    method_key = get_method_key('mean', call_num)
    column = parameters[method_key]['column_name']
    output_name = parameters[method_key]['output_name']
    temp=data.groupby('particle')[column].transform('mean')
    data[output_name] = temp
    return data

def median(data, f_index=None, parameters=None, call_num=None):
    ''' Mean of a columns values

    Notes
    -----

    Returns the median of a particle's trajectory values to a new
    column. The value is repeated next to all entries for that trajectory

    :return: dataframe with new column defined in output_name of parameters

    '''

    method_key = get_method_key('median', call_num)
    column = parameters[method_key]['column_name']
    output_name = parameters[method_key]['output_name']
    temp=data.groupby('particle')[column].transform('median')
    data[output_name] = temp
    return data

def max(data, f_index=None, parameters=None, call_num=None):
    ''' Max of a columns values

    Notes
    -----

    Returns the max of a particle's trajectory values to a new
    column. The value is repeated next to all entries for that trajectory

    :return: dataframe with new column defined in output_name of parameters

    '''

    method_key = get_method_key('max', call_num)
    column = parameters[method_key]['column_name']
    output_name = parameters[method_key]['output_name']
    temp=data.groupby('particle')[column].transform('max')
    data[output_name] = temp
    return data

def _classify_fn(x, threshold_value=None):
    ''' classify

        Notes
        -----

        Returns the median of a particle's trajectory values to a new
        column. The value is repeated next to all entries for that trajectory

        :return: dataframe with new column defined in output_name of parameters

        '''

    if x < threshold_value:
        return 1
    else:
        return 2

def classify(data, f_index=None, parameters=None, call_num=None):
    method_key = get_method_key('classify', call_num)
    column = parameters[method_key]['column_name']
    output_name=parameters[method_key]['output_name']
    threshold_value = get_param_val(parameters[method_key]['value'])
    data[output_name] = data[column].apply(_classify_fn, threshold_value=threshold_value)
    return data


def subtract_drift(data, f_index=None, parameters=None, call_num=None):
    ''' subtract drift from an x,y coordinate trajectory

    Notes
    -----

    Returns the median of a particle's trajectory values to a new
    column. The value is repeated next to all entries for that trajectory

    Returns
    -------

    dataframe with new columns defined in output_name of parameters

    '''


    method_key = get_method_key('subtract_drift', call_num)
    drift = tp.motion.compute_drift(data)
    drift_corrected = tp.motion.subtract_drift(data.copy(), drift)
    drift_corrected.index.name = 'index'
    drift_corrected=drift_corrected.sort_values(['particle','index'])
    data[['x_drift','y_drift']] = drift_corrected[['x','y']]
    return data


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

    #https: // docs.scipy.org / doc / scipy / reference / generated / scipy.spatial.Delaunay.html
    method_key = get_method_key('neighbours', call_num)
    method = parameters[method_key]['method']
    df['neighbours'] = np.NaN
    for f in _every_frame(df, f_index):
        df = df.loc[f]
        if method == 'delaunay':
            df =_find_delaunay(df, parameters=parameters)
        elif method == 'kdtree':
            df =_find_kdtree(df, parameters=parameters)
        df.loc[f] = df
    return df

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
    # neighbour_ids = [particle_ids[point_indices[a:b].tolist()] for a, b in zip(list_indices[:-1], list_indices[1:])]
    neighbour_ids = [point_indices[a:b].tolist() for a, b in zip(list_indices[:-1], list_indices[1:])]
    dist = sp.distance.squareform(sp.distance.pdist(points))

    neighbour_dists = [(dist[i, row]<cutoff).tolist() for i, row in enumerate(neighbour_ids)]
    indices = []
    for index, row in enumerate(neighbour_ids):
        indices.append([particle_ids[neighbour_ids[index][j]] for j,dummy in enumerate(row) if neighbour_dists[index][j]])
    df.loc[:, ['neighbours']] = indices
    return df


