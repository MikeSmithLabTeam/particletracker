import numpy as np
import os
from tqdm import tqdm
import pandas as pd

from ..general import dataframes
from ..general.parameters import  get_param_val
from ..customexceptions import *
from ..user_methods import *
from .link_methods import default, no_linking

class LinkTrajectory:
    def __init__(self, data_filename=None, parameters=None):
        path, filename = os.path.split(data_filename)
        self.data_filename = path + '/_temp/' + filename
        self.parameters=parameters

    @error_handling
    def link_trajectories(self, f_index=None, lock_part=-1):
        """Implements the trackpy functions link_df and filter_stubs"""
        if lock_part < 1:
            input_filename, output_filename = self.io_filenames(f_index, lock_part)

            with dataframes.DataStore(input_filename) as data:
                if (f_index is None) and ('default' in self.parameters['link']['link_method']):
                    #Default trackpy linking methods
                    df = default(data.df, self.parameters['link']['default'], f_index=None)
                else:
                    #No_linking
                    if f_index is None:
                        frame_range = self.parameters['config']['frame_range']
                        start=frame_range[0]
                        stop=frame_range[1]
                        if stop is None:
                            stop = data.df.index.max() + 1
                        step=frame_range[2]
                    #single frame
                    else:
                        start=f_index
                        stop=f_index+1
                        step=1

                    frames=[]
                    for f in tqdm(range(start, stop, step), 'Linking'):
                        frames.append(no_linking(data.get_frame(f), f_index=f))
                    
                    if frames:
                        df=pd.concat(frames)
                df.to_hdf(output_filename, 'data')
    
    def io_filenames(self,f_index, lock_part):
        if f_index is None:
            # Either clicking on link button or processing whole thing
            output_filename = self.data_filename[:-5] + '_link.hdf5'
            input_filename = self.data_filename[:-5] + '_track.hdf5'
        else:
            #process single frame
            output_filename = self.data_filename[:-5] + '_temp.hdf5'
            
            if lock_part == -1:
                #single frame when tracking not locked
                input_filename = self.data_filename[:-5] + '_temp.hdf5'
            else:
                #single frame when tracking is locked
                input_filename = self.data_filename[:-5] + '_track.hdf5'
        
        return input_filename, output_filename
        