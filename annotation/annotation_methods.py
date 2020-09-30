from ParticleTrackingGui.general.parameters import get_param_val, get_method_key
from ParticleTrackingGui.general.cmap import colour_array
import cv2
import numpy as np

'''
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
Text annotation
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
'''

def text_label(frame, data, f, parameters=None, call_num=None):
    '''
    Function puts text on an image at specific location.
    This function is for adding metadata or info not labelling
    particles with their ids.

    :param frame: frame to be annotated should be 3 colour channel
    :param data: datastore with particle information
    :param f: frame number
    :param parameters: annotation sub dictionary

    :return: annotated frame
    '''
    method_key = get_method_key('text_label', call_num=call_num)
    text=parameters[method_key]['text']
    position = parameters[method_key]['position']
    annotated_frame=cv2.putText(frame, text, position, cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                parameters[method_key]['font_size'],
                                parameters[method_key]['font_colour'],
                                parameters[method_key]['font_thickness'],
                                cv2.LINE_AA)

    return annotated_frame

def var_label(frame, data, f, parameters=None, call_num=None):
    '''
    Function puts text on an image at specific location.
    This function is for adding data specific to a single frame or info not labelling
    particles with their ids. The data for a given frame should be stored in 'var_column'
    ie all particles have this value stored. You could use it to put the "temperature" on
    a frame or the mean order parameter etc.

    :param frame: frame to be annotated should be 3 colour channel
    :param data: datastore with particle information
    :param f: frame number
    :param parameters: annotation sub dictionary.

    :return: annotated frame
    '''
    method_key = get_method_key('var_label', call_num=call_num)
    var_column=parameters[method_key]['var_column']
    text = str(data.get_info(f, var_column)[0])
    position = parameters[method_key]['position']

    annotated_frame=cv2.putText(frame, text, position, cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                parameters[method_key]['font_size'],
                                parameters[method_key]['font_colour'],
                                parameters[method_key]['font_thickness'],
                                cv2.LINE_AA)

    return annotated_frame

def particle_values(frame, data, f, parameters=None, call_num=None):
    '''
    Function annotates image with particle ids
    This function only makes sense if run on linked trajectories

    :param frame: frame to be annotated should be 3 colour channel
    :param data: datastore with particle information
    :param f: frame number
    :param parameters: annotation sub dictionary

    :return: annotated frame
    '''
    method_key = get_method_key('particle_values', call_num=None)
    x = data.get_info(f, 'x')
    y = data.get_info(f, 'y')

    particle_values = data.get_info(f, parameters[method_key]['values_column']).astype(int)

    for index, particle_val in enumerate(particle_values):
        frame = cv2.putText(frame, str(particle_val), (int(x[index]), int(y[index])),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL,
                            parameters[method_key]['font_size'],
                            parameters[method_key]['font_colour'],
                            parameters[method_key]['font_thickness'],
                            cv2.LINE_AA)

    return frame


'''
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
Particle annotation
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
'''
def get_class_subset(data, f, parameters, method=None):
    classifier_column= parameters[method]['classifier_column']
    if classifier_column is None:
        subset_df = data.df.loc[f]
    else:
        classifier = parameters[method]['classifier']
        temp = data.df.loc[f]
        subset_df = temp[temp[classifier_column] == classifier]
    return subset_df



def circles(frame, data, f, parameters=None, call_num=None):
    '''
    Function draws circles on an image at x,y locations. If data.df['r'] exists
    circles have this radius, else 'r' col is created with value set from annotation
    sub dictionary.

    :param frame: frame to be annotated should be 3 colour channel
    :param data: datastore with particle information
    :param f: frame number
    :param parameters: annotation sub dictionary

    :return: annotated frame
    '''
    method_key = get_method_key('circles', call_num=call_num)
    if 'r' not in list(data.df.columns):
        data.add_particle_property('r', get_param_val(parameters[method_key]['radius']))
    thickness = get_param_val(parameters[method_key]['thickness'])

    subset_df = get_class_subset(data, f, parameters, method=method_key)
    circles = subset_df[['x', 'y', 'r']].values
    colours = colour_array(subset_df, f, parameters, method=method_key)
    for i, circle in enumerate(circles):
        try:
            frame = cv2.circle(frame, (int(circle[0]), int(circle[1])), int(circle[2]), colours[i], thickness)
        except:
            print('Failed plotting circle, check data is valid')
    return frame

