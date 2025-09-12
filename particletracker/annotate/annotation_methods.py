import cv2
import numpy as np
import warnings

import pandas as pd

from ..general.parameters import get_param_val, get_method_key, param_parse
from .cmap import colour_array, place_colourbar_in_image
from ..customexceptions import *
from ..user_methods import *
from ..general.dataframes import df_single, df_range

warnings.simplefilter('ignore')

"""
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
Text annotation
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
"""
@error_handling
@param_parse
def text_label(_, frame, f_index=None, parameters=None, *args, **kwargs):
    """
    Text labels place a static label on an image at specific location.

    
    Notes
    -----
    This function is for adding titles or info that doesn't change


    Parameters
    ----------
    text
        Text to be displayed
    position
        Coordinates of upper left corner of text
    font_colour
        Colour of font specified in (B,G,R) format where values are integers from 0-255
    font_size
        Size of font
    font_thickness
        Thickness of font


    
    Args
    ----
    frame
        This is the unmodified frame of the input movie
    data
        This is the dataframe that stores all the tracked data
    f_index
        frame index
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key


    Returns
    -----------
        annotated frame : np.ndarray
    

    """
    text=parameters['text']
    position = parameters['position']
    annotated_frame=cv2.putText(frame, text, position, cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                int(parameters['font_size']),
                                parameters['font_colour'],
                                int(parameters['font_thickness']),
                                cv2.LINE_AA)

    return annotated_frame

@error_handling
@param_parse
@df_single
def var_label(df_single, frame, f_index=None, parameters=None, *args, **kwargs):
    """
    Var labels puts text on an image at specific location for each frame. The value
    displayed in that frame is mapped to a column in the dataframe. The values next 
    to each frame should all be the same for that column. Use for example to 
    specify the temperature. 

    Notes
    -----
    This function is for adding data specific to a single frame. For example
    you could indicate the temperature of the sample or time.
    The data for a given frame should be stored in a particular column
    specified in the 'var_column' section of the dictionary.
    

    Parameters
    ----------

    var_column
        Column name containing the info to be displayed on each frame
    position
        Coordinates of upper left corner of text
    font_colour
        Colour of font specified in (B,G,R) format where values are integers from 0-255
    font_size
        Size of font
    font_thickness
        Thickness of font

    
    Args
    ----
    frame
        This is the unmodified frame of the input movie
    data
        This is the dataframe that stores all the tracked data
    f_index
        frame index
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key


    Returns
    -----------
        annotated frame : np.ndarray
    

    """
    var_column=parameters['var_column']
    if var_column == 'index':
        text = str(f_index)
    else:
        info = np.unique(df_single.loc[f_index, var_column])[0]
        text = str(info)
    position = parameters['position']        

    annotated_frame=cv2.putText(frame, text, position, cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                int(parameters['font_size']),
                                parameters['font_colour'],
                                int(parameters['font_thickness']),
                                cv2.LINE_AA)

    return annotated_frame

@error_handling
@param_parse
@df_single
def particle_labels(df_single, frame, f_index=None, parameters=None, *args, **kwargs):
    """
    Annotates image with particle info from one column. The most common use
    is to indicate the particle index but any column of data could be used.
    
    Notes
    -----    
    For particle ids to be meaningful, you must have already run 
    'processed part' with linking selected.
    This is particularly useful if you want to extract information about
    specific particles. Annotate their ids to identify the reference
    id of the one you are interested in and then you can pull the subset
    of processed data out. See examples in Jupyter notebook. Any particle
    level data can however be displayed.


    Parameters
    ----------
    values_column
        Name of column containing particle info to be displayed.
    position
        Coordinates of upper left corner of text
    font_colour
        Colour of font specified in (B,G,R) format where values are integers from 0-255
    font_size
        Size of font
    font_thickness
        Thickness of font


    Args
    ----
    frame
        This is the unmodified frame of the input movie
    data
        This is the dataframe that stores all the tracked data
    f
        frame index
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key


    Returns
    -----------
        annotated frame : np.ndarray

    """
    x = df_single['x'].values
    y = df_single['y'].values

    particle_values = df_single[parameters['values_column']].values

    df_empty = np.isnan(particle_values[0])
    if np.all(df_empty):
        return frame

    for index, particle_val in enumerate(particle_values):
        frame = cv2.putText(frame, str(particle_val), (int(float(x[index])), int(float(y[index]))),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL,
                            int(parameters['font_size']),
                            parameters['font_colour'],
                            int(parameters['font_thickness']),
                            cv2.LINE_AA)

    return frame

