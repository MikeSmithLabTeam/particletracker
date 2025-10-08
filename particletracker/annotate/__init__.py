from tqdm import tqdm
import os

import numpy as np

from labvision.video import WriteVideo
from labvision.images.basics import display

from ..annotate import annotation_methods as am
from ..general.parameters import get_method_name, get_param_val, get_method_key



class TrackingAnnotator:

    def __init__(self, parameters=None, vidobject=None, data=None,frame=None, framerate=50):
        self.parameters = parameters
        self.cap = vidobject
        self.data=data
        self.pp_store = data.post_store
        self.output_filename = self.cap.filename[:-4] + '_annotate.mp4'

    def annotate(self, f_index=None, lock_part=-1):  
        print("Annotating...") 
        video_output = get_param_val(self.parameters['config']['video_output']['output'])
        
        #If no movie is requested and processing whole then return nothing
        if f_index is None and not video_output:
            return None
        
        #If whole movie and want video
        if f_index is None and video_output:
            scale= get_param_val(self.parameters['config']['video_output']['scale'])
            output_vid=WriteVideo(self.output_filename, frame=self.cap.read_frame(n=0), scale=scale)

        #whole movie
        if f_index is None:
            start = self.cap.frame_range[0]
            stop = self.cap.frame_range[1]
            step = self.cap.frame_range[2]
            df = self.pp_store.df
        else:
            start=f_index
            stop=f_index+1
            step=1
            #If postprocessing is locked read the full dataframe _postprocess.hdf5 otherwise use _temp.hdf5
            if lock_part==2:
                df = self.pp_store.df
                create_temp_hdf(self.pp_store, f_index)
            else:
                self.pp_store.clear_temp_df()
                df = self.pp_store.temp_df

        self.cap.set_frame(start)

        #Do the annotation
        for f in tqdm(range(start, stop, step), 'Annotating'):
            frame = self.cap.read_frame()
            
            try:
                for method in self.parameters['annotate']['annotate_method']:
                    method_name, call_num = get_method_name(method)
                    frame = getattr(am, method_name)(df.copy(), frame, f_index=f, parameters=self.parameters, call_num=call_num, section='annotate')
            except:
                print('No data to annotate')

            if f_index is None and video_output:
                output_vid.add_frame(frame)

        # close movie or return annotated frame
        if f_index is None and video_output:
            output_vid.close()
            print('Annotation complete')
        else:
            return frame

def create_temp_hdf(pp_store, f_index):
    df = pp_store.get_df(f_index=f_index)
    df.to_hdf(pp_store.temp_filename, key='data')