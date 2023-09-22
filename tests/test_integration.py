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
    assert os.path.exists(output_video), 'Eyes annotated video not created'
    assert int(df.loc[5, ['x_mean']].to_numpy()[0][0]) == int(
        153.9), 'tested value in eyes df incorrect'
    os.remove(output_video)
    os.remove(output_df)


def test_bacteria():
    """Test follows bacteria tutorial, checks annotated movie produced and that a particular 
    value occurs in the output dataframe. It then tidys up.
    Test uses:  
    Preprocessing: grayscale, medianblur, absolute_diff, threshold, fill_holes 
    Track: contours, 
    Postprocessing: contour_boxes, classify,
    Annotation: boxes,
    """
    pt.batchprocess("testdata/bacteria.mp4", "testdata/test_bacteria.param")
    output_video = "testdata/bacteria_annotate.mp4"
    output_df = "testdata/bacteria.hdf5"
    df = pd.read_hdf(output_df)
    assert os.path.exists(output_video), 'Bacteria annotated video not created'
    assert int(df.loc[5, ['box_width']].to_numpy()[0][0]) == int(
        5.813776969909668), 'tested value in bacteria df incorrect'
    os.remove(output_video)
    os.remove(output_df)

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
                    "testdata/test_discs.param", excel=True)
    output_video = "testdata/discs_annotate.mp4"
    output_df = "testdata/discs.hdf5"
    output_excel = "testdata/discs.xlsx"
    df = pd.read_hdf(output_df)
    assert os.path.exists(output_video), 'Discs annotated video not created'
    assert os.path.exists(output_excel), 'Excel output not created'
    assert df.loc[5, ['x_mean']].to_numpy()[0][0] == 142.5, df.loc[5, ['x_mean']].to_numpy()[
        0][0]  # 'tested value in discs df incorrect'
    os.remove(output_video)
    os.remove(output_df)
    os.remove(output_excel)


def test_hydrogel():
    """Test follows eye tutorial, checks annotated movie produced and that a particular 
    value occurs in the output dataframe. It then tidys up.
    Test uses: crop, rectangular mask, 
    Preprocessing: grayscale, blur, 
    Track: Hough, 
    Postprocessing: mean,
    Annotation: Circle,
    """
    pt.batchprocess("testdata/hydrogel.mp4", "testdata/test_hydrogel.param")
    output_video = "testdata/hydrogel_annotate.mp4"
    output_df = "testdata/hydrogel.hdf5"
    df = pd.read_hdf(output_df)
    assert os.path.exists(output_video), 'Hydrogel annotated video not created'
    assert int(df.loc[5, ['voronoi_area']].to_numpy()[3][0]) == int(
        833.9376763034877), df.loc[5, ['voronoi_area']].to_numpy()[3][0]  # 'tested value in hydrogel df incorrect'
    os.remove(output_video)
    os.remove(output_df)
