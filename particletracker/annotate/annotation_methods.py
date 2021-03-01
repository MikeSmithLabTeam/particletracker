import cv2
import numpy as np

from ..general.parameters import get_param_val, get_method_key
from .cmap import colour_array
from ..customexceptions.annotator_error import *
from ..user_methods import *

'''
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
Text annotation
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
'''

def text_label(frame, data, f, parameters=None, call_num=None):
    '''
    Text labels place a static label on an image at specific location.
    This function is for adding titles or info that doesn't change

    Parameters  :

    text            :   Text to be displayed
    position        :   Coordinates of upper left corner of text
    font_colour     :   Colour of font specified in (B,G,R) format where values are integers from 0-255
    font_size       :   Size of font
    font_thickness  :   Thickness of font

    Inputs:

    frame       :   This is the unmodified frame of the input movie
    data        :   This is the dataframe that stores all the tracked data
    f           :   An integer that references the current frame number
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    annotated frame : Annotated frame of type numpy ndarray.
    '''

    try:
        method_key = get_method_key('text_label', call_num=call_num)
        text=parameters[method_key]['text']
        position = parameters[method_key]['position']
        annotated_frame=cv2.putText(frame, text, position, cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                    int(parameters[method_key]['font_size']),
                                    parameters[method_key]['font_colour'],
                                    int(parameters[method_key]['font_thickness']),
                                    cv2.LINE_AA)

        return annotated_frame
    except Exception as e:
        raise TextLabelError(e)

def var_label(frame, data, f, parameters=None, call_num=None):
    '''
    Var labelsn put text on an image at specific location.
    This function is for adding data specific to a single frame. For example
    you could indicate the temperature of the sample or time.
    The data for a given frame should be stored in a particular column
    specified in the 'var_column' section of the dictionary.
    
    Parameters  :

    var_column      :   Column name containing the info to be displayed on each frame
    position        :   Coordinates of upper left corner of text
    font_colour     :   Colour of font specified in (B,G,R) format where values are integers from 0-255
    font_size       :   Size of font
    font_thickness  :   Thickness of font

    Inputs:

    frame       :   This is the unmodified frame of the input movie
    data        :   This is the dataframe that stores all the tracked data
    f           :   An integer that references the current frame number
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    annotated frame : Annotated frame of type numpy ndarray.
    
    '''
    try:
        method_key = get_method_key('var_label', call_num=call_num)
        var_column=parameters[method_key]['var_column']
        text = str(data.get_info(f, var_column)[0])
        position = parameters[method_key]['position']

        annotated_frame=cv2.putText(frame, text, position, cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                    int(parameters[method_key]['font_size']),
                                    parameters[method_key]['font_colour'],
                                    int(parameters[method_key]['font_thickness']),
                                    cv2.LINE_AA)

        return annotated_frame
    except Exception as e:
        raise VarLabelError(e)

def particle_labels(frame, data, f, parameters=None, call_num=None):
    '''
    Annotates image with particle ids. For this to be meaningful
    you must have already run processed part with linking selected.
    This is particularly useful if you want to extract information about
    specific particles. Annotate their ids to identify the reference
    id of the one you are interested in and then you can pull the subset
    of processed data out. See examples in Jupyter notebook. Any particle
    level data can however be displayed.

    Parameters  :

    values_column   :   Name of column containing particle info to be displayed.
    position        :   Coordinates of upper left corner of text
    font_colour     :   Colour of font specified in (B,G,R) format where values are integers from 0-255
    font_size       :   Size of font
    font_thickness  :   Thickness of font


    Inputs:

    frame       :   This is the unmodified frame of the input movie
    data        :   This is the dataframe store that stores all the tracked data
    f           :   An integer that references the current frame number
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    annotated frame : Annotated frame of type numpy ndarray.
    '''

    try:

        method_key = get_method_key('particle_labels', call_num=None)
        x = data.get_info(f, 'x')
        y = data.get_info(f, 'y')
    
        particle_values = data.get_info(f, parameters[method_key]['values_column'])#.astype(int)
    
        for index, particle_val in enumerate(particle_values):
            frame = cv2.putText(frame, str(particle_val), (int(x[index]), int(y[index])),
                                cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                int(parameters[method_key]['font_size']),
                                parameters[method_key]['font_colour'],
                                int(parameters[method_key]['font_thickness']),
                                cv2.LINE_AA)

        return frame
    except Exception as e:
        raise ParticleLabelsError(e)

