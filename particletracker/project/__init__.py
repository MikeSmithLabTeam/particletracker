import os.path
import numpy as np
import pandas as pd

from ..crop import ReadCropVideo
from .. import preprocess, track, link, postprocess, \
    annotate
from ..customexceptions import BaseError, flash_error_msg

class PTWorkflow:
    '''
    PTWorkflow is a parent class that handles the workflow of a particle tracking project.
    '''

    def __init__(self, video_filename=None, error_reporting=None):
        self.video_filename = video_filename
        self.error_reporting=error_reporting
        self.filename = os.path.splitext(self.video_filename)[0]
        self.data_filename = self.filename + '.hdf5'

        #These should be overwritten in child class
        self.crop_select = False
        self.preprocess_select = False
        self.track_select = False
        self.link_select = False
        self.postprocess_select = False
        self.annotate_select = False

        self.parameters = {}

    def _setup(self):
        ''' Setup is a internal class method it instantiates the reader object
        Depending on the settings in PARAMETERS this may also crop the video frames
        as they are requested.'''
        datapath=os.path.dirname(self.video_filename)
        self.parameters['experiment']['video_filename'] = self.video_filename
        self.parameters['postprocess']['add_frame_data']['data_path'] = datapath
        self._create_processes()

    def _create_processes(self, n=0):
        self.cap = ReadCropVideo(parameters=self.parameters,
                                 filename=self.video_filename,error_reporting=self.error_reporting
                                 )
        self.ip = preprocess.Preprocessor(self.parameters)
        
        self.pt = track.ParticleTracker(
            parameters=self.parameters['track'], preprocessor=self.ip,
            vidobject=self.cap, data_filename=self.data_filename)
        self.link = link.LinkTrajectory(
            data_filename=self.data_filename,
            parameters=self.parameters['link'])
        self.pp = postprocess.PostProcessor(
            data_filename=self.data_filename,
            parameters=self.parameters['postprocess'])
        self.an = annotate.TrackingAnnotator(vidobject=self.cap,
                                               data_filename=self.data_filename,
                                               parameters=self.parameters[
                                                   'annotate'], frame=self.cap.read_frame(n=n))
        self.frame = self.cap.read_frame()

    def reset_annotator(self):
        self.an = annotate.TrackingAnnotator(vidobject=self.cap,
                                                       data_filename=self.data_filename,
                                                       parameters=self.parameters[
                                                           'annotate'], frame=self.cap.read_frame(self.parameters['experiment']['frame_range'][0]))

    def process(self, use_part=False, excel=False):
        """Process an entire video

        Process is called on the main instance using the command
        particle_tracking_instance.process(). One call results in the entire
        movie being processed according to the actions selected in the child class.
        i.e track = True
            link = True etc

        if use_part == True the processing perorms the postprocessing and annotation steps only. 

        if excel == True this will export the data as an excel file with the name videoname.xlsx

        :return:
        """
        if not use_part:
            if self.track_select:
                self.pt.track()
            if self.link_select:
                self.link.link_trajectories()
        if self.postprocess_select:
            self.pp.process(use_part=use_part)
        if self.annotate_select:
            self.an.annotate(use_part=use_part)
        print(excel)
        
        if excel:
            df = pd.read_hdf(self.data_filename)
            print(df.head())
            df.to_excel(self.data_filename[:-5] + '.xlsx')


    def process_frame(self, frame_num, use_part=False):
        """Process a single frame

        process_frame() is for use with the tracking guis when
        optimising parameters. It takes the frame indicated by
        frame_num and processes it according to the selected actions.
        ie. track=True, link=True

        Notes
        -----

        Some combinations of actions are not possible. e.g you can't link trajectories
        that haven't been tracked! The software will however allow you to do things progressively
        so that if you have previously tracked a video and it has sucessfully written to a dataframe
        then it will subsequently link that data without needing to retrack the video.
        The same logic applies to annotation etc. It is worth however making backups at various points.
        When processing individual frames the data is temporarily stored in videoname_temp.hdf5 However, during
        process_part or process the data is stored in videoname.hdf5

        The software assumes the datastore is in the same folder as the video being processed.

        If use_part = True the data for first 5 stages is read from file videoname.hdf5 and only postprocess and annotate are
        being run.

        """
        proc_frame = self.cap.read_frame(frame_num)
        
        try:
            if not use_part:
                if self.preprocess_select:
                    proc_frame = self.ip.process(proc_frame)
                    proc_frame = self.cap.apply_mask(proc_frame)
                if self.track_select:
                    self.pt.track(f_index=frame_num)            
                if self.link_select:
                    self.link.link_trajectories(f_index=frame_num)
            if self.postprocess_select:
                self.pp.process(f_index=frame_num, use_part=use_part)
            if self.annotate_select:
                annotatedframe = self.an.annotate(f_index=frame_num, use_part=use_part)
            else:
                annotatedframe = self.cap.read_frame(frame_num)
        except BaseError as e:     
            if self.error_reporting is not None:
                flash_error_msg(e, self.error_reporting)
            annotatedframe = self.cap.read_frame(frame_num)
            self.error_reporting.toggle_img.setChecked(False)
            self.error_reporting.toggle_img.setText("Captured Image")
            
        return annotatedframe, proc_frame

