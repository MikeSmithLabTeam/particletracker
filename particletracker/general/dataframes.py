from functools import lru_cache
import functools
import pandas as pd
import numpy as np
import os

from particletracker.customexceptions import error_with_hint


class DataManager:
    """Manages data files and caching for particle tracking workflow"""

    def __init__(self, base_filename=None, lock_part=-1):
        # If this is an image sequence base_filename will terminate in an astrix which we remove.
        base_path, base_filename = os.path.split(
            base_filename.replace('*', ''))
        self.base_filename = base_path + '/_temp/' + base_filename
        self.temp_filename = self.base_filename + '_temp.hdf5'
        self._stores = [None, None, None]  # _track, _link, _postprocess
        self.update_lock(lock_part=lock_part)

    def update_lock(self, lock_part=-1):
        DataRead.lock_part = lock_part
        self.clear_data()

    @property
    def track_store(self):
        """Lazy loading of tracking data"""
        #if self._stores[0] is None:
        self._stores[0] = DataRead(
                f"{self.base_filename}_track.hdf5",
                self.temp_filename,
                output_filename=f"{self.base_filename}_link.hdf5",
                store_index=0)
        self._stores[0]

        return self._stores[0]

    @property
    def link_store(self):
        """Lazy loading of tracking data"""
        #if self._stores[1] is None:
        self._stores[1] = DataRead(
                f"{self.base_filename}_link.hdf5",
                self.temp_filename,
                output_filename=f"{self.base_filename}_postprocess.hdf5",
                store_index=1)
        return self._stores[1]

    @property
    def post_store(self):
        """Lazy loading of tracking data"""
        #if self._stores[2] is None:
        self._stores[2] = DataRead(
                f"{self.base_filename}_postprocess.hdf5",
                self.temp_filename,
                output_filename=None,
                store_index=2)
        return self._stores[2]

    def clear_data(self):
        """Clear all data caches"""
        for idx, store in enumerate(self._stores):
            if idx > DataRead.lock_part:
                if store is not None:
                    store.clear_data()
                    #self._stores[idx] = None


class DataRead:
    """Enhanced DataStore with caching"""
    lock_part = -1

    def __init__(self, read_filename, temp_filename, output_filename=None, store_index=0):
        """
        Initialize DataStore for reading and combining dataframes to be outputted and written to a different DataStore.

        Parameters
        ----------
        read_filename : str
            Path to full input HDF5 file
        temp_filename : str
            Path to temporary HDF5 file
        output_filename : str
            Path to output_filename
        store_index : str
            index indicating whether this is for tracking (0), linking (1) or postprocessing (2)
        """
        self.read_filename = read_filename
        self.temp_filename = temp_filename
        self.output_filename = output_filename
        self.store_index = store_index
        self._df = None
        self._temp_df = None
        self.full=False

    @property
    def df(self):
        """Returns full dataframe. Loads lazily."""
        if self._df is None:
            self._df = self._load(self._df, full=True)
        return self._df

    @property
    def temp_df(self):
        """Returns temporary dataframe. Loads lazily"""
        self._temp_df = self._load(self._temp_df, full=False)
        return self._temp_df

    def _load(self, df, full=False):
        """internal loading method"""
        try:
            if full:
                df = pd.read_hdf(self.read_filename, key='data')
            else:
                df = pd.read_hdf(self.temp_filename, key='data')
            if not df.index.is_monotonic_increasing:
                df.sort_index(inplace=True)
            return df  
        except Exception as e:
            print(f'Error loading file: {e}')
            return pd.DataFrame()
    
    def get_df(self, f_index=None):
        """Returns single or whole frame from the whole dataframe in _df.

        Parameters
        ----------
        f_index : int        

        Returns
        -------
        pd.DataFrame
        """
        if not self.full:
            return self.temp_df
        else:
            df=self.df
            if f_index is None:
                return df
            else:
                try:
                    frame_data = df.loc[f_index]
                    if isinstance(frame_data, pd.Series):
                        # If only one row, convert to DataFrame
                        frame_data = frame_data.to_frame().T
                except KeyError:
                    frame_data = df.iloc[0:0]
                    print(f'Frame {f_index} not found in data')
                return frame_data

    def clear_data(self):
        self._df = None
        self._temp_df = None

    @error_with_hint("HINT: this often happens if you try to use a method in gui that requires previous stage to be locked. You can still process the entire movie.")
    def combine_data(self, modified_df=None):
        # Get frame index from modified data
        frame_idx = modified_df.index[0]
        
        if self.full:
            df = self.df
        else:
            df = self.temp_df

        # Add new columns with NaN values
        new_cols = modified_df.columns.difference(df.columns)
        
        for col in new_cols:
            df[col] = pd.Series(dtype=modified_df[col].dtype)
        
        # Update the specific frame with new values
        mask = df.index == frame_idx
        
        for col in modified_df.columns:
            df.loc[mask, col] = modified_df[col].values.squeeze()
        
        return df
        


def df_single(func):
    """df_single decorator is designed to send a single frame of the data to a function"""
    @functools.wraps(func)
    def wrapper_param_format(*args, **kwargs):
        store = args[0]
        new_args = (store.get_df(f_index=kwargs['f_index']),) + args[1:]
        return func(*new_args, **kwargs)
    return wrapper_param_format


def df_range(func):
    """df_range decorator is designed to send a range of frames of the data to a function"""
    @functools.wraps(func)
    def wrapper_param_format(*args, **kwargs):
        store = args[0]
        f_index = kwargs['f_index']
        parameters = kwargs['parameters']

        #Get the whole dataframe
        df = store.get_df(f_index=None)

        if 'output_name' in parameters.keys():
            output_name = parameters['output_name']
            if output_name not in df.columns:
                df[output_name] = np.nan

        span = parameters['span']

        if f_index is not None:
            # Calculate minimum required frame range for rolling operations
            half_span = np.floor(span / 2)
            start = max(f_index - half_span, df.index.min())
            finish = min(f_index + half_span, df.index.max())
        else:
            # For full dataset processing, use all frames
            start = df.index.min()
            finish = df.index.max()
        
        if 'column_name' in parameters.keys():
            #Used in postprocessing for rolling averages etc
            new_args = (df.loc[start:finish],) + args[1:]  # column
        else:
            #Used in annotation for trajectories
            new_args = (df.loc[start:finish, [parameters['x_column'], parameters['y_column'],'particle']],) + args[1:]  # column
        return func(*new_args, **kwargs)
    return wrapper_param_format


class DataWrite:

    def __init__(self, output_filename):
        """Initialize output file for writing"""
        self._output_file = output_filename.replace('*', '')
        self._output_frames = []
        self._output_df = None

    def write_data(self, df, f_index=None):
        """
        Write data to output buffer. close_output will actually write to file. close_output is called
        automatically if context manager used.

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
            merged_df = df.copy()

            if len(self._output_frames) > 0:
                # Get existing columns and data from previous frames
                existing_frame = self._output_frames[-1]
                missing_cols = existing_frame.columns.difference(df.columns)

                # Add missing columns from existing frame, preserving data
                for col in missing_cols:
                    if col in existing_frame:
                        merged_df[col] = existing_frame[col].values
                    else:
                        merged_df[col] = np.nan

            # Set frame index and append
            merged_df.index = pd.Index(
                [f_index] * len(merged_df), name='frame')
            self._output_frames.append(merged_df)
            self._output_df = None

    def close_output(self):
        """Save accumulated data and close output file"""
        try:
            if self._output_df is not None:
                # Write full dataframe
                self._output_df.to_hdf(self._output_file, key='data')
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
