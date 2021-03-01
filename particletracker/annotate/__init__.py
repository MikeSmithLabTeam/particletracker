from tqdm import tqdm

from labvision.video import WriteVideo, WriteVideoFFMPEG

from ..annotate import annotation_methods as am
from ..general import dataframes
from ..general.parameters import get_method_name



class TrackingAnnotator:

    def __init__(self, parameters=None, vidobject=None, data_filename=None, bitrate='HIGH1080',frame=None, framerate=50):
        self.parameters = parameters
        self.cap = vidobject
        self.data_filename=data_filename
        self.output_filename = self.cap.filename[:-4] + '_annotate.mp4'
        #frame_size = (self.cap.height, self.cap.width, 3)


    def annotate(self, f_index=None, use_part=False, framerate=30):
        frame = self.cap.read_frame(n=0)
        if f_index is None:
            self.out = WriteVideo(filename=self.output_filename, frame=frame)
            data_filename = self.data_filename
        elif use_part:
            #self.out = WriteVideo(filename=self.output_filename, frame=frame)
            data_filename = self.data_filename
        else:
            data_filename = self.data_filename[:-5] + '_temp.hdf5'

        with dataframes.DataStore(data_filename, load=True) as data:
            if f_index is None:
                start = self.cap.frame_range[0]
                stop = self.cap.frame_range[1]
                step = self.cap.frame_range[2]
            else:
                start=f_index
                stop=f_index+1
                step=1
            self.cap.set_frame(start)
            for f in tqdm(range(start, stop, step), 'Annotating'):
                frame = self.cap.read_frame()
                for method in self.parameters['annotate_method']:
                    method_name, call_num = get_method_name(method)
                    frame = getattr(am, method_name)(frame, data, f, self.parameters, call_num=call_num)
                if f_index is None:
                    self.out.add_frame(frame)
            if f_index is None:
                self.out.close()
            else:
                return frame



