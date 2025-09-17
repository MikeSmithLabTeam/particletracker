import numpy as np
import pandas as pd
import trackpy

from ..general.parameters import  get_param_val
from ..customexceptions import *
from ..user_methods import *

@error_handling
def default(df_full, parameters):
    # Trackpy methods for default processing of entire movie / range
    df_full.reset_index(inplace=True)
    df_full = trackpy.link_df(df_full, get_param_val(parameters['max_frame_displacement']),
                            memory=get_param_val(parameters['memory']), 
                            link_strategy='auto', 
                            adaptive_step=0.75)
    df_full = trackpy.filter_stubs(df_full, get_param_val(parameters['min_frame_life']))
    if 'frame' in df_full.columns:
        df_full.drop('frame', axis=1, inplace=True)
    return df_full

@error_handling
def no_linking(df):
    #No linking either for whole movie or because only processing single frame. 
    # Adds a particle id to dataframes for convenience
    # These are made up and no relation to the particle ids in the fully processed video.

    num_particles = np.shape(df)[0]
    pids = np.linspace(0,num_particles-1, num=num_particles).astype(int)
    df['particle'] = pids
    return df