def boxes(frame, data, f, parameters=None, call_num=None):
    method_key = get_method_key('boxes', call_num=call_num)
    thickness = get_param_val(parameters[method_key]['thickness'])
    subset_df = get_class_subset(data, f, parameters, method=method_key)
    box_pts = subset_df[['box']].values

    colours = colour_array(subset_df, f, parameters, method=method_key)
    sz = np.shape(frame)
    for index, box in enumerate(box_pts):
        if contour_inside_img(sz, box):
            frame = _draw_contours(frame, box, col=colours[index],
                                       thickness=get_param_val(parameters[method_key]['thickness']))
    return frame

def contour_inside_img(sz, contour):
    inside=True
    frame_contour = np.array([[0,0],[0,sz[0]],[sz[1],sz[0]],[sz[1],0]])
    for pt in contour[0]:
        if cv2.pointPolygonTest(frame_contour, tuple(pt), False) < 0:
            inside = False
    return inside



def contours(frame, data, f, parameters=None, call_num=None):
    method_key = get_method_key('contours', call_num=call_num)
    thickness = get_param_val(parameters[method_key]['thickness'])
    subset_df = get_class_subset(data, f, parameters, method=method_key)
    contour_pts = subset_df[['contours']].values
    colours = colour_array(subset_df, f, parameters, method=method_key)

    for index, contour in enumerate(contour_pts):
       frame = _draw_contours(frame, contour, col=colours[index],
                                       thickness=thickness)
    return frame

def _draw_contours(img, contours, col=(0,0,255), thickness=1):
    """

    :param img:
    :param contours:
    :param col: Can be a defined colour in colors.py or a list of tuples(3,1) of colors of length contours
    :param thickness: -1 fills the contour.
    :return:
    """
    if (np.size(np.shape(col)) == 0) | (np.size(np.shape(col)) == 1):
        img = cv2.drawContours(img, contours, -1, col, thickness)
    else:
        for i, contour in enumerate(contours):
            img = cv2.drawContours(img, contour, -1, col[i], thickness)
    return img


def networks(frame, data, f, parameters=None, call_num=None):
    method_key = get_method_key('networks', call_num=call_num)
    df = get_class_subset(data, f, parameters, method=method_key)
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
            frame = cv2.line(frame,pt1, pt2, colours[index], thickness, lineType=cv2.LINE_AA)
    return frame
'''
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
Particle motion annotation
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
'''
def vectors(frame, data, f, parameters=None, call_num=None):
    method_key = get_method_key('vectors', call_num=call_num)
    dx = parameters[method_key]['dx_column']
    dy = parameters[method_key]['dy_column']

    vectors = data.get_info(f, ['x', 'y',dx, dy])

    thickness = get_param_val(parameters[method_key]['thickness'])
    line_type = 8
    tipLength = 0.01*get_param_val(parameters[method_key]['tip_length'])
    vector_scale = 0.01*get_param_val(parameters[method_key]['vector_scale'])

    colours = colour_array(data.df, f, parameters, method=method_key)

    for i, vector in enumerate(vectors):
        frame = cv2.arrowedLine(frame, (int(vector[0]), int(vector[1])),
                                (int(vector[0]+vector[2]*vector_scale),int(vector[1]+vector[3]*vector_scale)),
                                color=colours[i], thickness=thickness,line_type=line_type,shift=0,tipLength=tipLength)
    return frame

def trajectories(frame, data, f, parameters=None, call_num=None):
    #This can only be run on a linked trajectory
    method_key = get_method_key('trajectories', call_num=call_num)
    x_col_name = parameters[method_key]['x_column']
    y_col_name = parameters[method_key]['y_column']

    #In this case subset_df is only used to get the particle_ids and colours of trajectories.
    subset_df = get_class_subset(data, f, parameters, method=method_key)
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
        frame = cv2.polylines(frame,[traj_pts],False,colours[index],thickness)
    return frame

def frame_range(frame, data, f, parameters=None, call_num=None):
    '''
    This method performs no operation. It is included because
    the dictionary cycles through every active method. If this
    method is active
    '''
    return frame

