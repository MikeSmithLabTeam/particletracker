import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np

from ..general.parameters import get_param_val
from ..customexceptions.annotator_error import CmapError

def colour_array(subset_df, f, parameters, method=None):
    if True:
        cmap_type = get_param_val(parameters[method]['cmap_type'])
        sz = np.shape(subset_df.index.values)
        if cmap_type == 'static':
            colour_val = parameters[method]['colour']
            colours = colour_val*np.ones((sz[0],3))
        elif cmap_type == 'dynamic':
            cmap_column = parameters[method]['cmap_column']
            colour_data = subset_df[[cmap_column]].values
            cmap_max = get_param_val(parameters[method]['cmap_max'])
            cmap_min = get_param_val(parameters[method]['cmap_min'])           
            cmap_name = 'jet'
            
            norm = colors.Normalize(vmin=cmap_min, vmax=cmap_max, clip=True)
            
            colour_obj = plt.get_cmap(cmap_name, np.size(colour_data))
            colour_vals = 255 * colour_obj(norm(colour_data))
            colours = []
            for colour in colour_vals:
                colours.append((colour[0,2], colour[0,1], colour[0,0]))
            colours = np.array(colours)
    try:
        return colours
    except Exception as e:
        raise CmapError(e)

"""
def cmap_variables(data, f, parameters, method=None):
    '''
    Convenience method to extract the inputs necessary for building a colourmap

    :param data: DataStore
    :param f: frame number
    :param parameters: annotation parameters dictionary
    :param method: String of the method being used to annotate

    :return: Numpy array of data to be used in colour coding, type of colour map, maximum value to scale data.
    '''
    print('var')
    try:
        cmap_column = parameters[method]['cmap_column']
        if cmap_column is None:
            sz = np.shape(data.df.loc[f].index.values)
            colour_data = np.ones(sz)
            cmap_type='static'
        else:
            colour_data = data.get_info(f, cmap_column)
            cmap_type = parameters[method]['cmap_type']
        cmax_max = get_param_val(parameters[method]['cmap_max'])/10
        return colour_data, cmap_type, cmax_max
    except Exception as e:
        raise CmapError(e)
"""
"""
def colourmap(colour_data, cmap_type=None, cmax_max=None):
    print('maop')
    '''
    cmap could have different use cases:
    1: 'static' data is colour coded according to some classifier
    2: 'dynamic' data is colour coded according to continuous scale

    Colormap definitions: https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html
    case 1 colourmap is Set1 of Matplotlibs Qualitative color maps
    case 2 colourmap is jet from diverging colormaps


    :param data: Datastore object containing column upon which to perform the mapping
    :param f: integer specifying frame number
    :param col_name: string specifying column in dataframe of Datastore which supplies values for colour coding
    :param parameters: Dictionary specifying parameters

    :return: a
    '''
    try:
        if cmap_type == 'static':
            cmap_name = 'Set1'
        elif cmap_type == 'dynamic':
            cmap_name='jet'
        else:
            cmap_name = cmap_type

        if cmax_max is None:
            cmax_max = np.max(colour_data)

        colour_obj = plt.get_cmap(cmap_name, np.size(colour_data))
        colour_vals = 255*colour_obj(colour_data/cmax_max)
        colours=[]
        for colour in colour_vals:
            colours.append((colour[0],colour[1],colour[2]))
        return np.array(colours)
    except Exception as e:
        raise CmapError(e)

"""

