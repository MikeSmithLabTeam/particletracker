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

    #@error_handling
    def link_trajectories(self, f_index=None, lock_part=-1):
        """Implements the trackpy functions link_df and filter_stubs"""
        if lock_part < 1:
            if f_index is None:
                # processing whole thing
                output_filename = self.track_store.output_filename
                self.track_store.full = True
            else:
                #process single frame
                output_filename = self.track_store.temp_filename   
                if lock_part == -1:
                    #This reads the tracking from _temp.hdf5, created when the gui processes a single frame
                    self.track_store.full=False
                else:
                    #Processing whole movie or having lock_part==0
                    self.track_store.full=True

            df = self.track_store.get_data(f_index=f_index)

            if df is not None and df.isna().all().all():
                #If it is an empty dataframe copy to _link.hdf5 file
                df=df
            elif (f_index is None) and ('default' in self.parameters['link']['link_method']):#
                #Default trackpy linking method only used when processing whole movie.
                df = default(df, self.parameters['link']['default'])
            else:
                #no linking - this takes place when analysing temp single frames or as an option on the whole movie.
                df = no_linking(self.track_store.get_data(f_index=f_index))

            with DataWrite(output_filename) as store:
                store.write_data(df)
                    
 

