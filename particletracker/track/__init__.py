import os
from PyQt5.QtCore import pyqtSignal, QObject
from tqdm import tqdm
import numpy as np

from ..general import dataframes
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

    def __init__(self, parameters=None, preprocessor=None, vidobject=None, data_filename=None, *args, **kwargs):
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
            if f_index is None:
                start = self.cap.frame_range[0]
                stop = self.cap.frame_range[1]
                step = self.cap.frame_range[2]
            else:
                start = f_index
                stop = f_index + 1
                step=1

            self.cap.set_frame(start)
            
            for f in tqdm(range(start, stop, step), 'Tracking'):
                try:
                    df_frame = self.analyse_frame()
                    data.add_tracking_data(f, df_frame)
                    #Signal to indicate how many frames tracked
                    self.track_progress.emit(f, start, stop, step)
                except:
                    pass
            
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
        if df_frame.empty:
            for column in df_frame.columns:
                df_frame[column] = [np.nan]
        return df_frame
        
