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
                    #Default trackpy linking method
                    print('tail', self.track_store._df.tail())
                    df = default(self.track_store, self.parameters['link']['default'])
                    store.write_data(df)
                    print('default')
                else:
                    #no linking
                    store.write_data(no_linking(self.track_store.get_data(f_index=f_index)))
                    
 

