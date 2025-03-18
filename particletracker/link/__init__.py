import numpy as np
import os
from tqdm import tqdm
import pandas as pd

from ..general.dataframes import DataWrite
from ..general.parameters import  get_param_val
from ..customexceptions import *
from ..user_methods import *
from .link_methods import default, no_linking

class LinkTrajectory:
    def __init__(self, data=None, parameters=None):
        self.track_store = data.track_store
        self.parameters=parameters

    @error_handling
    def link_trajectories(self, f_index=None, lock_part=-1):
        """Implements the trackpy functions link_df and filter_stubs"""
        if lock_part < 1:
            if f_index is None:
                # processing whole thing
                output_filename = self.track_store.temp_filename[:-10] + '_link.hdf5'
            else:
                #process single frame
                output_filename = self.track_store.temp_filename   
            
            with DataWrite(output_filename) as store:
                if (f_index is None) and ('default' in self.parameters['link']['link_method']):
                    #Default trackpy linking method only used when processing whole movie.
                    df = default(self.track_store.get_data(), self.parameters['link']['default'])
                else:
                    #no linking
                    if (f_index is not None) and (lock_part == -1):
                        #This reads the tracking from _temp.hdf5, created when the gui processes a single frame
                        full=False
                    else:
                        #f_index is None or lock_part == 0 and f_index is an integer value of the frame.
                        #If you process the whole movie or you read a single frame with the tracking stage locked, tracking 
                        #data is read from the _track.hdf5 file
                        full=True
                    df = self.track_store.get_data(f_index=f_index, full=full)
                store.write_data(df)
                    
 

