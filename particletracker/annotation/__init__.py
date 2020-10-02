from labvision.video import WriteVideo, WriteVideoFFMPEG
from ..annotation import annotation_methods as am
from ..general import dataframes
from ..general.parameters import get_method_name
from tqdm import tqdm


class TrackingAnnotator:

    def __init__(self, parameters=None, vidobject=None, data_filename=None, bitrate='HIGH1080',frame=None, framerate=50):
        self.parameters = parameters
        self.cap = vidobject
        self.data_filename=data_filename
        self.output_filename = self.cap.filename[:-4] + '_annotate.mp4'
        #frame_size = (self.cap.height, self.cap.width, 3)


    def annotate(self, f_index=None, use_part=False, bitrate='HIGH1080', framerate=30):
        if f_index is None:
            frame = self.cap.read_frame(n=0)
            if self.parameters['videowriter'] == 'opencv':
                self.out = WriteVideo(filename=self.output_filename, frame=frame)
            elif self.parameters['videowriter'] == 'ffmpeg':
                self.out = WriteVideoFFMPEG(self.output_filename, bitrate=bitrate, framerate=framerate)
            data_filename = self.data_filename

        elif use_part:
            if self.parameters['videowriter'] == 'opencv':
                self.out = WriteVideo(filename=self.output_filename, frame=frame)
            elif self.parameters['videowriter'] == 'ffmpeg':
                self.out = WriteVideoFFMPEG(self.output_filename, bitrate=bitrate, framerate=framerate)
            data_filename = self.data_filename
        else:
            data_filename = self.data_filename[:-5] + '_temp.hdf5'

        with dataframes.DataStore(data_filename, load=True) as data:
            if f_index is None:
                if ('frame_range' in self.parameters['annotate_method']) and (self.parameters['frame_range'] is not None):
                    start = self.parameters['frame_range'][0]
                    stop = self.parameters['frame_range'][1]
                else:
                    start=0
                    stop=self.cap.num_frames - 1
            else:
                start=f_index
                stop=f_index+1
            self.cap.set_frame(start)

            for f in tqdm(range(start, stop, 1), 'Annotating'):
                frame = self.cap.read_frame()
                for method in self.parameters['annotate_method']:
                    method_name, call_num = get_method_name(method)
                    frame = getattr(am, method_name)(frame, data, f, self.parameters, call_num=call_num)
                if f_index is None:
                    self.out.add_frame(frame)

            if f_index is None:
                self.out.close()
                print('vid written')
            else:
                return frame



