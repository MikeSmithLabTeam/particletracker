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
import shutil
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from particletracker import suppress_warnings
from particletracker import batchprocess
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
    output_video = "testdata/eyes_annotate.mp4"
    output_df = "testdata/eyes.hdf5"
    temp_dir = "testdata/_temp"

    if os.path.exists(temp_dir):
        # Attempt to delete the folder before the test runs
        shutil.rmtree(temp_dir, ignore_errors=True)

    batchprocess("testdata/eyes.mp4", "testdata/test_eyes.param")
    
    
    df = pd.read_hdf(output_df)
    
    assert os.path.exists(output_video), 'Eyes annotated video not created'
    assert int(df.loc[3, ['x_mean']].to_numpy()[0][0]) == int(
        152.3), df.loc[3, ['x_mean']].to_numpy()[0][0]
    os.remove(output_video)
    os.remove(output_df)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def test_colloids():
    """Test follows colloids tutorial, checks annotated movie produced and that a particular 
    value occurs in the output dataframe. It then tidys up.
    Test uses: 
    Preprocessing: grayscale, blur, absolute_diff, threshold
    Track: trackpy, 
    Postprocessing: add_frame_data
    Annotation: circles, particle_labels, trajectories, text_label, var_label
    """
    output_video = "testdata/colloids_annotate.mp4"
    output_df = "testdata/colloids.hdf5"
    temp_dir = "testdata/_temp"

    if os.path.exists(temp_dir):
        # Attempt to delete the folder before the test runs
        shutil.rmtree(temp_dir, ignore_errors=True)

    batchprocess("testdata/colloids.mp4", "testdata/test_colloids.param")
    


    df = pd.read_hdf(output_df)
    
    assert os.path.exists(output_video)
    assert int(df.loc[0, ['mass']].to_numpy()[0][0]) == int(
        1210.1742613661322), df.loc[0, ['mass']].to_numpy()[0][0]
    os.remove(output_video)
    os.remove(output_df)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def test_hydrogel():
    """Test follows hydrogel tutorial, checks annotated movie produced and that a particular 
    value occurs in the output dataframe. It then tidys up.
    Test uses: crop, rectangular mask, 
    Preprocessing: grayscale, blur, 
    Track: Hough, 
    Postprocessing:voronoi,
    Annotation: Circle,
    """
    output_video = "testdata/hydrogel_annotate.mp4"
    output_df = "testdata/hydrogel.hdf5"
    temp_dir = "testdata/_temp"

    if os.path.exists(temp_dir):
        # Attempt to delete the folder before the test runs
        shutil.rmtree(temp_dir, ignore_errors=True)

    batchprocess("testdata/hydrogel.mp4", "testdata/test_hydrogel.param")
    

    df = pd.read_hdf(output_df)

    assert os.path.exists(output_video), 'Hydrogel annotated video not created'
    assert int(df.loc[0, ['voronoi_area']].to_numpy()[2][0]) == int(1145.768422864055), df.loc[0, ['voronoi_area']].to_numpy()[2][0]  # 'tested value in hydrogel df incorrect'
    os.remove(output_video)
    os.remove(output_df)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def test_bacteria():
    """Test follows bacteria tutorial, checks annotated movie produced and that a particular 
    value occurs in the output dataframe. It then tidys up.
    Test uses:  
    Preprocessing: grayscale, medianblur, absolute_diff, threshold, fill_holes 
    Track: contours, 
    Postprocessing: contour_boxes, classify
    Annotation: boxes,
    """
    output_video = "testdata/bacteria_annotate.mp4"
    output_df = "testdata/bacteria.hdf5"
    temp_dir = "testdata/_temp"

    if os.path.exists(temp_dir):
        # Attempt to delete the folder before the test runs
        shutil.rmtree(temp_dir, ignore_errors=True)

    batchprocess("testdata/bacteria.mp4", "testdata/test_bacteria.param")
    
    df = pd.read_hdf(output_df)
    assert os.path.exists(output_video), 'Bacteria annotated video not created'
    assert int(df.loc[0, ['box_width']].to_numpy()[0][0]) == int(
        4.0), df.loc[0, ['box_width']].to_numpy()[0][0]
    os.remove(output_video)
    os.remove(output_df)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def test_discs():
    """Test follows discs tutorial, checks annotated movie produced and that a particular 
    value occurs in the output dataframe, checks an excel file is exported. It then tidys up.
    Test uses: crop, rectangular mask, 
    Preprocessing: grayscale, medianblur, 
    Track: Hough, 
    Postprocessing: neighbours,
    Annotation: circles, networks, particle_labels,
    """
    output_video = "testdata/discs_annotate.mp4"
    output_df = "testdata/discs.hdf5"
    output_csv = "testdata/discs.csv"
    temp_dir = "testdata/_temp"

    if os.path.exists(temp_dir):
        # Attempt to delete the folder before the test runs
        shutil.rmtree(temp_dir, ignore_errors=True)

    batchprocess("testdata/discs.mp4",
                    "testdata/test_discs.param")
    
    df = pd.read_hdf(output_df)
    assert os.path.exists(output_video), 'Error Discs annotated video not created'
    assert df.loc[0, ['x']].to_numpy()[0][0] == 1019.5, df.loc[0, ['x']].to_numpy()[
        0][0]  # 'tested value in discs df incorrect'
    os.remove(output_video)
    os.remove(output_df)

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


"""------------------------------------------------------------------------------------------
These tests attempt to check all the methods in one section
------------------------------------------------------------------------------------------"""




