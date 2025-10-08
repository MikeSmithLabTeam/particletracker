from tqdm import tqdm
import os
import pandas as pd
import numpy as np

from ..general.parameters import get_method_name, get_span
from ..general.dataframes import DataWrite, combine_data_frames
from ..postprocess import postprocessing_methods as pm


class PostProcessor:
    def __init__(self, parameters=None, data=None):
        self.data=data
        self.link_store = data.link_store
        self.parameters = parameters      

    def process(self, f_index=None, lock_part=-1):
        """
        Data being processed can follow a number of scenarios
        1)There may be no postprocessing methods in which case whatever comes in _temp.hdf5 or _link.hdf5 should simply be copied to the output filename - _temp.hdf5 for single frames or _postprocess.hdf5 for full
        2) Single frame where there is only a single temporary file from the linking stage. Some postprocessing methods
        require a range of frames in order to process e.g running mean. The code should "gracefully" error indicating which method has caused the issue at bottom of screen. If there is no error _temp.hdf5 should be postprocessed and output to _temp.hdf5 with the additional data.
        3) Single frame where the data from the linking stage has been locked. It is only possible to lock if _link.hdf5 has been
        previously created through processing all the data. Decorator on the postprocessing functions determines whether a single frame or range of frame data is sent to postprocessing function. Single frame data output to _temp.hdf5.
        4) Processing the entire movie or range of frames with or without locking of linking stage. Data output to _postprocess.hdf5     
        """

        print('Postprocessing...')
        assert lock_part < 2, 'PTWorkflow.process logic should guarantee this but it broke'

        #Set output_filename
        if f_index is None:
            output_filename = self.link_store.output_filename
        else:
            output_filename = self.link_store.temp_filename
        
        #Choose whether to load full df or temp
        if f_index is None:
            df = self.link_store.df
        elif lock_part == 1 and self.parameters['postprocess']['postprocess_method']:
            full_df = self.link_store.df

            max_span = get_span(self.parameters['postprocess'])

            half_span = np.floor(max_span / 2)
            start = max(f_index - half_span, full_df.index.min())
            finish = min(f_index + half_span, full_df.index.max())

            #return a range
            df = full_df.loc[start:finish]
        else:
            self.link_store.clear_temp_df()
            df = self.link_store.temp_df
            print('straight from store', df)      

        """This block either copies across the data if no postprocessing methods (if block) or the line in the else block containing getattr(pm, method_name() says call the method in postprocessing_methods.py with the name method_name and pass the parameters to it. Take the return value and add it to the postprocessing store.
        See intro to postprocessing to understand how parameters and full dataframe are parsed by each function.
        """ 
        
        with DataWrite(output_filename) as store:
            if not self.parameters['postprocess']['postprocess_method']:
                #No methods selected copy data across
                store.write_data(df)
            else:
                for method in self.parameters['postprocess']['postprocess_method']:
                    method_name, call_num = get_method_name(method)
                    df = getattr(pm, method_name)(df,f_index=f_index, parameters=self.parameters, call_num=call_num, section='postprocess')    

                
                if f_index is not None:
                    print('Temp', f_index)
                    store.write_data(df.loc[f_index])
                else:
                    print('Full')
                    store.write_data(df)

        print('Postprocessing complete')

                                        
                    
                    
          
