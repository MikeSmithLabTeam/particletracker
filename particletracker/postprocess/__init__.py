from tqdm import tqdm
import os
import pandas as pd

from ..general.parameters import get_method_name
from ..general.dataframes import DataStore
from ..postprocess import postprocessing_methods as pm


class PostProcessor:
    def __init__(self, parameters=None, data_filename=None):
        path, filename = os.path.split(data_filename)
        self.data_filename = path + '/_temp/' + filename
        self.parameters = parameters      

    def process(self, f_index=None, lock_part=-1):
        
        input_filename, output_filename = self.io_filenames(f_index, lock_part)
                
        with DataStore(input_filename) as data:
            #whole movie
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
            
            frames = []
            for f in tqdm(range(start, stop, step), 'Postprocessing'):
                for method in self.parameters['postprocess']['postprocess_method']:
                    method_name, call_num = get_method_name(method)
                    frames.append(getattr(pm, method_name)(data.get_frame(f), f_index=f,parameters=self.parameters, call_num=call_num, section='postprocess'))

            if frames:
                df = pd.concat(frames)
                df.to_hdf(output_filename, 'data')

    def io_filenames(self, f_index, lock_part):
        #If processing whole movie f_index is None else you are just processing one frame
        if f_index is None:
            # Either clicking on postprocess button or processing whole thing
            output_filename = self.data_filename[:-5] + '_postprocess.hdf5'
            input_filename = self.data_filename[:-5] + '_link.hdf5'
        else:
            #process single frame
            output_filename = self.data_filename[:-5] + '_temp.hdf5'
            if lock_part == 2:
                #single frame when linking is locked
                input_filename = self.data_filename[:-5] + '_link.hdf5'                
            else:
                #single frame when linking not locked
                input_filename = self.data_filename[:-5] + '_temp.hdf5'
        
        return input_filename, output_filename

