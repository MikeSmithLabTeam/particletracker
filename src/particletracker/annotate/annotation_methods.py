import cv2
import numpy as np
import warnings

import pandas as pd

from ..general.parameters import get_param_val, get_method_key, param_parse
from .cmap import colour_array, place_colourbar_in_image
from ..customexceptions import *
from ..general.dataframes import df_single, df_range
from ..general.contour_parsing import reconstruct_box_pts, reconstruct_contour_pts

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

    df_empty = pd.isna(particle_values[0])
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
    box_pts = tuple(reconstruct_contour_pts(subset_df[['box_pts']].values))
    
    if not box_pts:
        #0 boxes
        return frame

    (colours, colourbar) = colour_array(subset_df, f_index, parameters)

    #for index, box in enumerate(box_pts):
    #    frame = _draw_contours(frame, box, col=colours[index],
    #                            thickness=int(parameters['thickness']))
    frame = _draw_contours(frame, box_pts, col=colours, thickness=int(parameters['thickness']))
        
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
    
    subset_df = _get_class_subset(df_single, parameters).copy()

    if get_param_val(parameters['rad_from_data']):
        circles = subset_df[[x_col_name, y_col_name, r_col_name]].values
    else:
        subset_df['user_rad'] = parameters['user_rad']
        circles = subset_df[[x_col_name, y_col_name, 'user_rad']].values

    thickness = parameters['thickness']

    #No objects found
    if len(circles) == 0 or circles is None or pd.isna(circles).all():
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
    contour_pts = tuple(reconstruct_contour_pts(subset_df[['contours']].values))
    (colours, colourbar) = colour_array(subset_df, f_index, parameters)

    if not contour_pts:
        return frame

    frame = _draw_contours(frame, contour_pts, col=colours, thickness=int(thickness))
    
    if colourbar is not None:
        frame = place_colourbar_in_image(frame, colourbar, parameters) 
    return frame

@error_handling
def _draw_contours(img, contours, col=(0,0,255), thickness=1):
    if (np.size(np.shape(col)) == 0):
        img = cv2.drawContours(img, contours, -1, col, thickness)
    else:
        for i, contour in enumerate(contours):
            img = cv2.drawContours(img, [contour], -1, col[i], int(thickness))
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
@df_single
def voronoi(df_single,frame, f_index=None, parameters=None, *args, **kwargs):
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

    subset_df = _get_class_subset(df_single, parameters)

    print(f"\nVoronoi subset df: {subset_df}")
    print(f"\nVoronoi subset df shape: {subset_df.shape}")
    
    # 1. Grab both columns simultaneously. This gives a 2D array of shape (M, 2)
    # where column 0 is the flat list and column 1 is the vertex count.
    voronoi_data = subset_df[['voronoi', 'voronoi_counts']].values
    (colours, colourbar) = colour_array(subset_df, f_index, parameters)
    print(f"Voroni type: {type(voronoi_data[:, 0])}")
    if len(voronoi_data) == 0:
        return frame

    if np.shape(voronoi_data)[0] == 1:
        # Check if the list column is empty/NaN (handles 0 contours scenario safely)
        df_empty = pd.isna(voronoi_data[0, 0]) or len(voronoi_data[0, 0]) == 0
        if np.all(df_empty):
            return frame

    # 2. Iterate through and reconstruct each particle's cell polygon on the fly
    for index, row in enumerate(voronoi_data):
        flat_list = row[0]
        v_count = row[1]
        
        # Skip if it's an infinite boundary cell (count was set to 0 or flat_list is empty)
        if v_count == 0 or len(flat_list) == 0:
            continue
            
        # Reconstruct the original 2D (V, 2) array and cast to int32 for OpenCV
        contour = np.array(flat_list, dtype=np.int32).reshape(v_count, 2)
        
        # 3. Pass the freshly reconstructed (V, 2) polygon array to the drawer
        frame = _draw_polygon(frame, contour, col=colours[index],
                                        thickness=int(thickness))
                                        
    if colourbar is not None:
        frame = place_colourbar_in_image(frame, colourbar, parameters) 
    return frame


def _draw_polygon(img, pts, col=(0,0,255), thickness=1, closed=True):
    # pts arrives here as a clean (V, 2) int32 NumPy array
    if pts is None or len(pts) == 0:
        return img
    
    # OpenCV drawing functions expect a list of 2D shapes, i.e., [pts]
    if thickness == -1:
        img = cv2.fillPoly(img, [pts], col)
    else:
        img = cv2.polylines(img, [pts], closed, col, thickness) 
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
    thickness = parameters['thickness']
    line_type = parameters['line_type']
    tip_length = 0.01*parameters['tip_length']
    vector_scale = 0.01*parameters['vector_scale']

    (colours, colourbar) = colour_array(df_single, f_index, parameters)
    
    for i, vector in enumerate(vectors):
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

    if colourbar is not None:
        frame = place_colourbar_in_image(frame, colourbar, parameters)     
    return frame