'''
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
Particle annotation
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
'''

def _get_class_subset(data, f, parameters, method=None):
    '''
    Internal function to get subset of particles
    '''    
    try:
        classifier_column= parameters[method]['classifier_column']
        
        if classifier_column is None:
            subset_df = data.df.loc[f]
        else:
            classifier = parameters[method]['classifier']
            temp = data.df.loc[f]
            subset_df = temp[temp[classifier_column] == classifier]
        return subset_df
    except Exception as e:
        raise GetClassSubsetError(e)


def circles(frame, data, f, parameters=None, call_num=None):
    '''
    Circles places a ring on every specified particle.

    Parameters  :

    radius          :   If tracking method specifies radius this is set automatically.
                        Otherwise this can be adjusted arbitrarily.
    cmap_type       :   Options are 1. static  2. dynamic
    cmap_column     :   Name of column containing data to specify colour in dynamic mode,#for dynamic
    cmap_max        :   Specifies max data value for colour map in dynamic mode
    cmap_scale      :   Scale factor for colour map
    colour          :   Colour to be used for static cmap_type (B,G,R) values from 0-255
    classifier_col  : None - selects all particles, column name of classifier values to apply to subset of particles
    classifier      :   The value in the classifier column to apply colour map to. 
    thickness       :   Thickness of circle. -1 fills the circle in solidly.


    Inputs:

    frame       :   This is the unmodified frame of the input movie
    data        :   This is the dataframe that stores all the tracked data
    f           :   An integer that references the current frame number
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    annotated frame : Annotated frame of type numpy ndarray.
    '''
    try:

        method_key = get_method_key('circles', call_num=call_num)
        if 'r' not in list(data.df.columns):
            data.add_particle_property('r', get_param_val(parameters[method_key]['radius']))
        thickness = get_param_val(parameters[method_key]['thickness'])

        subset_df = _get_class_subset(data, f, parameters, method=method_key)
        circles = subset_df[['x', 'y', 'r']].values
        colours = colour_array(subset_df, f, parameters, method=method_key)
        for i, circle in enumerate(circles):
            frame = cv2.circle(frame, (int(circle[0]), int(circle[1])), int(circle[2]), colours[i], int(thickness))
        return frame
    except Exception as e:
        raise CirclesError(e)

def boxes(frame, data, f, parameters=None, call_num=None):
    '''
    Boxes places a rectangle that encloses the contour of specified particle. This method is only
    valid if the tracking method results in a bounding box being stored in the dataframe. This is
    not the case for trackpy.

    Parameters  :

    cmap_type       :   Options are 1. static  2. dynamic
    cmap_column     :   Name of column containing data to specify colour in dynamic mode,#for dynamic
    cmap_max        :   Specifies max data value for colour map in dynamic mode
    cmap_scale      :   Scale factor for colour map
    colour          :   Colour to be used for static cmap_type (B,G,R) values from 0-255
    classifier_col  : None - selects all particles, column name of classifier values to apply to subset of particles
    classifier      :   The value in the classifier column to apply colour map to. 
    thickness       :   Thickness of box. -1 fills the box in

    Inputs:

    frame       :   This is the unmodified frame of the input movie
    data        :   This is the dataframe that stores all the tracked data
    f           :   An integer that references the current frame number
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs:
    
    annotated frame : Annotated frame of type numpy ndarray.
    '''

    try:
        method_key = get_method_key('boxes', call_num=call_num)
        thickness = get_param_val(parameters[method_key]['thickness'])
        subset_df = _get_class_subset(data, f, parameters, method=method_key)
        box_pts = subset_df[['box']].values

        colours = colour_array(subset_df, f, parameters, method=method_key)
        sz = np.shape(frame)
        for index, box in enumerate(box_pts):
            if _contour_inside_img(sz, box):
                frame = _draw_contours(frame, box, col=colours[index],
                                           thickness=int(get_param_val(parameters[method_key]['thickness'])))
        return frame
    except Exception as e:
        raise BoxesError(e)

def _contour_inside_img(sz, contour):
    inside=True
    frame_contour = np.array([[0,0],[0,sz[0]],[sz[1],sz[0]],[sz[1],0]])
    for pt in contour[0]:
        if cv2.pointPolygonTest(frame_contour, tuple(pt), False) < 0:
            inside = False
    return inside
    

