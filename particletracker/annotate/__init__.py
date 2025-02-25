from tqdm import tqdm
import os

from labvision.video import WriteVideo

from ..annotate import annotation_methods as am
from ..general import dataframes
from ..general.parameters import get_method_name



class TrackingAnnotator:

    def __init__(self, parameters=None, vidobject=None, data_filename=None, bitrate='HIGH1080',frame=None, framerate=50):
        self.parameters = parameters
        self.cap = vidobject
        path, filename = os.path.split(data_filename)
        self.data_filename = path + '/_temp/' + filename
        self.output_filename = self.cap.filename[:-4] + '_annotate.mp4'

    def annotate(self, f_index=None, lock_part=-1):   
        
        
        if (lock_part >= 2) or (f_index is None):
            #single frame when postprocess is locked or whole movie
            input_filename = self.data_filename[:-5] + '_postprocess.hdf5'
        else:
            #single frame when postprocess not locked
            input_filename = self.data_filename[:-5] + '_temp.hdf5'
            

        output_vid=WriteVideo(self.output_filename, self.cap.frame_size)

        with dataframes.DataStore(input_filename) as data:
            #whole movie
            if f_index is None:
                start = self.cap.frame_range[0]
                stop = self.cap.frame_range[1]
                step = self.cap.frame_range[2]
            else:
                start=f_index
                stop=f_index+1
                step=1
            self.cap.set_frame(start)
            
            #Do the annotation
            for f in tqdm(range(start, stop, step), 'Annotating'):
                frame = self.cap.read_frame()
                try:
                    for method in self.parameters['annotate']['annotate_method']:
                        method_name, call_num = get_method_name(method)
                        frame = getattr(am, method_name)(frame, data, f, parameters=self.parameters, call_num=call_num, section='annotate')
                except:
                    print('No data to annotate')

                if f_index is None:
                    output_vid.add_frame(frame)
            
            # close movie or return annotated frame
            if f_index is None:
                output_vid.close()
            else:
                return frame



