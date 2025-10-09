import numpy as np
import scipy.spatial as sp
import pandas as pd
import os
import shutil
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from particletracker import batchprocess
from particletracker.postprocess.postprocessing_methods import hexatic_order


def test_network_methods():
    """Testing the postprocessing methods

    Uses hydrogel to test voronoi, neighbours, hexatic

    """
    output_df = "testdata/hydrogel.hdf5"
    temp_dir = "testdata/_temp"

    if os.path.exists(temp_dir):
        # Attempt to delete the folder before the test runs
        shutil.rmtree(temp_dir, ignore_errors=True)

    batchprocess("testdata/hydrogel.mp4", "testdata/test_networks.param")
    
    df = pd.read_hdf(output_df)

    assert int(df.loc[0,'voronoi_area'].to_numpy()[3]) == int(81650), 'Voronoi failed'
    assert df.loc[0,'neighbours'].to_numpy()[3][0] == 29, 'Neighbours failed'
    assert int(100*df.loc[0,'hexatic_order_phase'].to_numpy()[3]) == int(18), 'Hexatic failed'

    os.remove(output_df)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)