def contours(frame, data, f, parameters=None, call_num=None):
    '''
    Contours draws the tracked contour returned from Contours tracking
    method onto the image.

    Parameters  :

    cmap_type       :   Options are 1. static  2. dynamic
    cmap_column     :   Name of column containing data to specify colour in dynamic mode,#for dynamic
    cmap_max        :   Specifies max data value for colour map in dynamic mode
    cmap_scale      :   Scale factor for colour map
    colour          :   Colour to be used for static cmap_type (B,G,R) values from 0-255
    classifier_col  : None - selects all particles, column name of classifier values to apply to subset of particles
    classifier      :   The value in the classifier column to apply colour map to. 
    thickness       :   Thickness of contour. -1 will fill in contour


    Inputs:

    frame       :   This is the unmodified frame of the input movie
    data        :   This is the dataframe that stores all the tracked data
    f           :   An integer that references the current frame number
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs
    
    annotated frame : Annotated frame of type numpy ndarray.
    '''
    try:
        method_key = get_method_key('contours', call_num=call_num)
        thickness = get_param_val(parameters[method_key]['thickness'])
        subset_df = _get_class_subset(data, f, parameters, method=method_key)
        contour_pts = subset_df[['contours']].values
        
        colours = colour_array(subset_df, f, parameters, method=method_key)

        for index, contour in enumerate(contour_pts):
           frame = _draw_contours(frame, contour, col=colours[index],
                                           thickness=int(thickness))
        return frame
    except Exception as e:
        raise ContoursError(e)

def _draw_contours(img, contours, col=(0,0,255), thickness=1):
    if (np.size(np.shape(col)) == 0) | (np.size(np.shape(col)) == 1):
        img = cv2.drawContours(img, contours, -1, col, thickness)
    else:
        for i, contour in enumerate(contours):
            img = cv2.drawContours(img, contour, -1, col[i], int(thickness))
    return img        


def networks(frame, data, f, parameters=None, call_num=None):
    '''
    Networks draws a network of particles that must previously have been 
    calculated in postprocessing. See "neighbours" in postprocessing.

    Parameters  :

    cmap_type       :   Options are 1. static  2. dynamic
    cmap_column     :   Name of column containing data to specify colour in dynamic mode,#for dynamic
    cmap_max        :   Specifies max data value for colour map in dynamic mode
    cmap_scale      :   Scale factor for colour map
    colour          :   Colour to be used for static cmap_type (B,G,R) values from 0-255
    classifier_col  : None - selects all particles, column name of classifier values to apply to subset of particles
    classifier      :   The value in the classifier column to apply colour map to. 
    thickness       :   Thickness of network lines


    Inputs:

    frame       :   This is the unmodified frame of the input movie
    data        :   This is the dataframe that stores all the tracked data
    f           :   An integer that references the current frame number
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs
    
    annotated frame : Annotated frame of type numpy ndarray.
    '''
    try:
        method_key = get_method_key('networks', call_num=call_num)
        df = _get_class_subset(data, f, parameters, method=method_key)
        df = df.set_index('particle')
        particle_ids = df.index.values
        colours = colour_array(df, f, parameters, method=method_key)
        thickness = get_param_val(parameters[method_key]['thickness'])

        for index, particle in enumerate(particle_ids):
            pt = df.loc[particle, ['x', 'y']].values
            pt1 = (int(pt[0]), int(pt[1]))
            neighbour_ids = df.loc[particle, 'neighbours']
            for index2, neighbour in enumerate(neighbour_ids):
                pt = df.loc[neighbour, ['x','y']].values
                pt2 = (int(pt[0]), int(pt[1]))
                frame = cv2.line(frame,pt1, pt2, colours[index], int(thickness), lineType=cv2.LINE_AA)
    except Exception as e:
        raise NetworksError(e)
