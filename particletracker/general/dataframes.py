import os
import numpy as np
import pandas as pd

def data_filename_create(movie_filename):
    """Wrangle input filenames
    
    Changes individual img to wildcard version but leaves videos unchanged
    img002.png --> img.hdf5
    img*.png --> img.hdf5
    vid001.mp4 --> vid001.hdf5
    """
    path, filename = os.path.split(movie_filename)
    if not os.path.exists(path + '/_temp'):
        os.mkdir(path + '/_temp')
    filename_stub, ext = os.path.splitext(filename)
    if os.path.splitext(movie_filename)[1] in ['.png','.jpg','.tiff','.JPG']:   
        data_filename = os.path.join(path, ''.join([letter for letter in filename_stub if letter.isalpha()]) + '.hdf5')
    else:
        data_filename = os.path.join(path, filename_stub + '.hdf5')
    return data_filename

class DataStore:
    """
    Dataframe Management
    ----------
    df : pandas dataframe
        Contains info on particle positions and properties.
        Index of dataframe is the video frame.
    """

    def __init__(self, filename):
        self.filename = os.path.splitext(filename)[0] + '.hdf5'
        self.df = None
        self.load()
        
    def get_frame(self, frame_index):
        """Get a single frame from the dataset, using cache if available"""
        frame_data  = self.df[self.df.index == frame_index]
        return frame_data.copy()

    def load(self):
        """Load DataFrame"""
        try:
            self.df = pd.read_hdf(self.filename, key='data')           
        except Exception as e:
            print('Error in general.dataframes')
            print(e)
            print('Error in DataStore.load')

    def _clear_cache(self):
        """Clear the frame cache"""
        self.get_frame.cache_clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def set_dtypes(self, data_dict):
        for key, value in data_dict.items():
            if self.df[key].dtype != value:
                self.df[key] = self.df[key].astype(value)

    def set_frame_index(self):
        """Move frame column to index"""
        if 'frame' in self.df.columns.values.tolist():
            if self.df.index.name == 'frame':
                self.df = self.df.drop('frame', 1)
            else:
                self.df = self.df.set_index('frame')



