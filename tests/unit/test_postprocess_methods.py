import os

import cv2
import numpy as np
import pandas as pd
import pytest

from particletracker.postprocess import postprocessing_methods as pp


def test_absolute_creates_abs_column():
    df = pd.DataFrame({'value': [-2, 3, -1]})
    parameters = {
        'postprocess': {
            'absolute': {'column_name': 'value'}
        }
    }

    output = pp.absolute(df.copy(), parameters=parameters, section='postprocess', call_num=None)

    assert 'value_abs' in output.columns
    assert output['value_abs'].tolist() == [2, 3, 1]


def test_add_frame_data_populates_column_for_all_frames(tmp_path):
    frame_values = [10, 20, 30]
    csv_path = tmp_path / 'frame_data.csv'
    pd.Series(frame_values).to_csv(csv_path, index=False, header=False)

    df = pd.DataFrame(index=[0, 1, 2])
    parameters = {
        'postprocess': {
            'add_frame_data': {
                'new_column_name': 'frame_val',
                'data_filename': 'frame_data',
                'data_path': str(tmp_path)
            }
        }
    }

    output = pp.add_frame_data(df.copy(), parameters=parameters, section='postprocess', call_num=None, f_index=None)

    assert output['frame_val'].tolist() == [10, 20, 30]


def test_angle_calculates_degrees():
    df = pd.DataFrame({'dx': [1, 0], 'dy': [0, 1]})
    parameters = {
        'postprocess': {
            'angle': {
                'x_column': 'dx',
                'y_column': 'dy',
                'output_name': 'theta',
                'units': 'degrees'
            }
        }
    }

    output = pp.angle(df.copy(), parameters=parameters, section='postprocess', call_num=None)

    assert np.isclose(output.loc[0, 'theta'], 0.0)
    assert np.isclose(output.loc[1, 'theta'], 90.0)


def test_classify_assigns_boolean_label():
    df = pd.DataFrame({'score': [0, 5, 10]})
    parameters = {
        'postprocess': {
            'classify': {
                'column_name': 'score',
                'output_name': 'is_mid',
                'lower_threshold': 2,
                'upper_threshold': 8
            }
        }
    }

    output = pp.classify(df.copy(), parameters=parameters, section='postprocess', call_num=None)

    assert output['is_mid'].tolist() == [False, True, False]


def test_logic_operators_work_as_expected():
    df = pd.DataFrame({'a': [True, False], 'b': [False, True]})
    and_params = {
        'postprocess': {'logic_AND': {'column_name': 'a', 'column_name2': 'b', 'output_name': 'and_out'}}
    }
    not_params = {
        'postprocess': {'logic_NOT': {'column_name': 'a', 'output_name': 'not_out'}}
    }
    or_params = {
        'postprocess': {'logic_OR': {'column_name': 'a', 'column_name2': 'b', 'output_name': 'or_out'}}
    }

    and_output = pp.logic_AND(df.copy(), parameters=and_params, section='postprocess', call_num=None)
    not_output = pp.logic_NOT(df.copy(), parameters=not_params, section='postprocess', call_num=None)
    or_output = pp.logic_OR(df.copy(), parameters=or_params, section='postprocess', call_num=None)

    assert and_output['and_out'].tolist() == [False, False]
    assert not_output['not_out'].tolist() == [False, True]
    assert or_output['or_out'].tolist() == [1, 1]


def test_magnitude_computes_vector_length():
    df = pd.DataFrame({'dx': [3, 0], 'dy': [4, 5]})
    parameters = {
        'postprocess': {
            'magnitude': {
                'column_name': 'dx',
                'column_name2': 'dy',
                'output_name': 'r'
            }
        }
    }

    output = pp.magnitude(df.copy(), parameters=parameters, section='postprocess', call_num=None)

    assert np.isclose(output.loc[0, 'r'], 5.0)
    assert np.isclose(output.loc[1, 'r'], 5.0)


def test_neighbours_kdtree_and_delaunay_generate_lists():
    df = pd.DataFrame({
        'particle': [0, 1, 2, 3],
        'x': [0.0, 1.0, 1.0, 0.0],
        'y': [0.0, 0.0, 1.0, 1.0]
    }, index=[0, 0, 0, 0])
    df.index.name = 'frame'

    kt_params = {'postprocess': {'neighbours': {'method': 'kdtree', 'neighbours': 2, 'cutoff': 2.0}}}
    dl_params = {'postprocess': {'neighbours': {'method': 'delaunay', 'cutoff': 2.0}}}

    kdtree_output = pp.neighbours(df.copy(), parameters=kt_params, section='postprocess', call_num=None, f_index=0)
    delaunay_output = pp.neighbours(df.copy(), parameters=dl_params, section='postprocess', call_num=None, f_index=0)

    assert 'neighbours' in kdtree_output.columns
    assert 'neighbour_dists' in kdtree_output.columns
    assert len(kdtree_output.loc[0, 'neighbours']) >= 1
    assert len(delaunay_output.loc[0, 'neighbours']) >= 1


def test_voronoi_adds_voronoi_columns():
    df = pd.DataFrame({
        'x': [0.0, 1.0, 1.0, 0.0],
        'y': [0.0, 0.0, 1.0, 1.0]
    }, index=[0, 0, 0, 0])

    parameters = {
        'postprocess': {
            'voronoi': {}
        }
    }

    output = pp.voronoi(df.copy(), parameters=parameters, section='postprocess', call_num=None, f_index=0)

    assert 'voronoi' in output.columns
    assert 'voronoi_area' in output.columns
    assert len(output['voronoi_area']) == 4


def test_real_imag_splits_complex_values():
    df = pd.DataFrame({'z': [1+1j, -1+2j]})
    parameters = {
        'postprocess': {
            'real_imag': {'column_name': 'z'}
        }
    }

    output = pp.real_imag(df.copy(), parameters=parameters, section='postprocess', call_num=None)

    assert np.array_equal(output['z_re'].tolist(), [1.0, -1.0])
    assert np.array_equal(output['z_im'].tolist(), [1.0, 2.0])


def test_difference_mean_median_and_rate_with_particle_time_series():
    df = pd.DataFrame({'particle': [1, 1, 1], 'x': [1.0, 2.0, 3.0]}, index=[0, 1, 2])
    df.index.name = 'frame'
    base_params = {
        'postprocess': {
            'difference': {'column_name': 'x', 'output_name': 'dx', 'span': 3},
            'mean': {'column_name': 'x', 'output_name': 'x_mean', 'span': 3},
            'median': {'column_name': 'x', 'output_name': 'x_median', 'span': 3},
            'rate': {'column_name': 'x', 'output_name': 'x_rate', 'span': 3, 'fps': 1}
        }
    }

    diff_output = pp.difference(df.copy(), parameters=base_params, section='postprocess', call_num=None)
    mean_output = pp.mean(df.copy(), parameters=base_params, section='postprocess', call_num=None)
    median_output = pp.median(df.copy(), parameters=base_params, section='postprocess', call_num=None)
    rate_output = pp.rate(df.copy(), parameters=base_params, section='postprocess', call_num=None)

    assert np.isnan(diff_output.loc[0, 'dx'])
    assert np.isclose(diff_output.loc[1, 'dx'], 2.0)
    assert np.isnan(diff_output.loc[2, 'dx'])

    assert np.isclose(mean_output.loc[1, 'x_mean'], 2.0)
    assert np.isclose(median_output.loc[1, 'x_median'], 2.0)
    assert np.isclose(rate_output.loc[1, 'x_rate'], 2.0 / 3.0)

