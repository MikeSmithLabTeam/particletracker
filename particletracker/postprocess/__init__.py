from tqdm import tqdm
import os
import pandas as pd

from ..general.parameters import get_method_name
from ..general.dataframes import DataWrite
from ..postprocess import postprocessing_methods as pm


class PostProcessor:
    def __init__(self, parameters=None, data=None):
        self.link_store = data.link_store
        self.parameters = parameters      

    def process(self, f_index=None, lock_part=-1):
        if f_index is None:
            # processing whole thing
            output_filename = self.link_store.temp_filename[:-10] + '_postprocess.hdf5'
            start, stop, step = self.parameters['config']['_frame_range']
            if stop is None:
                stop = self.link_store.get_data().index.max() + 1
            
            full=True
            self.link_store.reload()
        else:
            #process single frame
            output_filename = self.link_store.temp_filename
            start = f_index
            stop = f_index + 1
            step = 1
            
            #If linking is locked read the full dataframe _link.hdf5 otherwise use _temp.hdf5
            full=lock_part==1
            # When lock_part is changed the full dataframe associated with the link data is reloaded.
                    

        """Some postprocessing methods need whole dataframe and some just need one frame. The implementation of caching
        in dataframes.DataRead complicates this. The decorator @param_parse reduces params dictionary and dataframe to the appropriate bit. The decorator @df_single or @df_multiple chop down the dataframes passed to the methods."""
        
        with DataWrite(output_filename) as store:
            if not self.parameters['postprocess']['postprocess_method'] and f_index is None:
                #If there is no postprocessing copy link data to postprocessing.
                store.write_data(self.link_store.get_data(full=True))
            else:               
                for f in tqdm(range(start, stop, step), 'Postprocessing'):
                    for method in self.parameters['postprocess']['postprocess_method']:
                        method_name, call_num = get_method_name(method)
                        store.write_data(getattr(pm, method_name)(self.link_store, f_index=f, full=full, parameters=self.parameters, call_num=call_num, section='postprocess'), f_index=f)


