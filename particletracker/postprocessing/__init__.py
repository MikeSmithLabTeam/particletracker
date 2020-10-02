from general.parameters import get_method_name
from general.dataframes import DataStore
from postprocessing import postprocessing_methods as pm


class PostProcessor:
    def __init__(self, parameters=None, vidobject=None, data_filename=None):
        self.parameters = parameters
        self.cap = vidobject
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

        self.data = DataStore(input_filename, load=True)

        self.data.df['frame'] = self.data.df.index
        self.data.df.index.name = 'index'

        self.data.df = self.data.df.sort_values(['particle', 'frame'])

        for method in self.parameters['postprocess_method']:
            method_name, call_num = get_method_name(method)
            self.data.df = getattr(pm, method_name)(self.data.df, f_index=f_index,parameters=self.parameters, call_num=call_num)

        self.data.save(filename=output_filename)

