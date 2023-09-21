from tqdm import tqdm

from ..general.parameters import get_method_name
from ..general.dataframes import DataStore
from ..postprocess import postprocessing_methods as pm


class PostProcessor:
    def __init__(self, parameters=None, data_filename=None):
        self.parameters = parameters

        self.data_filename = data_filename

    def process(self, f_index=None, use_part=False):
        if f_index is None:
            input_filename = self.data_filename
            output_filename = self.data_filename
        else:
            if use_part:
                input_filename = self.data_filename
                output_filename = self.data_filename
            else:
                input_filename = self.data_filename[:-5] + '_temp.hdf5'
                output_filename = self.data_filename[:-5] + '_temp.hdf5'

        with DataStore(input_filename, load=True) as data:
            if f_index is None:
                frame_range = self.parameters['experiment']['frame_range']
                start=frame_range[0]
                stop=frame_range[1]
                if stop is None:
                    stop = data.df.index.max() + 1
                step=frame_range[2]
            else:
                start=f_index
                stop=f_index+1
                step=1
            
            for f in tqdm(range(start, stop, step), 'Postprocessing'):
                for method in self.parameters['postprocess']['postprocess_method']:
                    method_name, call_num = get_method_name(method)
                    data.df = getattr(pm, method_name)(data.df, f_index=f,parameters=self.parameters, call_num=call_num)
                    #comment

            data.save(filename=output_filename)


