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
        print('Linking...')
        """Implements the trackpy functions link_df and filter_stubs"""
        _original = self.track_store.full

        assert lock_part < 1, 'PTWorkflow.process logic should guarantee this'
        # 3 cases:
        if f_index is None:
            # lock_part == -1 and f_index is None
            # Tracking processes whole movie. If f_index is None linking operates
            # on whole movie.
            output_filename = self.track_store.output_filename
            self.track_store.full = True
        else:
            #process single frame f_index
            output_filename = self.track_store.temp_filename   
            if lock_part == -1:
                #Tracking only operates on one frame producing _temp.hdf5, Linking reads from this temporary file
                self.track_store.full=False
            else:
                #If lock_part == 0 The tracking data on whole movie is stored in a file _track.hdf5 created previously. We only want to operate on one frame of this. You load full tracking data and then grab a single frame process it and store result in a temporary file.
                self.track_store.full=True

        df = self.track_store.get_df(f_index=f_index)

        if df is not None and df.isna().all().all():
            #If it is an empty dataframe copy to _link.hdf5 file
            df=df
        elif (f_index is None) and ('default' in self.parameters['link']['link_method']):#
            #Default trackpy linking method only used when processing whole movie.
            df = default(df, self.parameters['link']['default'])
        else:
            #no linking - this takes place when analysing temp single frames or as an option on the whole movie.
            df = no_linking(self.track_store.get_df(f_index=f_index))

        with DataWrite(output_filename) as store:
            store.write_data(df)
            

        #reset datastore state
        self.track_store.full = _original
        print('Linking Complete')
 

