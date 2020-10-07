from ..general import dataframes
from ..general.parameters import  get_param_val
import trackpy
import numpy as np
import pandas as pd

class LinkTrajectory:
    def __init__(self, data_filename=None, parameters=None):
        self.data_filename=data_filename
        self.parameters=parameters

    def link_trajectories(self, f_index=None):
        try:
            """Implements the trackpy functions link_df and filter_stubs"""
            # Reload DataStore
            if f_index is None:
                'When processing whole video store in file with same name as movie'
                data_filename = self.data_filename
            else:
                'store temporarily'
                data_filename = self.data_filename[:-5] + '_temp.hdf5'

            with dataframes.DataStore(data_filename, load=True) as data:
                if f_index is None:
                    # Trackpy methods
                    data.reset_index()
                    data.df = trackpy.link_df(data.df, get_param_val(self.parameters['default']['max_frame_displacement']),memory=get_param_val(self.parameters['default']['memory']))
                    data.df = trackpy.filter_stubs(data.df, get_param_val(self.parameters['default']['min_frame_life']))
                else:
                    #Adds a particle id to single temporary dataframes for convenience
                    num_particles = np.shape(data.df)[0]
                    pids = np.linspace(0,num_particles-1, num=num_particles).astype(int)
                    data.df['particle'] = pids

                # Save DataStore
                data.save(filename=data_filename)
        except Exception as e:
            print('Error in linking')
            print(e)