"""
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
Particle annotation
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
"""
@error_handling
def _get_class_subset(df_frame, parameters):
    """
    Internal function to get subset of particles
    """    
      
    classifier_column= parameters['classifier_column']
    if classifier_column is None:
        subset_df = df_frame
    else:
        classifier = parameters['classifier']
        temp = df_frame
        subset_df = temp[temp[classifier_column] == classifier]
    return subset_df

@error_with_hint(additional_message="HINT: Annotating boxes requires you to run contour_boxes in postprocessing. Did you forget?")
@param_parse
@df_single
def boxes(df_single, frame, f_index=None, parameters=None, *args, **kwargs):
    """
    Boxes places a rotated rectangle on the image that encloses the contours of specified particles.

    Notes
    -----
    This method requires you to have used contours for the tracking and run contour_boxes 
    in postprocessing. 

    Parameters
    ----------
    cmap_type
        Options are 'static' or 'dynamic'
    cmap_column
        Name of column containing data to specify colour in dynamic mode,
    cmap_max
        Specifies max data value for colour map in dynamic mode
    cmap_scale
        Scale factor for colour map
    colour
        Colour to be used for static cmap_type (B,G,R) values from 0-255
    classifier_column
        None selects all particles, column name of classifier values to specify subset of particles
    classifier
        The value in the classifier column which applies to subset (True or False)
    thickness
        Thickness of box. -1 fills the box in


    
    Args
    ----
    frame
        This is the unmodified frame of the input movie
    data
        This is the dataframe that stores all the tracked data
    f
        frame index
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key


    Returns
    -----------
        annotated frame : np.ndarray
    
    """
    subset_df = _get_class_subset(df_single, parameters)
    box_pts = subset_df[['box_pts']].values
    
    if np.shape(box_pts)[0] == 1:
        df_empty = np.isnan(box_pts[0])
        if np.all(df_empty):
            #0 boxes
            return frame

    (colours, colourbar) = colour_array(subset_df, f_index, parameters)

    for index, box in enumerate(box_pts):
        frame = _draw_contours(frame, box, col=colours[index],
                                thickness=int(parameters['thickness']))
        
    if colourbar is not None:
        frame = place_colourbar_in_image(frame, colourbar, parameters) 
    return frame


def _contour_inside_img(sz, contour):
    inside=True
    frame_contour = np.array([[0,0],[0,sz[0]],[sz[1],sz[0]],[sz[1],0]])
    for pt in contour[0]:
        if cv2.pointPolygonTest(frame_contour, tuple(pt), False) < 0:
            inside = False
    return inside
    
@error_handling
@param_parse
@df_single
def circles(df_single, frame, f_index=None, parameters=None, *args, **kwargs):
    """
    Circles places a ring on every specified particle
    
    
    Parameters
    ----------
    xdata_column
        Name of column to use for x coordinates
    ydata_column
        Name of column to use for y coordinates
    rad_from_data
        Specify radius manually: False or use measured rad: True. Only works
        for Hough transform.
    radius
        If rad_from_data = False this specifies the radius of circle
    cmap_type
        Options are static or dynamic
    cmap_column
        Name of column containing data to specify colour in dynamic mode,#for dynamic
    cmap_max
        Specifies max data value for colour map in dynamic mode
    cmap_scale
        Scale factor for colour map
    colour
        Colour to be used for static cmap_type (B,G,R) values from 0-255
    classifier_column
        None - selects all particles, column name of classifier values to apply to subset of particles
    classifier
        The value in the classifier column to apply colour map to (True or False) 
    thickness
        Thickness of circle. -1 fills the circle in solidly.


    Args
    ----
    frame : np.ndarray
        This is the unmodified frame of the input movie
    data : pandas dataframe
        This is the dataframe that stores all the tracked data
    f : int
        frame index
    parameters : dict
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num : int or None
        Usually None but if multiple calls are made modifies method name with get_method_key


    Returns
    -----------
        annotated frame : np.ndarray
    

    """
    x_col_name = parameters['xdata_column']
    y_col_name = parameters['ydata_column']
    r_col_name = parameters['rdata_column']
    
    subset_df = _get_class_subset(df_single, parameters)

    if get_param_val(parameters['rad_from_data']):
        circles = subset_df[[x_col_name, y_col_name, r_col_name]].values
    else:
        subset_df['user_rad'] = parameters['user_rad']
        circles = subset_df[[x_col_name, y_col_name, 'user_rad']].values

    thickness = parameters['thickness']

    #No objects found
    df_empty = np.isnan(circles[0])
    if np.all(df_empty):
        return frame
    
    (colours, colourbar) = colour_array(subset_df, f_index, parameters)
    
    if np.shape(circles) == (3,):#One object
        frame = cv2.circle(frame, (int(circles[0]), int(circles[1])), int(circles[2]), colours[0], int(thickness))
    else:
        for i, circle in enumerate(circles):
            frame = cv2.circle(frame, (int(circle[0]), int(circle[1])), int(circle[2]), colours[i], int(thickness))
    
    if colourbar is not None:
        frame = place_colourbar_in_image(frame, colourbar, parameters) 
    return frame

