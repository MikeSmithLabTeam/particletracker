import os
from PyQt5.QtCore import pyqtSignal, QObject
from tqdm import tqdm
import numpy as np
import pandas as pd

from ..general.dataframes import DataWrite
from ..track import tracking_methods as tm


class ParticleTracker(QObject):
    track_progress = pyqtSignal(int, int, int, int)

    """
    Class to track the locations of the particles in a video_crop.

    Notes
    -----

    1) Uses preprocessing.Preprocessor to manipulate images.
    2) Uses methods in tracking_methods to locate the particles
    3) Confirms that each detected particle is real
    4) Saves particle positions and boundary information in a dataframe


    """

    def __init__(self, parameters=None, preprocessor=None, vidobject=None, *args, **kwargs):
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
        super(ParticleTracker,self).__init__(*args, **kwargs)
        
        self.parameters = parameters
        self.ip = preprocessor
        self.cap = vidobject
        path, filename = os.path.split(os.path.splitext(vidobject.filename)[0])
        self.base_filename = path + '/_temp/' + filename
        
    def track(self, f_index=None, lock_part=-1):
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
        if lock_part == -1:
            if f_index is None:
                'When processing whole video store in file with same name as movie'
                output_filename = f"{self.base_filename}_track.hdf5"
            else:
                'store temporarily'
                output_filename = f"{self.base_filename}_temp.hdf5"

            if f_index is None:
                start = self.cap.frame_range[0]
                stop = self.cap.frame_range[1]
                step = self.cap.frame_range[2]
            else:
                start = f_index
                stop = f_index + 1
                step=1

            self.cap.set_frame(start)

            with DataWrite(output_filename) as store:    
                for f in tqdm(range(start, stop, step), 'Tracking'):
                    df_frame = self.analyse_frame(n=f)
                    store.write_data(df_frame, f_index=f)
                    #Signal to indicate how many frames tracked
                    self.track_progress.emit(f, start, stop, step)               

    def analyse_frame(self, n=None):
        """Analyses a single frame using a track method specified in PARAMETERS
        Returns
        -------
        Pandas dataframe with tracked data.
        """
        frame = self.cap.read_frame(n=n)
        method = self.parameters['track']['track_method'][0]
        
        if self.ip is None:
            preprocessed_frame = frame
        else:
            preprocessed_frame = self.ip.process(frame)
            preprocessed_frame = self.cap.apply_mask(preprocessed_frame)
        
        #Apply tracking track method to frame
        df_frame = getattr(tm, method)(preprocessed_frame, frame, self.parameters, section='track')
    
        if df_frame.empty:
            for column in df_frame.columns:
                df_frame[column] = [np.nan]
        return df_frame
        
