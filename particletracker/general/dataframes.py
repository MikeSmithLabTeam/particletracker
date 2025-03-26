from functools import lru_cache
import functools
import pandas as pd
import numpy as np
import os


class DataManager:
    """Manages data files and caching for particle tracking workflow"""

    def __init__(self, base_filename=None, lock_part=-1):
        base_path, base_filename = os.path.split(base_filename)
        self.base_filename = base_path + '/_temp/' + base_filename
        self.temp_filename = self.base_filename + '_temp.hdf5'
        self._stores = [None, None, None]  # _track, _link, _postprocess
        self.update_lock(lock_part=lock_part)

    def update_lock(self, lock_part=-1):
        DataRead.lock_part = lock_part
        self.clear_caches()

    @property
    def track_store(self):
        """Lazy loading of tracking data"""
        if self._stores[0] is None:
            self._stores[0] = DataRead(
                f"{self.base_filename}_track.hdf5",
                self.temp_filename,
                store_index=0)
        return self._stores[0]

    @property
    def link_store(self):
        """Lazy loading of tracking data"""
        if self._stores[1] is None:
            self._stores[1] = DataRead(
                f"{self.base_filename}_link.hdf5",
                self.temp_filename,
                store_index=1)
        return self._stores[1]

    @property
    def post_store(self):
        """Lazy loading of tracking data"""
        if self._stores[2] is None:
            self._stores[2] = DataRead(
                f"{self.base_filename}_postprocess.hdf5",
                self.temp_filename,
                store_index=2)
        return self._stores[2]

    def clear_caches(self):
        """Clear all data caches"""
        for idx, store in enumerate(self._stores):
            if idx > DataRead.lock_part:
                if store is not None:
                    store._clear_cache()
                    self._stores[idx] = None


class DataRead:
    """Enhanced DataStore with caching"""
    lock_part = -1

    def __init__(self, read_filename, temp_filename, store_index=0):
        """
        Initialize DataStore with separate input and output files

        Parameters
        ----------
        read_filename : str
            Path to full input HDF5 file
        temp_filename : str
            Path to temporary HDF5 file
        """
        self.read_filename = read_filename
        self.temp_filename = temp_filename
        self.store_index = store_index
        self._df=None
        self._clear_cache()

    def _load(self):
        """Lazy load DataFrame from read_filename"""
        try:
            if self._df is None:
                self._df = pd.read_hdf(self.read_filename, key='data')
            if not self._df.index.is_monotonic_increasing:
                self._df.sort_index(inplace=True)
        except Exception as e:
            print(f'Error loading read file: {e}')

    def reload(self):
        self._clear_cache()
        self._load()

    def get_data(self, f_index=None, full=True):
        """
        Get data from the dataset with caching for single frames and lazy loading.

        Parameters
        ----------
        f_index : int, optional
            If provided, returns single frame data (using cache)
            If None, returns entire DataFrame

        Returns
        -------
        pd.DataFrame
            Requested data
        """

        if f_index is None:
            self._load()
            return self._df
        else:
            if full or self.store_index == DataRead.lock_part:
                #Want to read from the full file either because you want to process one frame at a time
                # or because the previous stage is locked and you want to benefit from caching
                #Important that you call reload() before starting a full dataframe analysis. Or if you update
                #the data.
                if self._df is None:
                    self._load()
                return self._get_frame(f_index)
            else:
                #This should be when you want to read from the temporary file
                return pd.read_hdf(self.temp_filename, key='data')
                
            
    @lru_cache(maxsize=4)
    def _get_frame(self, f_index):
        """
        Cached access for single frame retrieval

        Parameters
        ----------
        f_index : int
            Frame number to retrieve

        Returns
        -------
        pd.DataFrame
            Single frame data
        """
        try:
            frame_data = self._df.loc[f_index]
            if isinstance(frame_data, pd.Series):
                # If only one row, convert to DataFrame
                frame_data = frame_data.to_frame().T
        except KeyError:
            frame_data = self._df.iloc[0:0]
            print(f'Frame {f_index} not found in data')
        return frame_data.copy()

    def _clear_cache(self):
        """Clear the frame reading cache"""
        self._get_frame.cache_clear()
        self._df=None


def df_single(func):
    """df_single decorator is designed to send a single frame of the data to a function"""
    @functools.wraps(func)
    def wrapper_param_format(*args, **kwargs):
        store = args[0]
        new_args = (store.get_data(f_index=kwargs['f_index'], full=kwargs['full']),) + args[1:]
        return func(*new_args, **kwargs)
    return wrapper_param_format

def df_range(func):
    """df_range decorator is designed to send a range of frames of the data to a function"""
    @functools.wraps(func)
    def wrapper_param_format(*args, **kwargs):
        store = args[0]
        df = store.get_data(f_index=None, full=True)
        f_index=kwargs['f_index']
        parameters = kwargs['parameters']
        column = parameters['column_name']
        output_name = parameters['output_name']
        span = parameters['span']

        if output_name not in df.columns:
            df[output_name] = np.nan

        start=f_index-span + 1
        if start < 0:
            start = 0

        finish=f_index + span + 1
        if finish > df.index.max():
            finish = df.index.max()

        new_args = (df.loc[start:finish,[column,'particle']],) + args[1:]
        return func(*new_args, **kwargs)
    return wrapper_param_format

class DataWrite:

    def __init__(self, output_filename):
        """Initialize output file for writing"""
        self._output_file = output_filename
        self._output_frames = []
        self._output_df = None

    def write_data(self, df, f_index=None):
        """
        Write data to output file

        Parameters
        ----------
        df : pd.DataFrame
            Data to write
        f_index : int, optional
            If provided, writes single frame data
            If None, writes entire DataFrame
        """
        if f_index is None:
            # Store whole DataFrame
            self._output_df = df
        else:
            # Collect frame for later concatenation
            df.index = pd.Index([f_index] * len(df), name='frame')
            self._output_frames.append(df)
            self._output_df = None

    def close_output(self):
        """Save accumulated data and close output file"""
        try:
            if self._output_df is not None:
                # Write full dataframe
                self._output_df.to_hdf(self._output_file, 'data')
            elif self._output_frames:
                # Concatenate and write collected frames
                final_df = pd.concat(self._output_frames)
                final_df.to_hdf(self._output_file, key='data')
        except Exception as e:
            print(f'Error in writing data: {e}')
            raise  # Re-raise the exception after cleanup
        finally:
            # Clear all stored data
            self._output_df = None
            self._output_frames = []
            self._output_file = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_output()
        return None

