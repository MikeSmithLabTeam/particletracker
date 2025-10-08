from tqdm import tqdm
import os
import pandas as pd

from ..general.parameters import get_method_name
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
        if f_index is None or lock_part == 1:
            df = self.link_store.df
        else:
            self.link_store.clear_temp_df()
            df = self.link_store.temp_df

        #Set start, stop and step
        if f_index is None:
            # processing whole thing
            start, stop, step = self.parameters['config']['_frame_range']
            df = self.link_store.df
            if df.empty:
                raise ValueError("No data found in link store")
            max_frame = df.index.max()
            if pd.isna(max_frame):
                raise ValueError("Invalid frame index found in data")
            stop = int(max_frame + 1)
        else:
            #process single frame
            start = f_index
            stop = f_index + 1
            step = 1        

        """This block either copies across the data if no postprocessing methods (if block) or the line in the else block containing getattr(pm, method_name() says call the method in postprocessing_methods.py with the name method_name and pass the parameters to it. Take the return value and add it to the postprocessing store.
        See intro to postprocessing to understand how parameters and full dataframe are parsed by each function.
        """ 
        
        with DataWrite(output_filename) as store:
            if not self.parameters['postprocess']['postprocess_method']:
                #No methods selected copy data across
                store.write_data(df)
            else:
                for f in tqdm(range(start, stop, step), 'Postprocessing'):
                    for method in self.parameters['postprocess']['postprocess_method']:
                        method_name, call_num = get_method_name(method)
                        print('df b4', df)
                        modified_df = getattr(pm, method_name)(df,f_index=f,parameters=self.parameters, call_num=call_num, section='postprocess')
                        print('init modified_df', modified_df)

                        if modified_df is not None:
                            df = combine_data_frames(df,modified_df)   
                        print('df', df)         

                    store.write_data(df.loc[f], f_index=f)

        print('Postprocessing complete')

                                        
                    
                    
          
