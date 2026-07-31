import os
from PyQt6.QtCore import pyqtSignal, QObject
from tqdm import tqdm
import numpy as np
import pandas as pd

from ..general.dataframes import DataWrite
from . import tracking_methods as tm
from .parallel_tracking import track_frames_parallel
from ..general.parameters import get_param_val, get_method_key, param_parse

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


        grabs the parallel_processing method to run tracking serially or using the ProcessPoolExecutor
        (e.g parallel) processing.

        
        Parameters
        ---------
        f_index: int or None
        """
        active_method = self.parameters['track']['track_method'][0]
        parallel_processing = self.parameters['track'][active_method]['parallel_processing'][0] #toggle serial/parallel

        if lock_part == -1:
            if f_index is None:
                'When processing whole video store in file with same name as movie'
                output_filename = f"{self.base_filename}_track.parquet"
            else:
                'store temporarily'
                output_filename = f"{self.base_filename}_temp.parquet"

            if f_index is None:
                start = self.cap.frame_range[0]
                stop = self.cap.frame_range[1]
                step = self.cap.frame_range[2]
            else:
                start = f_index
                stop = f_index + 1
                step=1

            self.cap.set_frame(start)

            if not parallel_processing:
                print("tracking in serial...")
                with DataWrite(output_filename) as store:    
                                for f in tqdm(range(start, stop, step), 'Tracking'):
                                    df_frame = self.analyse_frame(n=f)
                                    store.write_data(df_frame, f_index=f)
                                    #Signal to indicate how many frames tracked
                                    self.track_progress.emit(f, start, stop, step)  
                print('Tracking complete')    

            else:#parallel processing
                print("tracking in parallel...")
                frame_indices = list(range(start, stop, step))
                with DataWrite(output_filename) as store:
                    if f_index is None:
                        # Whole-video pass: worth the pool startup cost,
                        # each frame is independent so spread across cores.
                        progress_bar = tqdm(total=len(frame_indices), desc='Tracking')
    
                        def _handle_result(f, df_frame):
                            store.write_data(df_frame, f_index=f)
                            # Signal to indicate how many frames tracked
                            self.track_progress.emit(f, start, stop, step)
                            progress_bar.update(1)
    
                        track_frames_parallel(
                            self.cap.filename,
                            self.parameters,
                            frame_indices,
                            use_preprocessor=self.ip is not None,
                            on_result=_handle_result,
                        )
                        progress_bar.close()
                    else:
                        # Single frame: pool startup overhead isn't worth it.
                        for f in tqdm(frame_indices, 'Tracking'):
                            df_frame = self.analyse_frame(n=f)
                            store.write_data(df_frame, f_index=f)
                            self.track_progress.emit(f, start, stop, step)
                print('Tracking complete')



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
        
