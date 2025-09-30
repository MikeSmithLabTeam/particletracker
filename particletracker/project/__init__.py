import os
import numpy as np
import pandas as pd
import shutil

from ..crop import ReadCropVideo
from .. import preprocess, track, link, postprocess, \
    annotate
from ..general.writeread_param_dict import read_paramdict_file
from ..general.dataframes import DataManager
from ..customexceptions import BaseError, flash_error_msg, CsvError
from ..gui.menubar import CustomButton


class PTWorkflow:
    '''
    PTWorkflow is a parent class that handles the workflow of a particle tracking project. If you don't worry about 
    the gui then this is the top level class that handles everything. It is called directly by the batchprocess function.
    '''

    def __init__(self, video_filename=None, param_filename=None, error_reporting=None):
        self.video_filename = video_filename
        self.error_reporting = error_reporting
        self.base_filename = os.path.splitext(self.video_filename)[0]
        path, _ = os.path.split(self.base_filename)
        self.temp_folder = path + '/_temp/'
        self.param_filename = param_filename
        self.parameters = read_paramdict_file(self.param_filename)
        self._setup()

    def _setup(self):
        ''' Setup is an internal class method it instantiates the video reader object.
        Depending on the settings in PARAMETERS this may also crop the video frames
        as they are requested.'''
        datapath = os.path.dirname(self.video_filename)
        self.parameters['config']['_video_filename'] = self.video_filename
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

        #Handles storage, access to and caching of data at each stage of process
        self.data = DataManager(base_filename=self.base_filename)

        self.pt = track.ParticleTracker(
            parameters=self.parameters,
            preprocessor=self.ip,
            vidobject=self.cap)

        self.link = link.LinkTrajectory(
            data=self.data,
            parameters=self.parameters)

        self.pp = postprocess.PostProcessor(
            data=self.data,
            parameters=self.parameters)

        self.reset_annotator()

    def reset_annotator(self):
        self.an = annotate.TrackingAnnotator(vidobject=self.cap,
                                             data=self.data,
                                             parameters=self.parameters,
                                             frame=self.cap.read_frame(self.parameters['config']['_frame_range'][0]))

    def process(self, f_index=None, lock_part=-1):
        """Process an entire video

        Idea here is to call process with lock_part = -1 to indicate all steps of the process and then
        0 = track locked
        1 = link locked
        2 = postprocess locked  --> Creates the final file.
        annotation optional

        - If you just process a single frame then you read a temp.hdf5 datafile from the _temp folder which contains the current frame=f_index data.
        - If you process everything with f_index=None then each stage creates its own file containing data for all frames in _temp folder. The subsequent stage reads from this datafile and saves to a new file. At the end this is copied to the directory containing the video and represents the processed data. An annotated video is optionally produced
        - Once a datafile has been completely processed if the _temp file folder is not cleaned up you can go back and edit things. Locking a particular stage results in data being drawn from a full datafile of previous stage containing complete data. Subsequent stages are either stored in a temporary file for single image processing or in new versions of the datafiles for the later stages if processing everything.

        Process is called on the main instance using the command
        particle_tracking_instance.process(). One call results in the entire
        movie being processed according to the actions selected in the child class.

        One potentially confusing thing is that if you process a single frame then you move sequentially
        through preprocessor, tracker, linker, postprocessor and annotator. However, if you process the whole
        then the preprocessor is called from within tracker. All frames are tracked and then all frames are linked etc.
        """
        if not os.path.exists(self.temp_folder):
            os.mkdir(self.temp_folder)

        try:
            # Whole movie or one frame
            if f_index is None:
                proc_frame = self.frame
            else:
                proc_frame = self.cap.read_frame(f_index)
                # This will be overwritten below if annotation is required
                proc_frame = self.ip.process(proc_frame)
                proc_frame = self.cap.apply_mask(proc_frame)

            if lock_part < 0:
                self.pt.track(f_index=f_index)

            if lock_part < 1:
                self.link.link_trajectories(
                    f_index=f_index, lock_part=lock_part)

            if lock_part < 2:
                self.pp.process(f_index=f_index, lock_part=lock_part)

            if lock_part < 3:
                annotated_frame = self.an.annotate(
                    f_index=f_index, lock_part=lock_part)
            else:
                annotated_frame = self.frame
            if f_index is None:
                move_final_data(self.video_filename)

            
        except BaseError as e:
            if self.error_reporting is not None:
                print(e)
                flash_error_msg(e, self.error_reporting)
                self.error_reporting.toggle_img.setChecked(False)#Moved these two lines in if statement
                self.error_reporting.toggle_img.setText("Captured Image")
            proc_frame = self.frame
            annotated_frame = self.frame

        return annotated_frame, proc_frame

def move_final_data(movie_filename):
    path, filename = os.path.split(movie_filename)
    postprocess_datafile = path + '/_temp/' + filename[:-4] + CustomButton.extension[2]
    output_datafile = path + '/' + filename[:-4] + '.hdf5'

    if os.path.exists(postprocess_datafile):
        shutil.copy(postprocess_datafile, output_datafile)