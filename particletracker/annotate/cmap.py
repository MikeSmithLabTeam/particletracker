import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib as mpl
import numpy as np

from ..general.parameters import get_param_val
from ..customexceptions import *

@error_handling
def colour_array(subset_df, f, parameters):
    cmap_type = parameters['cmap_type']
    sz = np.shape(subset_df.index.values)
    if cmap_type == 'static':
        colour_val = parameters['colour']
        colours = colour_val*np.ones((sz[0],3))
        colourbar = None
    elif cmap_type == 'dynamic':
        cmap_column = parameters['cmap_column']
        colour_data = subset_df[[cmap_column]].values
        if np.iscomplexobj(colour_data):
            colour_data = np.angle(colour_data)
        cmap_max = parameters['cmap_max']
        cmap_min = parameters['cmap_min']
        try:
            cmap_name = parameters['cmap_name']
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
        
        if parameters['colour_bar'] is None:
            colourbar = None
        else:
            _,_,w,h= parameters['colour_bar']
            colourbar = create_colourbar(int(w),int(h), cmap_name, cmap_min, cmap_max)  
            print('finish')
                        
    return (colours, colourbar)
    
def create_colourbar(w,h, cmap, cmap_min, cmap_max):
    """
    Create a colorbar as a NumPy array with specified dimensions and colormap.

    Parameters:
    - w: Width of the white rectangle.
    - h: Height of the white rectangle.
    - cmap: Colormap to use.
    - cmap_min: Minimum value for the colormap.
    - cmap_max: Maximum value for the colormap.

    Returns:
    - colorbar_image: NumPy array representing the colorbar with white rectangle and black edge.
    """
    dpi=100
    figsize = (w/dpi, h/dpi)

    if h > w:
        orientation = 'vertical'
    else:
        orientation = 'horizontal'

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, layout='constrained')

    # Set the figure and axes background to be transparent
    fig.patch.set_facecolor('none')
    ax.patch.set_facecolor('none')

    norm = mpl.colors.Normalize(vmin=cmap_min, vmax=cmap_max)

    cbar=fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
             cax=ax, orientation=orientation)
    cbar.ax.tick_params(labelsize=14)

    # Remove padding and margins
    plt.subplots_adjust(left=0, right=0, top=0, bottom=0)

    # Convert the figure to a NumPy array
    fig.canvas.draw()
    colorbar_image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    colorbar_image = colorbar_image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    
    plt.close(fig)
    
    return colorbar_image

def place_colourbar_in_image(image, colourbar, parameters):
    """
    Place the colorbar into the image at the specified position (x, y).
    Crop the colorbar if it exceeds the image boundaries.

    Parameters:
    - image: Original image as a NumPy array.
    - colorbar: Colorbar as a NumPy array.
    - x: X-coordinate for the top-left corner of the colorbar.
    - y: Y-coordinate for the top-left corner of the colorbar.

    Returns:
    - image: Image with the colorbar placed at the specified position.
    """
    x,y,_,_=parameters['colour_bar']

    x=int(x)
    y=int(y)
    
    img_height, img_width, _ = image.shape
    cb_height, cb_width, _ = colourbar.shape

    # Calculate the maximum allowable width and height for the colorbar
    max_width = min(cb_width, img_width - x)
    max_height = min(cb_height, img_height - y)
    # Crop the colorbar if it exceeds the image boundaries
    print(2)
    cropped_colourbar = colourbar[:max_height, :max_width,:].copy()
    
    
    cropped_colourbar[0,:,:] = 0
    cropped_colourbar[-1,:,:] = 0
    cropped_colourbar[:,0,:] = 0
    cropped_colourbar[:,-1,:] = 0
    print(4)
    # Place the blended region back into the image
    image[y:y+max_height, x:x+max_width] = cropped_colourbar
    return image