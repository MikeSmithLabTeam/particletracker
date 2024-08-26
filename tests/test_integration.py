""" Some autosave features try to reorder these imports breaking stuff!

Add the following to settings.json to stop this:

"editor.formatOnSave": true,
"python.formatting.autopep8Args": ["--ignore", "E402"],

This is the correct order if you want to put them back!

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import particletracker as pt
import pandas as pd

"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import particletracker as pt
import pandas as pd

"""---------------------------------------------------------------------------------------------------------
These tests follow the tutorials and check that the output is as expected.

Note they don't test anything to do with the gui.
---------------------------------------------------------------------------------------------------------"""


def test_eyes():
    """Test follows eye tutorial, checks annotated movie produced and that a particular 
    value occurs in the output dataframe. It then tidys up.
    Test uses: crop, rectangular mask, 
    Preprocessing: grayscale, blur, 
    Track: Hough, 
    Postprocessing: mean,
    Annotation: Circle,
    """
    pt.batchprocess("testdata/eyes.mp4", "testdata/test_eyes.param")
    
    output_video = "testdata/eyes_annotate.mp4"
    output_df = "testdata/eyes.hdf5"
    df = pd.read_hdf(output_df)
    print('success')
    assert os.path.exists(output_video), 'Eyes annotated video not created'
    assert int(df.loc[3, ['x_mean']].to_numpy()[0][0]) == int(
        139.5), df.loc[3, ['x_mean']].to_numpy()[0][0]
    os.remove(output_video)
    os.remove(output_df)
    if os.path.exists(output_df[:-5] + '_temp.hdf5'):
        os.remove(output_df[:-5] + '_temp.hdf5')


def test_colloids():
    """Test follows colloids tutorial, checks annotated movie produced and that a particular 
    value occurs in the output dataframe. It then tidys up.
    Test uses: 
    Preprocessing: grayscale, blur, absolute_diff, threshold
    Track: trackpy, 
    Postprocessing: add_frame_data
    Annotation: circles, particle_labels, trajectories, text_label, var_label
    """
    pt.batchprocess("testdata/colloids.mp4", "testdata/test_colloids.param")
    output_video = "testdata/colloids_annotate.mp4"
    output_df = "testdata/colloids.hdf5"
    df = pd.read_hdf(output_df)
    assert os.path.exists(output_video)
    assert int(df.loc[5, ['mass']].to_numpy()[0][0]) == int(
        929.7972542773452), df.loc[5, ['mass']].to_numpy()[0][0]
    os.remove(output_video)
    os.remove(output_df)
    if os.path.exists(output_df[:-5] + '_temp.hdf5'):
        os.remove(output_df[:-5] + '_temp.hdf5')

def test_hydrogel():
    """Test follows hydrogel tutorial, checks annotated movie produced and that a particular 
    value occurs in the output dataframe. It then tidys up.
    Test uses: crop, rectangular mask, 
    Preprocessing: grayscale, blur, 
    Track: Hough, 
    Postprocessing:voronoi,
    Annotation: Circle,
    """
    pt.batchprocess("testdata/hydrogel.mp4", "testdata/test_hydrogel.param")
    output_video = "testdata/hydrogel_annotate.mp4"
    output_df = "testdata/hydrogel.hdf5"
    df = pd.read_hdf(output_df)
    assert os.path.exists(output_video), 'Hydrogel annotated video not created'
    assert int(df.loc[1, ['voronoi_area']].to_numpy()[3][0]) == int(
        1059.4268820529976), df.loc[1, ['voronoi_area']].to_numpy()[3][0]  # 'tested value in hydrogel df incorrect'
    os.remove(output_video)
    os.remove(output_df)
    if os.path.exists(output_df[:-5] + '_temp.hdf5'):
        os.remove(output_df[:-5] + '_temp.hdf5')

def test_bacteria():
    """Test follows bacteria tutorial, checks annotated movie produced and that a particular 
    value occurs in the output dataframe. It then tidys up.
    Test uses:  
    Preprocessing: grayscale, medianblur, absolute_diff, threshold, fill_holes 
    Track: contours, 
    Postprocessing: contour_boxes, classify
    Annotation: boxes,
    """
    pt.batchprocess("testdata/bacteria.mp4", "testdata/test_bacteria.param")
    output_video = "testdata/bacteria_annotate.mp4"
    output_df = "testdata/bacteria.hdf5"
    df = pd.read_hdf(output_df)
    assert os.path.exists(output_video), 'Bacteria annotated video not created'
    assert int(df.loc[5, ['box_width']].to_numpy()[0][0]) == int(
        5.813776969909668), df.loc[5, ['box_width']].to_numpy()[0][0]
    os.remove(output_video)
    os.remove(output_df)
    if os.path.exists(output_df[:-5] + '_temp.hdf5'):
        os.remove(output_df[:-5] + '_temp.hdf5')

def test_discs():
    """Test follows discs tutorial, checks annotated movie produced and that a particular 
    value occurs in the output dataframe, checks an excel file is exported. It then tidys up.
    Test uses: crop, rectangular mask, 
    Preprocessing: grayscale, medianblur, 
    Track: Hough, 
    Postprocessing: neighbours,
    Annotation: circles, networks, particle_labels,
    """
    pt.batchprocess("testdata/discs.mp4",
                    "testdata/test_discs.param")
    output_video = "testdata/discs_annotate.mp4"
    output_df = "testdata/discs.hdf5"
    output_csv = "testdata/discs.csv"
    df = pd.read_hdf(output_df)
    assert os.path.exists(output_video), 'Error Discs annotated video not created'
    assert os.path.exists(output_csv), 'Error Excel output not created'
    assert df.loc[1, ['x']].to_numpy()[0][0] == 273.5, df.loc[1, ['x']].to_numpy()[
        0][0]  # 'tested value in discs df incorrect'
    os.remove(output_video)
    os.remove(output_df)
    os.remove(output_csv)
    if os.path.exists(output_df[:-5] + '_temp.hdf5'):
        os.remove(output_df[:-5] + '_temp.hdf5')





"""------------------------------------------------------------------------------------------
These tests attempt to check all the methods in one section
------------------------------------------------------------------------------------------"""


def test_preprocess():
    """Testing the preprocessing methods

    This test loads up all the preprocessing methods and crudely tests that they work.
    colour_channel, grayscale, blur, median_blur, threshold, adaptive_threshold, fill_holes, 
    erode, dilate, absolute_diff, subtract_bkg, gamma, brightness_contrast, distance, invert
    """

    pt.batchprocess("testdata/colloids.mp4", "testdata/test_preprocess.param")
    output_video = "testdata/colloids_annotate.mp4"
    output_df = "testdata/colloids.hdf5"
    df = pd.read_hdf(output_df)
    assert os.path.exists(output_video), 'Preprocessing steps errored'
    assert int(df.loc[5, ['x']].to_numpy()[0][0]) == int(
        33.94708869287488), df.loc[5, ['x']].to_numpy()[0][0]
    os.remove(output_video)
    os.remove(output_df)
    if os.path.exists(output_df[:-5] + '_temp.hdf5'):
        os.remove(output_df[:-5] + '_temp.hdf5')


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
    pt.batchprocess("testdata/hydrogel.mp4", "testdata/test_postprocess.param")
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
    if os.path.exists(output_df[:-5] + '_temp.hdf5'):
        os.remove(output_df[:-5] + '_temp.hdf5')
