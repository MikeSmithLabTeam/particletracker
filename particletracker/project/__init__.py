import os.path
import numpy as np
import pandas as pd

from ..crop import ReadCropVideo
from .. import preprocess, track, link, postprocess, \
    annotate
from ..general.writeread_param_dict import read_paramdict_file
from ..general.dataframes import data_filename_create
from ..customexceptions import BaseError, flash_error_msg, CsvError



class PTWorkflow:
    '''
    PTWorkflow is a parent class that handles the workflow of a particle tracking project. If you don't worry about 
    the gui then this is the top level class that handles everything. It is called directly by the batchprocess function.
    '''

    def __init__(self, video_filename=None, param_filename=None, error_reporting=None):
        self.video_filename = video_filename
        self.error_reporting = error_reporting
        self.data_filename = data_filename_create(self.video_filename)
        path, file = os.path.split(self.data_filename)
        self.temp_folder = path + '/_temp'
        self.param_filename = param_filename
        self.parameters = read_paramdict_file(self.param_filename)
        #self.select_tabs()
        self._setup()

    def select_tabs(self):
        """Boolean values that determine which parts of the tracking process run"""
        self.experiment_select = self.parameters['selected']['experiment']
        self.crop_select = self.parameters['selected']['crop']
        self.preprocess_select = self.parameters['selected']['preprocess']
        self.track_select = self.parameters['selected']['track']
        self.link_select = self.parameters['selected']['link']
        self.postprocess_select = self.parameters['selected']['postprocess']
        self.annotate_select = self.parameters['selected']['annotate']

    def _setup(self):
        ''' Setup is an internal class method it instantiates the video reader object.
        Depending on the settings in PARAMETERS this may also crop the video frames
        as they are requested.'''
        datapath = os.path.dirname(self.video_filename)
        self.parameters['experiment']['video_filename'] = self.video_filename
        self.parameters['postprocess']['add_frame_data']['data_path'] = datapath
        self._create_processes()

    def _create_processes(self):
        """A particle tracking project needs:
        1. A video reading object
        2. Something that handles preprocessing of the images
        3. A tracker to locate objects in the images
        4. A linker that creates trajectories of particles between frames
        5. A postprocessor that does analysis - eg calc velocities or neighbours
        6. An annotator which adds features to the final image to visualise the results

        """
        self.cap = ReadCropVideo(parameters=self.parameters,
                                 filename=self.video_filename, error_reporting=self.error_reporting)
        self.frame = self.cap.read_frame(n=0)

        self.ip = preprocess.Preprocessor(self.parameters)
        
        self.pt = track.ParticleTracker(
                            parameters=self.parameters, 
                            preprocessor=self.ip,
                            vidobject=self.cap, 
                            data_filename=self.data_filename)
        
        self.link = link.LinkTrajectory(
                            data_filename=self.data_filename,
                            parameters=self.parameters)
        
        self.pp = postprocess.PostProcessor(
                    data_filename=self.data_filename,
                    parameters=self.parameters)
        
        self.an = annotate.TrackingAnnotator(vidobject=self.cap,
                                             data_filename=self.data_filename,
                                             parameters=self.parameters,
                                             frame=self.cap.read_frame(n=0))

    def reset_annotator(self):
        self.an = annotate.TrackingAnnotator(vidobject=self.cap,
                                             data_filename=self.data_filename,
                                             parameters=self.parameters,
                                             frame=self.cap.read_frame(self.parameters['config']['frame_range'][0]))

    def process(self, lock_part=-1, f_index=None):
        """Process an entire video

        Idea here is to call process with use_part = None to indicate all steps of the process and then
        0 = just_track
        1 = just_link
        2 = just_postprocess
        3 = just_annotate
        4 = complete --> Creates the final file.

        setting movie=True specifies whole range of movie
        movie=False specifies single frame - This is used by the gui.

        Process is called on the main instance using the command
        particle_tracking_instance.process(). One call results in the entire
        movie being processed according to the actions selected in the child class.

        One potentially confusing thing is that if you process a single frame then you move sequentially
        through preprocessor, tracker, linker, postprocessor and annotator. However, if you process the whole
        then the preprocessor is called from within tracker. All frames are tracked and then all frames are linked etc.


        i.e track = True
            link = True etc

        if use_part == True the processing perorms the postprocessing and annotation steps only. 

        if csv == True this will export the data as an csv file with the name videoname.xlsx

        :return:
        """
        if not os.path.exists(self.temp_folder):
            os.mkdir(self.temp_folder)

        try:
            # Whole movie or one frame
            if f_index is None:
                proc_frame = self.frame
            else:
                proc_frame = self.cap.read_frame(f_index)
                #This will be overwritten below if annotation is required
                proc_frame = self.ip.process(proc_frame)
                proc_frame = self.cap.apply_mask(proc_frame)

            if lock_part < 0:
                self.pt.track(f_index=f_index)
            if lock_part < 1:
                self.link.link_trajectories(f_index=f_index, lock_part=lock_part)
            if lock_part < 2:
                self.pp.process(f_index=f_index, lock_part=lock_part)
            if lock_part < 3:
                annotated_frame = self.an.annotate(f_index=f_index, lock_part=lock_part)
            else:
                annotated_frame = self.frame

            if self.parameters['config']['csv_export']:
                try:
                    df = pd.read_hdf(self.data_filename)
                    df.to_csv(self.data_filename[:-5] + '.csv')
                except Exception as e:
                    CsvError(e)

        except BaseError as e:           
            if self.error_reporting is not None:
                print(e)
                flash_error_msg(e, self.error_reporting)
            self.error_reporting.toggle_img.setChecked(False)
            self.error_reporting.toggle_img.setText("Captured Image")
            proc_frame = self.frame
            annotated_frame = self.frame
        
        return annotated_frame, proc_frame

