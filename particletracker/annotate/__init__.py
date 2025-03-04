from tqdm import tqdm
import os

from labvision.video import WriteVideo

from ..annotate import annotation_methods as am
from ..general import dataframes
from ..general.parameters import get_method_name



class TrackingAnnotator:

    def __init__(self, parameters=None, vidobject=None, data=None, bitrate='HIGH1080',frame=None, framerate=50):
        self.parameters = parameters
        self.cap = vidobject
        self.pp_store = data.post_store
        self.output_filename = self.cap.filename[:-4] + '_annotate.mp4'

    def annotate(self, f_index=None, lock_part=-1):   
        if f_index is None:
            output_vid=WriteVideo(self.output_filename, self.cap.frame_size)

        print(self.pp_store.get_data(f_index=1).head())

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
                    frame = getattr(am, method_name)(frame, self.pp_store, f, parameters=self.parameters, call_num=call_num, section='annotate')
            except:
                print('No data to annotate')

            if f_index is None:
                output_vid.add_frame(frame)
        
        # close movie or return annotated frame
        if f_index is None:
            output_vid.close()
            print('Annotation finished')
        else:
            return frame



