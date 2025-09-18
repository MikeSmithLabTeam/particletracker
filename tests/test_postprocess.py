import numpy as np
import pandas as pd
from particletracker.postprocess.postprocessing_methods import hexatic_order
import scipy.spatial as sp

<<<<<<< HEAD
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
    batchprocess("testdata/hydrogel.mp4", "testdata/test_postprocess.param")
    output_video = "testdata/hydrogel_annotate.mp4"
    output_df = "testdata/hydrogel.hdf5"
    df = pd.read_hdf(output_df)

    assert os.path.exists(output_video), 'Postprocessing steps errored'
    assert int(df.loc[5, ['x']].to_numpy()[0][0]) == int(
        1030), 'Tested x value in df incorrect' + str(df.loc[3, ['x']].to_numpy()[0][0])
    assert int(df.loc[5, ['theta']].to_numpy()[0][0]) == int(
        14.1670555226312), 'Tested angle value in df incorrect'
    assert int(10*df.loc[5, ['hexatic_order_re']].to_numpy()[1][0]) == int(
        10*0.640), 'Tested hexatic_order_re value in df incorrect'
    assert int(100*df.loc[5, ['hexatic_order_ang']].to_numpy()[1][0]) == int(
        100*-0.04394359424687039), 'Tested heaxatic_order_ang value in df incorrect'
    assert int(df.loc[5, ['x_diff']].to_numpy()[0][0]) == int(
        -1.0), 'Tested x_diff value in df incorrect'
    assert int(df.loc[5, ['vx']].to_numpy()[1][0]) == int(
        -30), 'Tested vx value in df incorrect'
    assert int(df.loc[5, ['median_x']].to_numpy()[0][0]) == int(
        862), 'Tested median_x value in df incorrect'
    assert int(df.loc[5, ['number_of_neighbours']].to_numpy()[1][0]) == int(
        3.0), 'Tested number_of_neighbours value in df incorrect'

    os.remove(output_video)
    os.remove(output_df)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
||||||| 64f60168
=======
def test_hexatic_order():
    """Testing that the hexatic_order() function in particle 
     tracker postprocessing methods works. Has the param parse
      decorator attached. """
    
    param = {'postprocess':{'hexatic_order':{
            'cutoff':[5]}}}
    
    data = pd.read_hdf("testdata/hexatic_test_data.hdf5")
    data = hexatic_order(data, f_index=0, parameters=param, call_num=None, section='postprocess')
    hexatic_col = data["hexatic_order"]
    value = hexatic_col.iloc[[3][0]]    #pick particle away from edge
    assert int(np.real(value)) == 1
    assert int(np.imag(value)) == 0
>>>>>>> 3b7588ff46e3cbbcbcca6525623880719a0f83d2
