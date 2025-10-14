import numpy as np
import scipy.spatial as sp
import pandas as pd
import os
import shutil
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from particletracker import batchprocess
from particletracker.postprocess.postprocessing_methods import hexatic_order
from tests.test_integration import clean_up


def test_network_methods():
    """Testing the postprocessing methods

    Uses hydrogel to test voronoi, neighbours, hexatic

    """
    output_df = "testdata/hydrogel.hdf5"
    temp_dir = "testdata/_temp"

    clean_up(temp_dir)

    batchprocess("testdata/hydrogel.mp4", "testdata/test_networks.param")
    
    df = pd.read_hdf(output_df)

    assert int(df.loc[0,'voronoi_area'].to_numpy()[3]) == int(81650.5916), int(df.loc[0,'voronoi_area'].to_numpy()[3])
    assert df.loc[0,'neighbours'].to_numpy()[4][0] == 29, df.loc[0,'neighbours'].to_numpy()[4][0]
    assert int(100*df.loc[0,'hexatic_order_phase'].to_numpy()[3]) == int(18.2519), int(100*df.loc[0,'hexatic_order_phase'].to_numpy()[3])

    os.remove(output_df)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def test_rolling_methods():
    """Testing the postprocessing methods associated with rolling

    Uses colloids to test mean, median, diff, rate

    """
    output_df = "testdata/eyes.hdf5"
    temp_dir = "testdata/_temp"

    clean_up(temp_dir)

    batchprocess("testdata/eyes.mp4", "testdata/test_rolling.param")
    
    df = pd.read_hdf(output_df)


    assert df.loc[3,'x_mean'].to_numpy()[0] == np.float64(151.16666666666666),'mean failed'
    assert df.loc[3,'median'].to_numpy()[0] == np.float64(149.5), 'median failed'
    assert df.loc[3,'x_diff'].to_numpy()[0] == np.float32(6.0),df.loc[3,'x_diff'].to_numpy()[0]
    assert df.loc[3,'vx'].to_numpy()[0] == np.float32(100.0), df.loc[3,'vx'].to_numpy()[0]

    os.remove(output_df)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)