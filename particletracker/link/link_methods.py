import numpy as np
import pandas as pd
import trackpy

from ..general.parameters import  get_param_val
from ..customexceptions import *
from ..user_methods import *

def default(df, parameters, f_index=None):
    # Trackpy methods for default processing of entire movie / range
    df.reset_index(inplace=True)
    df = trackpy.link_df(df, get_param_val(parameters['max_frame_displacement']),
                            memory=get_param_val(parameters['memory']), 
                            link_strategy='auto', 
                            adaptive_step=0.75)
    df = trackpy.filter_stubs(df, get_param_val(parameters['min_frame_life']))
    return df


def no_linking(df, f_index=None):
    #No linking either for whole movie or because only processing single frame. 
    # Adds a particle id to dataframes for convenience
    # These are made up and no relation to the particle ids in the fully processed video.
    df_frame = df.loc[[f_index]]

    num_particles = np.shape(df)[0]
    pids = np.linspace(0,num_particles-1, num=num_particles).astype(int)
    df['particle'] = pids

    df.loc[[f_index]] = df_frame
    return df