@error_handling
@param_parse
@df_single
def contours(df_single, frame, f_index=None, parameters=None, *args, **kwargs):
    """
    Contours draws the tracked contour returned from Contours tracking
    method onto the image.

    Notes
    -----
    Requires the contours tracking method.


    Parameters
    ----------
    cmap_type
        Options are static or dynamic
    cmap_column
        Name of column containing data to specify colour in dynamic mode
    cmap_max
        Specifies max data value for colour map in dynamic mode
    cmap_scale
        Scale factor for colour map
    colour_bar
        Add a colour bar. This only works with dynamic cmap. The values can be None or a tuple specifying (x,y,width,height).
    colour
        Colour to be used for static cmap_type (B,G,R) values from 0-255
    classifier_column
        None - selects all particles, column name of classifier values to apply to subset of particles
    classifier
        The value in the classifier column to apply colour map to (True or False). 
    thickness
        Thickness of contour. -1 will fill in contour


    Args
    ----
    frame
        This is the unmodified frame of the input movie
    data
        This is the dataframe that stores all the tracked data
    f
        frame index
    parameters
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num
        Usually None but if multiple calls are made modifies method name with get_method_key


    Returns
    -----------
        annotated frame : np.ndarray
    """    
    thickness = parameters['thickness']
    
    subset_df = _get_class_subset(df_single, parameters)
    contour_pts = subset_df[['contours']].values
    (colours, colourbar) = colour_array(subset_df, f_index, parameters)
    if np.shape(contour_pts)[0] == 1:
        df_empty = np.isnan(contour_pts[0])
        if np.all(df_empty):
            #0 contours
            return frame

    for index, contour in enumerate(contour_pts):
        frame = _draw_contours(frame, contour, col=colours[index],
                                        thickness=int(thickness))
    
    if colourbar is not None:
        frame = place_colourbar_in_image(frame, colourbar, parameters) 
    return frame

@error_handling
def _draw_contours(img, contours, col=(0,0,255), thickness=1):
    if (np.size(np.shape(col)) == 0) | (np.size(np.shape(col)) == 1):
        img = cv2.drawContours(img, contours, -1, col, thickness)
    else:
        for i, contour in enumerate(contours):
            img = cv2.drawContours(img, contour, -1, col[i], int(thickness))
    return img        

@error_with_hint(additional_message="HINT: To run networks you must have selected neighbours in postprocessing")
@param_parse
@df_single
def networks(df_single, frame, f_index=None, parameters=None, *args, **kwargs):
    """
    Networks draws a network of lines between particles

    
    Notes
    -----
    The network must previously have been calculated in postprocessing. 
    See "neighbours" in postprocessing.


    Parameters
    ----------
    cmap_type
        Options are static or dynamic
    cmap_column
        Name of column containing data to specify colour in dynamic mode,#for dynamic
    cmap_max
        Specifies max data value for colour map in dynamic mode
    cmap_scale
        Scale factor for colour map
    colour
        Colour to be used for static cmap_type (B,G,R) values from 0-255
    classifier_column
        None - selects all particles, column name of classifier values to apply to subset of particles
    classifier
        The value in the classifier column to apply colour map to. 
    thickness
        Thickness of network lines


    Args
    ----
    frame : np.ndarray
        This is the unmodified frame of the input movie
    data : pandas dataframe
        This is the dataframe that stores all the tracked data
    f : int
        frame index
    parameters : dict
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num : int or None
        Usually None but if multiple calls are made modifies method name with get_method_key


    Returns
    -----------
        annotated frame : np.ndarray
    
    """
    df = _get_class_subset(df_single, parameters)
    df=df.set_index('particle')
    particle_ids = df.index.values
    (colours, colourbar) = colour_array(df, f_index, parameters)
    thickness = parameters['thickness']

    for index, particle in enumerate(particle_ids):
        pt = df.loc[particle, ['x', 'y']].values
        pt1 = (int(pt[0]), int(pt[1]))
        neighbour_ids = df.loc[particle, 'neighbours']
        for neighbour in neighbour_ids:
            pt = df.loc[neighbour, ['x','y']].values
            pt2 = (int(pt[0]), int(pt[1]))
            frame = cv2.line(frame,pt1, pt2, colours[index], int(thickness), lineType=cv2.LINE_AA)
    if colourbar is not None:
        frame = place_colourbar_in_image(frame, colourbar, parameters) 
    return frame