'''
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
Particle motion annotation
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
'''
def vectors(frame, data, f, parameters=None, call_num=None):
    '''
    Vectors draw info onto images in the form of arrows. 

    Parameters  :

    x_column        :  Column name of x coordinates, defaults to 'x'
    y_column        :  Column name of y coordinates, defaults to 'y'
    traj_length'    :  How many frames into the past to draw the trajectory. This is truncated by ends
                       of the movie. If you are on frame 0 it won't draw anything!
    cmap_type       :   Options are 1. static  2. dynamic
    cmap_column     :   Name of column containing data to specify colour in dynamic mode,#for dynamic
    cmap_max        :   Specifies max data value for colour map in dynamic mode
    cmap_scale      :   Scale factor for colour map
    colour          :   Colour to be used for static cmap_type (B,G,R) values from 0-255
    classifier_col  :  None - selects all particles, column name of classifier values to apply to subset of particles
    classifier      :   The value in the classifier column to apply colour map to. 
    thickness       :   Thickness of line. 


    Inputs:

    frame       :   This is the unmodified frame of the input movie
    data        :   This is the dataframe that stores all the tracked data
    f           :   An integer that references the current frame number
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs
    
    annotated frame : Annotated frame of type numpy ndarray.
    '''

    try:
        method_key = get_method_key('vectors', call_num=call_num)
        dx = parameters[method_key]['dx_column']
        dy = parameters[method_key]['dy_column']

        vectors = data.get_info(f, ['x', 'y',dx, dy])

        thickness = get_param_val(parameters[method_key]['thickness'])
        line_type = get_param_val(parameters[method_key]['line_type'])
        tip_length = 0.01*get_param_val(parameters[method_key]['tip_length'])
        vector_scale = 0.01*get_param_val(parameters[method_key]['vector_scale'])

        colours = colour_array(data.df, f, parameters, method=method_key)

        for i, vector in enumerate(vectors):
            frame = cv2.arrowedLine(frame, (int(vector[0]), int(vector[1])),
                                    (int(vector[0]+vector[2]*vector_scale),int(vector[1]+vector[3]*vector_scale)),
                                    color=colours[i], thickness=int(thickness),line_type=line_type,shift=0,tipLength=tip_length)
        return frame
    except Exception as e:
        raise VectorsError(e)

def trajectories(frame, data, f, parameters=None, call_num=None):
    '''
    Vectors draw info onto images in the form of arrows. 

    Parameters  :

    dx_column       :   Column name that specifies the x component of vector,
    dy_column       :   Column name that specifies the y component of vector,
    line_type       :   OpenCV line type
    tip_length      :   Length of the vector arrow tip
    vector_scale    :   How to scale the data to the displayed vector length                
    cmap_type       :   Options are 1. static  2. dynamic
    cmap_column     :   Name of column containing data to specify colour in dynamic mode,#for dynamic
    cmap_max        :   Specifies max data value for colour map in dynamic mode
    cmap_scale      :   Scale factor for colour map
    colour          :   Colour to be used for static cmap_type (B,G,R) values from 0-255
    classifier_column': None - selects all particles, column name of classifier values to apply to subset of particles
    classifier      :   The value in the classifier column to apply colour map to. 
    thickness       :   Thickness of line. 


    Inputs:

    frame       :   This is the unmodified frame of the input movie
    data        :   This is the dataframe that stores all the tracked data
    f           :   An integer that references the current frame number
    parameters  :   Dictionary like object (same as .param files or 
                        output from general.param_file_creator.py
    call_num    :   Usually None but if multiple calls are made modifies
                    method name with get_method_key

    Outputs
    
    annotated frame : Annotated frame of type numpy ndarray.
    '''
    try:
        #This can only be run on a linked trajectory
        method_key = get_method_key('trajectories', call_num=call_num)
        x_col_name = parameters[method_key]['x_column']
        y_col_name = parameters[method_key]['y_column']

        #In this case subset_df is only used to get the particle_ids and colours of trajectories.
        subset_df = _get_class_subset(data, f, parameters, method=method_key)
        particle_ids = subset_df['particle'].values

        colours = colour_array(subset_df, f, parameters, method=method_key)
        thickness = get_param_val(parameters[method_key]['thickness'])
        traj_length = get_param_val(parameters[method_key]['traj_length'])

        if (f-traj_length) < 0:
            traj_length = f

        df = data.df.sort_index()
        df.index.name='frame'
        df['frame'] = df.index
        df2 = df.loc[f-traj_length:f]

        df3 = df2.set_index(['particle','frame']).sort_index(level='particle')

        for index, particle in enumerate(particle_ids):
            traj_pts = df3[[x_col_name,y_col_name]].loc[particle]
            traj_pts = np.array(traj_pts.values, np.int32).reshape((-1,1,2))
            frame = cv2.polylines(frame,[traj_pts],False,colours[index],int(thickness))
        return frame
    except Exception as e:
        raise TrajectoriesError(e)
