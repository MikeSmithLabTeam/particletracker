import cv2
import numpy as np
import warnings

from ..general.parameters import get_param_val, get_method_key
from .cmap import colour_array
from ..customexceptions.annotator_error import *
from ..user_methods import *

warnings.simplefilter('ignore')
"""
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
Text annotation
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
"""

def text_label(frame, data, f, parameters=None, call_num=None):
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

    try:
        method_key = get_method_key('var_label', call_num=call_num)
        var_column=parameters[method_key]['var_column']
        if var_column == 'index':
            text = str(f)
        else:
            print('test')
            info = np.unique(data.df.loc[f, var_column])[0]
            text = str(info)
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
    try:
        method_key = get_method_key('particle_labels', call_num=None)
        x = data.get_info(f, 'x')
        y = data.get_info(f, 'y')

    
        particle_values = data.get_info(f, parameters[method_key]['values_column'])#.astype(int)     

        df_empty = np.isnan(particle_values[0])
        if np.all(df_empty):
            return frame

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

"""
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
Particle annotation
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
"""

def _get_class_subset(data, f, parameters, method=None):
    """
    Internal function to get subset of particles
    """    
    try:
        
        classifier_column= parameters[method]['classifier_column']
        if classifier_column is None:
            subset_df = data.df.loc[f]
        else:
            classifier = get_param_val(parameters[method]['classifier'])
            temp = data.df.loc[f]
            subset_df = temp[temp[classifier_column] == classifier]
        return subset_df
    except Exception as e:
        raise GetClassSubsetError(e)


def boxes(frame, data, f, parameters=None, call_num=None):
    """
    Boxes places a rotated rectangle on the image that encloses the contours of specified particles.


    Notes
    -----
    This method requires you to have used contours for the tracking and run boxes 
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

    try:
        method_key = get_method_key('boxes', call_num=call_num)
        thickness = get_param_val(parameters[method_key]['thickness'])
        subset_df = _get_class_subset(data, f, parameters, method=method_key)
        box_pts = subset_df[['box_pts']].values
       
        if np.shape(box_pts)[0] == 1:
            df_empty = np.isnan(box_pts[0])
            if np.all(df_empty):
                #0 boxes
                return frame

        colours = colour_array(subset_df, f, parameters, method=method_key)
        sz = np.shape(frame)

        for index, box in enumerate(box_pts):
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
    

def circles(frame, data, f, parameters=None, call_num=None):
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
    
    try:
        method_key = get_method_key('circles', call_num=call_num)
        x_col_name = parameters[method_key]['xdata_column']
        y_col_name = parameters[method_key]['ydata_column']
        r_col_name = parameters[method_key]['rdata_column']
        
        if get_param_val(parameters[method_key]['rad_from_data']):
            subset_df = _get_class_subset(data, f, parameters, method=method_key)
            circles = subset_df[[x_col_name, y_col_name, r_col_name]].values
            
        else:
            data.add_particle_property('user_rad', get_param_val(parameters[method_key]['user_rad']))
            subset_df = _get_class_subset(data, f, parameters, method=method_key)
            circles = subset_df[[x_col_name, y_col_name, 'user_rad']].values
    
        thickness = get_param_val(parameters[method_key]['thickness'])

        #No objects found
        df_empty = np.isnan(circles[0])
        if np.all(df_empty):
            return frame
        
        colours = colour_array(subset_df, f, parameters, method=method_key)
        
        if np.shape(circles) == (3,):#One object
            frame = cv2.circle(frame, (int(circles[0]), int(circles[1])), int(circles[2]), colours[0], int(thickness))
        else:
            for i, circle in enumerate(circles):
                frame = cv2.circle(frame, (int(circle[0]), int(circle[1])), int(circle[2]), colours[i], int(thickness))
    
        return frame
    
    except Exception as e:
        raise CirclesError(e)



def contours(frame, data, f, parameters=None, call_num=None):
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

    try: 
        method_key = get_method_key('contours', call_num=call_num)
        thickness = get_param_val(parameters[method_key]['thickness'])
        
        subset_df = _get_class_subset(data, f, parameters, method=method_key)
        contour_pts = subset_df[['contours']].values
        colours = colour_array(subset_df, f, parameters, method=method_key)

        if np.shape(contour_pts)[0] == 1:
            df_empty = np.isnan(contour_pts[0])
            if np.all(df_empty):
                #0 contours
                return frame

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
        return frame
    except Exception as e:
        raise NetworksError(e)


def voronoi(frame, data, f, parameters=None, call_num=None):
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
    
    try:
        method_key = get_method_key('voronoi', call_num=call_num)
        thickness = get_param_val(parameters[method_key]['thickness'])

        subset_df = _get_class_subset(data, f, parameters, method=method_key)
        contour_pts = subset_df[['voronoi']].values
        colours = colour_array(subset_df, f, parameters, method=method_key)

        if np.shape(contour_pts)[0] == 1:
            df_empty = np.isnan(contour_pts[0])
            if np.all(df_empty):
                #0 contours
                return frame

        for index, contour in enumerate(contour_pts):
            frame = _draw_polygon(frame, contour, col=colours[index],
                                          thickness=int(thickness))
        return frame
    except Exception as e:
        raise VoronoiError(e)

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
def vectors(frame, data, f, parameters=None, call_num=None):
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



"""
These methods require more than one frames data to be analysed so you'll need to run use part first.

"""
def trajectories(frame, data, f, parameters=None, call_num=None):
    """
    Trajectories draws the historical track of each particle onto an image. 

    Notes
    -----
    Requires data from other frames hence you must have previously processed
    the video and then toggled use_part_processed button.


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
    import time
    
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

        #tests showed mucking about with the index was faster than selecting on particle column
        df = data.df
        df.index.name='frame'
        df2 = df.loc[f-traj_length:f]     
        df3 = df2.set_index(['particle'], append=True).swaplevel(i=0,j=1).sort_index(level='particle')
        for index, particle in enumerate(particle_ids):
            traj_pts = df3[[x_col_name,y_col_name]].loc[particle]
            traj_pts = np.array(traj_pts.values, np.int32).reshape((-1,1,2))
            frame = cv2.polylines(frame,[traj_pts],False,colours[index],int(thickness))
        
        return frame
    except Exception as e:
        raise TrajectoriesError(e)