@error_with_hint(additional_message="HINT: To run Voronoi Annotation you must have selected Voronoi in the postprocessing section")
@param_parse
def voronoi(data,frame, f_index=None, parameters=None, *args, **kwargs):
    """
    Voronoi draws the voronoi network that surrounds each particle

    
    Notes
    -----
    The voronoi cells must previously have been calculated in postprocessing. 
    See "voronoi" in postprocessing.


    Parameters
    ----------
    cmap_type
        Options are static or dynamic
    cmap_column
        Name of column containing data to specify colour in dynamic mode,#for dynamic
    cmap_max
        Specifies max data value for colour map in dynamic mode
    cmap_min
        Specifies min data value for colour map in dynamic mode
    cmap_scale
        Scale factor for colour map
    colour
        Colour to be used for static cmap_type (B,G,R) values from 0-255
    classifier_column
        None - selects all particles, column name of classifier values to apply to subset of particles
    classifier
        The value in the classifier column to apply colour map to. 
    thickness
        Thickness of network lines


    Args
    ----
    frame : np.ndarray
        This is the unmodified frame of the input movie
    data : pandas dataframe
        This is the dataframe that stores all the tracked data
    f : int
        frame index
    parameters : dict
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num : int or None
        Usually None but if multiple calls are made modifies method name with get_method_key


    Returns
    -----------
        annotated frame : np.ndarray
    
    """

    thickness = parameters['thickness']

    subset_df = _get_class_subset(data.get_data(f_index=f_index), parameters)
    contour_pts = subset_df[['voronoi']].values
    (colours, colourbar) = colour_array(subset_df, f_index, parameters)

    if np.shape(contour_pts)[0] == 1:
        df_empty = np.isnan(contour_pts[0])
        if np.all(df_empty):
            #0 contours
            return frame

    for index, contour in enumerate(contour_pts):
        frame = _draw_polygon(frame, contour, col=colours[index],
                                        thickness=int(thickness))
    if colourbar is not None:
        frame = place_colourbar_in_image(frame, colourbar, parameters) 
    return frame


def _draw_polygon(img, pts, col=(0,0,255), thickness=1, closed=True):
    if np.any(np.isnan(pts[0])):
        return img
    
    if thickness == -1:
        img = cv2.fillPoly(img, [pts[0].astype(np.int32)], col)
    else:
        img = cv2.polylines(img, [pts[0].astype(np.int32)], closed, col, thickness) 
    return img

