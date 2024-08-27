from tqdm import tqdm

from ..general.parameters import get_method_name
from ..general.dataframes import DataStore
from ..postprocess import postprocessing_methods as pm


class PostProcessor:
    def __init__(self, parameters=None, data_filename=None):
        self.data_filename = data_filename
        self.parameters = parameters      

    def process(self, f_index=None, use_part=False):
        #If processing whole movie f_index is None else you are just processing one frame
        if f_index is None:
            data_filename = self.data_filename
        else:
            #Use part relies on data from processing of whole movie
            #else we are storing info in a temporary file.
            if use_part:
                data_filename = self.data_filename
            else:
                data_filename = self.data_filename[:-5] + '_temp.hdf5'
                
        with DataStore(data_filename, load=True) as data:
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
            
            for f in tqdm(range(start, stop, step), 'Postprocessing'):
                for method in self.parameters['postprocess']['postprocess_method']:
                    print(self.parameters['postprocess']['postprocess_method'])
                    method_name, call_num = get_method_name(method)
                    print(method_name)
                    data.df = getattr(pm, method_name)(data.df, f_index=f,parameters=self.parameters, call_num=call_num, section='postprocess')

            data.save(filename=data_filename)


