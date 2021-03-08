from ..general.parameters import get_method_name
from ..general.dataframes import DataStore
from ..postprocess import postprocessing_methods as pm


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
        
        #Check df is arranged properly
        index_names = self.data.df.index.names
        column_names = self.data.df.columns

        if ('particle' in index_names) and ('frame' in index_names):
            if 'particle' in column_names:
                self.data.df.pop('particle')
            if 'frame' in column_names:
                self.data.df.pop('frame')
            if 'frame' in index_names[0]:
                self.data.df=self.data.df.swaplevel()
        elif ('particle' in index_names) and ('frame' not in index_names):
            self.data.df.set_index(['frame'],append=True, drop=True,inplace=True)
        elif ('particle' not in index_names) and ('frame' in index_names):
            self.data.df.set_index(['particle'],append=True, drop=True,inplace=True)
            self.data.df=self.data.df.swaplevel()
        else:
            self.data.df.set_index(['frame','particle'], drop=True,inplace=True)
        
        self.data.df.sort_index(inplace=True)

        for method in self.parameters['postprocess_method']:
            method_name, call_num = get_method_name(method)
            self.data.df = getattr(pm, method_name)(self.data.df, f_index=f_index,parameters=self.parameters, call_num=call_num)

        self.data.df.reset_index(level='particle', inplace=True)
        self.data.save(filename=output_filename)

