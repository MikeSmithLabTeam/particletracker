import os
from tqdm import tqdm
from ParticleTrackingGui.general import dataframes
from ParticleTrackingGui.tracking import tracking_methods as tm
from pathlib import Path
import numpy as np

class ParticleTracker:
    """
    Class to track the locations of the particles in a video_crop.

    Notes
    -----

    1) Uses preprocessing.Preprocessor to manipulate images.
    2) Uses methods in tracking_methods to locate the particles
    3) Confirms that each detected particle is real
    4) Saves particle positions and boundary information in a dataframe


    """

    def __init__(self, parameters=None, preprocessor=None, vidobject=None, data_filename=None):
        """

        Parameters
        ----------

        parameters: dictionary
            Contains parameters for any functions

        preprocessor: instance of Preprocessor()

        vidobject: instance of ReadCropVideo()

        data_filename: str
            Filepath for datastore

        """

        self.filename = os.path.splitext(vidobject.filename)[0]
        self.parameters = parameters
        self.ip = preprocessor
        self.cap = vidobject
        self.data_filename = self.filename + '.hdf5'

    def track(self, f_index=None):
        """
        Method called by track.process() and track.process_frame()

        Notes
        -----
        If track is called with f_index=None it will run a tracking method
        on all the frames specified by frame_range when the ReadVideo object was
        instantiated by PTWorkflow. If f_index is an integer value only that frame is
        processed. A store is still created.

        Parameters
        ---------
        f_index: int or None
        """
        if f_index is None:
            'When processing whole video store in file with same name as movie'
            data_filename = self.data_filename
        else:
            'store temporarily'
            data_filename = self.data_filename[:-5] + '_temp.hdf5'

        with dataframes.DataStore(data_filename) as data:
            data.add_metadata('number_of_frames', self.cap.num_frames)
            data.add_metadata('fps', self.cap.fps)
            data.add_metadata('video_filename', self.cap.filename)
            if f_index is None:
                start = 0
                stop = self.cap.num_frames
            else:
                start = f_index
                stop = f_index + 1
            self.cap.set_frame(start)
            for f in tqdm(range(start, stop, 1), 'Tracking'):
                df_frame = self.analyse_frame()
                data.add_tracking_data(f, df_frame)
            data.save(filename=data_filename)

    def analyse_frame(self):
        """Analyses a single frame using a track method specified in PARAMETERS
        Returns
        -------
        Pandas dataframe with tracked data.
        """
        frame = self.cap.read_frame()
        method = self.parameters['track_method'][0]
        if self.ip is None:
            preprocessed_frame = frame
        else:
            preprocessed_frame = self.ip.process(frame)
            preprocessed_frame = self.cap.apply_mask(preprocessed_frame)
        df_frame = getattr(tm, method)(preprocessed_frame, frame, self.parameters)
        return df_frame

    def update_parameters(self, parameters):
        self.parameters = parameters
        self.ip.update_parameters(self.parameters)
