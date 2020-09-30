import os
import numpy as np
import pandas as pd


class DataStore:
    """
    Manages HDFStore containing particle data and metadata
    Attributes
    ----------
    df : pandas dataframe
        Contains info on particle positions and properties.
        Index of dataframe is the video frame.
    metadata : dict
        Dictionary containing any metadata values.
    """

    def __init__(self, filename, load=False):
        self.filename = os.path.splitext(filename)[0] + '.hdf5'
        if load:
            self.load()
        else:
            self.df = pd.DataFrame()
            self.metadata = {}
            self.save()


    def load(self):
        """Load HDFStore"""
        with pd.HDFStore(self.filename) as store:
            self.df = store.get('df')
            self.metadata = store.get_storer('df').attrs.metadata

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

    def set_dtypes(self, data_dict):
        for key, value in data_dict.items():
            if self.df[key].dtype != value:
                self.df[key] = self.df[key].astype(value)

    def add_frame_property(self, heading, values):
        """
        Add data for each frame.
        Parameters
        ----------
        heading: str
            title of dataframe column
        values: arraylike
            array of values with length = num_frames
        """
        prop = pd.Series(values,
                         index=pd.Index(np.arange(len(values)), name='frame'))
        self.df[heading] = prop

    def add_metadata(self, name, data):
        """
        Add metadata to store.
        Parameters
        ----------
        name: str
            string key for dictionary
        data: Any
            Anything that can be saved as a dictionary item
        """
        self.metadata[name] = data

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
        if isinstance(tracked_data, pd.DataFrame):
            self._add_tracking_dataframe(frame, tracked_data)
        else:
            self._add_tracking_array(frame, tracked_data, col_names)

    def _add_tracking_dataframe(self, frame, data):
        data['frame'] = frame
        self.df = self.df.append(data.set_index('frame'))

    def _add_tracking_array(self, frame, data, col_names):
        if isinstance(data, np.ndarray):
            col_names = ['x', 'y', 'r'] if col_names is None else col_names
            data_dict = {name: data[:, i] for i, name in enumerate(col_names)}

        elif isinstance(data, list):
            data_dict = {name: data[i] for i, name in enumerate(col_names)}

        else:
            print('type wrong')
        data_dict['frame'] = frame
        new_df = pd.DataFrame(data_dict).set_index('frame')
        self.df = self.df.append(new_df)

    def append_store(self, store):
        """
        Append an instance of this class to itself.
        Parameters
        ----------
        store: seperate instance of this class
        """
        self.df = self.df.append(store.df)
        self.metadata = {**self.metadata, **store.metadata}

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
        """Save HDFStore"""
        self.add_headings_to_metadata()
        if filename is None:
            with pd.HDFStore(self.filename) as store:
                store.put('df', self.df)
                store.get_storer('df').attrs.metadata = self.metadata
                store.close()
        else:
            with pd.HDFStore(filename) as store:
                store.put('df', self.df)
                store.get_storer('df').attrs.metadata = self.metadata
                store.close()

    def add_headings_to_metadata(self):
        self.metadata['headings'] = self.headings

    def set_frame_index(self):
        """Move frame column to index"""
        if 'frame' in self.df.columns.values.tolist():
            if self.df.index.name == 'frame':
                self.df = self.df.drop('frame', 1)
            else:
                self.df = self.df.set_index('frame')


def load_metadata(filename):
    with pd.HDFStore(filename) as store:
        metadata = store.get_storer('df').attrs.metadata
    return metadata


def concatenate_datastore(datastore_list, new_filename):
    DS_out = DataStore(new_filename, load=False)
    for file in datastore_list:
        DS = DataStore(file, load=True)
        DS_out.append_store(DS)
    DS_out.save()


if __name__ == "__main__":
    from Generic import filedialogs

    file = filedialogs.load_filename()
    DS = DataStore(file)
    print(DS.df.head())
    print(DS.df.tail())
    print(DS.metadata)
    print(DS.df.dtypes)

