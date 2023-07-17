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

    def __init__(self, filename, load=False):
        self.filename = os.path.splitext(filename)[0] + '.hdf5'
        if load:
            self.load()
        else:
            self.df = pd.DataFrame()
            self.save()


    def load(self):
        """Load DataFrame"""
        try:
            self.df = pd.read_hdf(self.filename, key='data')           
        except Exception as e:
            print('Error in general.dataframes')
            print(e)
            print('Error in DataStore.load')


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

    def set_dtypes(self, data_dict):
        for key, value in data_dict.items():
            if self.df[key].dtype != value:
                self.df[key] = self.df[key].astype(value)


    def add_particle_property(self, heading, values):
        """
        Add properties for each particle in the dataframe
        Parameters
        ----------
        heading: str
            Title of dataframe column
        values: arraylike
            Array of values with same length as dataframe
        """
        self.df[heading] = values

    def add_tracking_data(self, frame, tracked_data, col_names=None):
        """
        Add tracked data for each frame.
        Parameters
        ----------
        frame: int
            Frame number
        tracked_data: arraylike
            (N, D) shape array of N particles with D properties
        col_names: list of str
            Titles of each D properties for dataframe columns
        """
        print('tracking data on Dataframes')
        if isinstance(tracked_data, pd.DataFrame):
            self._add_tracking_dataframe(frame, tracked_data)
        else:
            self._add_tracking_array(frame, tracked_data, col_names)

    def _add_tracking_dataframe(self, frame, data):
        data['frame'] = frame
        self.df = pd.concat([self.df,data.set_index('frame')])

    def _add_tracking_array(self, frame, data, col_names):
        if isinstance(data, np.ndarray):
            col_names = ['x', 'y', 'r'] if col_names is None else col_names
            data_dict = {name: data[:, i] for i, name in enumerate(col_names)}
        elif isinstance(data, list):
            data_dict = {name: data[i] for i, name in enumerate(col_names)}
        else:
            print('type wrong')
        data_dict['frame'] = frame
        new_df = pd.DataFrame(data_dict)
        #self.df = self.df.append(new_df)
        self.df = pd.concat([self.df, new_df.set_index('frame')])

    def append_store(self, store):
        """
        Append an instance of this class to itself.
        Parameters
        ----------
        store: seperate instance of this class
        """
        self.df = self.df.append(store.df)

    def get_column(self, name):
        return self.df[name].values

    @property
    def headings(self):
        return self.df.columns.values.tolist()

    def get_info(self, frame, headings):
        """
        Get information on particles in a particular frame.
        Parameters
        ----------
        frame: int
        headings: list of str
            Titles of dataframe columns to be returned
        """
        return self.df.loc[frame, headings].values

    def reset_index(self):
        """Move frame index to column"""
        self.df = self.df.reset_index()

    def save(self, filename=None):
        try:
            if filename is None:
                self.df.to_hdf(self.filename,'data')
            else:
                self.df.to_hdf(filename, 'data')
        except Exception as e:
            print('Error in general.dataframes')
            print(e)
            print('Error in DataStore.save')

    def set_frame_index(self):
        """Move frame column to index"""
        if 'frame' in self.df.columns.values.tolist():
            if self.df.index.name == 'frame':
                self.df = self.df.drop('frame', 1)
            else:
                self.df = self.df.set_index('frame')



