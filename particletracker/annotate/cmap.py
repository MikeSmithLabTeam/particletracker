import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np

from ..general.parameters import get_param_val
from ..customexceptions.annotator_error import CmapError

def colour_array(subset_df, f, parameters, method=None):
    try:
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
            try:
                cmap_name = get_param_val(parameters[method]['cmap_name'])
                assert cmap_name in plt.colormaps(), "Colormap isn't available, setting to jet"
            except Exception as e:
                cmap_name = 'jet'
                # print('reached this point')
                # raise CmapError(e)
                print("Cmap set to jet")
            
            norm = colors.Normalize(vmin=cmap_min, vmax=cmap_max, clip=True)
            colour_obj = plt.get_cmap(cmap_name, np.size(colour_data))
            colour_vals = 255 * colour_obj(norm(colour_data))
            colours = []
            for colour in colour_vals:
                colours.append((colour[0,2], colour[0,1], colour[0,0]))
            colours = np.array(colours)
    
        return colours
    except Exception as e:
        raise CmapError(e)

