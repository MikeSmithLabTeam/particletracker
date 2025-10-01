import numpy as np
import pandas as pd
from particletracker.postprocess.postprocessing_methods import hexatic_order
import scipy.spatial as sp

import pandas as pd
import os
import shutil

from particletracker import batchprocess



def test_postprocess():
    """Testing the postprocessing methods

    test_eyes checks the mean
    test_bacteria checks the contour_boxes and classify
    test_colloids checks the add_frame_data
    test_hydrogel checks the voronoi
    test_discs checks the neighbours

    Here we test the remaining methods where possible.
    If you are going to use these you should still check the output
    makes sense as we didn't double check the output when we wrote these.
    Passing tests implies the code produces the same result as before!!

    """
    output_video = "testdata/hydrogel_annotate.mp4"
    output_df = "testdata/hydrogel.hdf5"
    temp_dir = "testdata/_temp"

    if os.path.exists(temp_dir):
        # Attempt to delete the folder before the test runs
        shutil.rmtree(temp_dir, ignore_errors=True)

    #batchprocess("testdata/hydrogel.mp4", "testdata/test_postprocess.param")
    
    #df = pd.read_hdf(output_df)

    assert False, "This is yet to be setup"

    os.remove(output_video)
    os.remove(output_df)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