@error_with_hint(additional_message="HINT: To run tj_gb you must have run find_tj_gb_coords in the postprocessing section")
@param_parse
@df_single
def plot_tj_gb(df_single,frame, f_index=None, parameters=None, *args, **kwargs):
    tj_x, tj_y = get_entity_coords_for_plotting(df_single, 'TJ')
    gb1_x, gb1_y = get_entity_coords_for_plotting(df_single, 'GB1')
    gb2_x, gb2_y = get_entity_coords_for_plotting(df_single, 'GB2')
    gb3_x, gb3_y = get_entity_coords_for_plotting(df_single, 'GB3')
    
    # Helper function to draw polylines from coordinate arrays
    def draw_gb_lines(x_arr, y_arr, color, thickness):
        if len(x_arr) > 0 and len(y_arr) > 0:
            # Reshape coordinates into an (N, 1, 2) integer array required by cv2.polylines
            pts = np.stack((x_arr, y_arr), axis=-1).astype(np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=False, color=color, thickness=thickness)

    # 3. Draw grain boundaries (BGR color format: Yellow, Cyan, Magenta)
    draw_gb_lines(gb1_x, gb1_y, color=parameters['gb1_colour'], thickness=parameters['gb_thickness'])     
    draw_gb_lines(gb2_x, gb2_y, color=parameters['gb2_colour'], thickness=parameters['gb_thickness'])    
    draw_gb_lines(gb3_x, gb3_y, color=parameters['gb3_colour'], thickness=parameters['gb_thickness'])     

    # 4. Draw the triple junction circle (Red in BGR: (0, 0, 255))
    if tj_x is not None and tj_y is not None:
        cv2.circle(
            frame, 
            center=(int(tj_x), int(tj_y)), 
            radius=parameters['tj_radius'], 
            color=parameters['tj_colour'], 
            thickness=parameters['tj_thickness']
        )

    return frame

def get_entity_coords_for_plotting(frame_df: pd.DataFrame, entity_type: str):
    """
    Extracts coordinates for a specific entity instance (by frame, type, and ID)
    formatted for plotting.
    
    Returns:
        - For line/path entities (e.g., grain_boundary): A tuple of (x_array, y_array)
        - For point entities (e.g., triple_junction): A tuple of scalar floats (x, y)
    """
    row = frame_df[(frame_df['entity_type'] == entity_type)]
    
    coords = row['coords'].iloc[0]
    arr = np.array(coords)

    if entity_type == 'triple_junction':
        # Return a single (x, y) point for plt.scatter or plt.plot
        return float(arr[0]), float(arr[1])
    else:
        # Return (x_array, y_array) for a path/line
        return arr[:, 0], arr[:, 1]
    







"""Extract and combine the largest filled objects from an RGB image."""





def main() -> None:
  image_path = "C:/Users/ppzmis/OneDrive - The University of Nottingham/Documents/Papers/Joe/triple_junction/up_1_frame0_1.png"
  image = cv2.imread(image_path, cv2.IMREAD_COLOR)

  h, w = image.shape[:2]
  center = (w // 2, h // 2)
  radius = w // 3

  mask = np.ones((h, w), dtype=np.uint8)
  #mask = cv2.circle(circular_mask, center, radius, 255, thickness=-1)

  red_ref = np.array([0, 0, 128])
  green_ref = np.array([124, 255, 124])
  blue_ref = np.array([128, 0, 0])

  tolerance = 10

  
  final = make_mask(image, red_bounds, green_bounds, blue_bounds, mask)

  cl_rg, cl_gb, cl_br = extract_centerlines_via_skeleton(final)
  triple_junction = find_triple_junction(cl_rg, cl_gb, cl_br)

  plt.figure()
  plt.imshow(image)

  for cl, name, col in [
      (cl_rg, "Centerline 1", "purple"),
      (cl_gb, "Centerline 2", "orange"),
      (cl_br, "Centerline 3", "cyan"),
  ]:
    if cl:
      cx = [p[0] for p in cl]
      cy = [p[1] for p in cl]
      plt.plot(cx, cy, color=col, linewidth=2, label=name)

  if triple_junction != (0.0, 0.0):
    plt.scatter(
        [triple_junction[0]],
        [triple_junction[1]],
        color="gold",
        s=150,
        marker="X",
        zorder=10,
        label="Triple Junction",
    )

  plt.legend(loc="upper right")
  plt.title("Centerlines and Triple Junction Superimposed on Original Image")
  plt.axis("off")
  plt.show()