"""
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
Particle motion annotation
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
"""
@error_handling
@param_parse
@df_single
def vectors(df_single, frame, f_index=None, parameters=None, *args, **kwargs):
    """
    Vectors draw info onto images in the form of arrows. 


    Notes
    -----
    Vectors draws an arrow starting at each particle with a length and direction
    specified by 2 components. The magnitude of the vector can be scaled to be appropriate.


    Parameters
    ----------
    dx_column
        Column name of x component of vector, defaults to 'x'
    dy_column
        Column name of y component of vector, defaults to 'y'
    vector_scale
        scaling between vector data and length of displayed line
    classifier_column
        None - selects all particles, column name of classifier values to apply to subset of particles
    classifier
        The value in the classifier column to apply colour map to. 
    cmap_type
        Options are static or dynamic
    cmap_column
        Name of column containing data to specify colour in dynamic mode,
    cmap_max
        Specifies max data value for colour map in dynamic mode
    cmap_min
        Specifies min data value for colour map in dynamic mode
    colour
        Colour to be used for static cmap_type (B,G,R) values from 0-255
    line_type
        OpenCV parameter can be -1, 4, 8, 16
    thickness
        Thickness of line. Defaults to 2
    tip_length
        Controls length of arrow head


    Args
    ----
    frame : np.ndarray
        This is the unmodified frame of the input movie
    data : pandas dataframe
        This is the dataframe that stores all the tracked data
    f : int
        frame index
    parameters : dict
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num : int or None
        Usually None but if multiple calls are made modifies method name with get_method_key


    Returns
    -----------
        annotated frame : np.ndarray
    
    """
    dx = parameters['dx_column']
    dy = parameters['dy_column']
    vectors = df_single[['x', 'y',dx, dy]].to_numpy()
    print(vectors)

    thickness = parameters['thickness']
    print('default line_type', parameters['line_type'])
    line_type = parameters['line_type']
    tip_length = 0.01*parameters['tip_length']
    vector_scale = 0.01*parameters['vector_scale']
    print('vector scale')

    (colours, colourbar) = colour_array(df_single, f_index, parameters)
    print('colours')
    
    for i, vector in enumerate(vectors):
        print(i, vector)
        frame = cv2.arrowedLine(frame, (int(vector[0]), int(vector[1])),
                                (int(vector[0]+vector[2]*vector_scale),int(vector[1]+vector[3]*vector_scale)),
                                color=colours[i], thickness=int(thickness),line_type=int(line_type),shift=0,tipLength=tip_length)
        
    if colourbar is not None:
        frame = place_colourbar_in_image(frame, colourbar, parameters) 
    return frame


"""
These methods require more than one frames data to be analysed so you'll need to run use part first.

"""
@error_with_hint(additional_message="HINT: To visualise annotate trajectories in the gui you must have already run a complete processing routine. This must have used linking. This is because this relies on data from other frames. You can of course process the movie and include trajectories.")
@param_parse
@df_range
def trajectories(df_range, frame, f_index=None, parameters=None, *args, **kwargs):
    """
    Trajectories draws the historical track of each particle onto an image. 

    Notes
    -----
    Requires data from other frames hence you must have previously processed
    the video.


    Parameters
    ----------
    x_column
        column name of x coordinates of particle,
    y_column
        column name of y coordinates of particle, 
    traj_length
        number of historical frames to include in each trajectory.               
    classifier_column
        None - selects all particles, column name of classifier values to apply to subset of particles
    classifier
        The value in the classifier column to apply colour map to (True or False). 
    cmap_type
        Options are static or dynamic
    cmap_column
        Name of column containing data to specify colour in dynamic mode,
    cmap_max
        Specifies max data value for colour map in dynamic mode
    cmap_min
        Specifies min data value for colour map in dynamic mode
    colour
        Colour to be used for static cmap_type (B,G,R) values from 0-255
    thickness
        Thickness of line. 
    
    Args
    ----
    frame : np.ndarray
        This is the unmodified frame of the input movie
    data : pandas dataframe
        This is the dataframe that stores all the tracked data
    f : int
        frame index
    parameters : dict
        Nested dictionary like object (same as .param files or output from general.param_file_creator.py)
    call_num : int or None
        Usually None but if multiple calls are made modifies
        method name with get_method_key

    Returns
    -----------
        annotated frame : np.ndarray
    
    """
    #This can only be run on a linked trajectory
    x_col_name = parameters['x_column']
    y_col_name = parameters['y_column']

    #In this case subset_df is only used to get the particle_ids and colours of trajectories.
    subset_df = _get_class_subset(df_range.loc[f_index], parameters)
    particle_ids = subset_df['particle'].values

    (colours, colourbar) = colour_array(subset_df, f_index, parameters)
    thickness = parameters['thickness']
    traj_length = parameters['span']

    if (f_index-traj_length) < 0:
        traj_length = f_index

    #tests showed mucking about with the index was faster than selecting on particle column
    df_range.index.name='frame'
    df2 = df_range.loc[f_index-traj_length:f_index]     
    df3 = df2.set_index(['particle'], append=True).swaplevel(i=0,j=1).sort_index(level='particle')

    for index, particle in enumerate(particle_ids):
        traj_pts = df3[[x_col_name,y_col_name]].loc[particle]
        traj_pts = np.array(traj_pts.values, np.int32).reshape((-1,1,2))
        frame = cv2.polylines(frame,[traj_pts],False,colours[index],int(thickness))

    print(colourbar)
    if colourbar is not None:
        frame = place_colourbar_in_image(frame, colourbar, parameters)     
    return frame
