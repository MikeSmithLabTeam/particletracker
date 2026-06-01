import cv2
import numpy as np
import pandas as pd

from particletracker.annotate import annotation_methods as am


def test_text_label_draws_text():
    frame = np.zeros((50, 150, 3), dtype=np.uint8)
    parameters = {
        'annotation': {
            'text_label': {
                'text': 'test',
                'position': (5, 15),
                'font_colour': (255, 255, 255),
                'font_size': 1,
                'font_thickness': 1,
            }
        }
    }

    output = am.text_label(None, frame.copy(), f_index=0, parameters=parameters, section='annotation', call_num=None)

    assert output.shape == frame.shape
    assert np.any(output != frame)


def test_var_label_displays_frame_specific_value():
    frame = np.zeros((50, 150, 3), dtype=np.uint8)
    df = pd.DataFrame(
        {'temp': [22, 22], 'x': [10, 20], 'y': [10, 20]},
        index=[0, 0],
    )
    parameters = {
        'annotation': {
            'var_label': {
                'var_column': 'temp',
                'position': (5, 15),
                'font_colour': (255, 255, 255),
                'font_size': 1,
                'font_thickness': 1,
            }
        }
    }

    output = am.var_label(df, frame.copy(), f_index=0, parameters=parameters, section='annotation', call_num=None)

    assert np.any(output != frame)


def test_particle_labels_returns_frame_when_values_are_nan():
    frame = np.zeros((50, 150, 3), dtype=np.uint8)
    df = pd.DataFrame(
        {'x': [10.0, 20.0], 'y': [10.0, 20.0], 'label': [np.nan, np.nan]},
        index=[0, 0],
    )
    parameters = {
        'annotation': {
            'particle_labels': {
                'values_column': 'label',
                'font_colour': (255, 255, 255),
                'font_size': 1,
                'font_thickness': 1,
            }
        }
    }

    output = am.particle_labels(df, frame.copy(), f_index=0, parameters=parameters, section='annotation', call_num=None)
    assert np.array_equal(output, frame)


def test_boxes_draws_rotated_box_for_static_color():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    box_pts = np.array([[[10, 10], [10, 20], [20, 20], [20, 10]]], dtype=np.int32)
    df = pd.DataFrame(
        {'box_pts': [box_pts], 'x': [10], 'y': [10]},
        index=[0, 0],
    )
    parameters = {
        'annotation': {
            'boxes': {
                'classifier_column': None,
                'colour': (0, 255, 0),
                'cmap_type': 'static',
                'thickness': 1,
            }
        }
    }

    output = am.boxes(df, frame.copy(), f_index=0, parameters=parameters, section='annotation', call_num=None)
    assert np.any(output != frame)


def test_circles_draws_circles_with_user_radius():
    frame = np.zeros((80, 80, 3), dtype=np.uint8)
    df = pd.DataFrame(
        {'x': [40.0, 20.0], 'y': [40.0, 20.0]},
        index=[0, 0],
    )
    parameters = {
        'annotation': {
            'circles': {
                'xdata_column': 'x',
                'ydata_column': 'y',
                'rdata_column': 'r',
                'rad_from_data': False,
                'user_rad': 10,
                'cmap_type': 'static',
                'colour': (255, 0, 0),
                'classifier_column': None,
                'thickness': 2,
            }
        }
    }

    output = am.circles(df, frame.copy(), f_index=0, parameters=parameters, section='annotation', call_num=None)
    assert np.any(output != frame)


def test_contours_draws_contours_for_static_color():
    frame = np.zeros((80, 80, 3), dtype=np.uint8)
    contour = np.array([[[10, 10]], [[20, 10]], [[20, 20]], [[10, 20]]], dtype=np.int32)
    df = pd.DataFrame(
        {'contours': [contour], 'x': [10], 'y': [10]},
        index=[0, 0],
    )
    parameters = {
        'annotation': {
            'contours': {
                'cmap_type': 'static',
                'colour': (0, 0, 255),
                'thickness': 1,
                'classifier_column': None,
            }
        }
    }

    output = am.contours(df, frame.copy(), f_index=0, parameters=parameters, section='annotation', call_num=None)
    assert np.any(output != frame)


def test_networks_draw_lines_between_neighbours():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    df = pd.DataFrame(
        {'x': [10.0, 20.0], 'y': [10.0, 20.0], 'particle': [0, 1], 'neighbours': [[1], [0]]},
        index=[0, 0],
    )
    parameters = {
        'annotation': {
            'networks': {
                'classifier_column': None,
                'cmap_type': 'static',
                'colour': (255, 255, 0),
                'thickness': 1,
            }
        }
    }

    output = am.networks(df, frame.copy(), f_index=0, parameters=parameters, section='annotation', call_num=None)
    assert np.any(output != frame)


def test_voronoi_draws_polygons_when_voronoi_defined():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    poly = np.array([[10, 10], [20, 10], [20, 20], [10, 20]], dtype=np.float32)
    df = pd.DataFrame(
        {'voronoi': [poly], 'x': [10], 'y': [10]},
        index=[0, 0],
    )
    parameters = {
        'annotation': {
            'voronoi': {
                'classifier_column': None,
                'cmap_type': 'static',
                'colour': (0, 255, 255),
                'thickness': 1,
            }
        }
    }

    output = am.voronoi(df, frame.copy(), f_index=0, parameters=parameters, section='annotation', call_num=None)
    assert np.any(output != frame)


def test_vectors_draw_arrows_for_each_particle():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    df = pd.DataFrame(
        {'x': [10.0, 20.0], 'y': [10.0, 20.0], 'dx': [10.0, -5.0], 'dy': [0.0, 5.0]},
        index=[0, 0],
    )
    parameters = {
        'annotation': {
            'vectors': {
                'dx_column': 'dx',
                'dy_column': 'dy',
                'vector_scale': 10,
                'tip_length': 10,
                'line_type': 8,
                'thickness': 1,
                'cmap_type': 'static',
                'colour': (0, 128, 255),
            }
        }
    }

    output = am.vectors(df, frame.copy(), f_index=0, parameters=parameters, section='annotation', call_num=None)
    assert np.any(output != frame)


def test_trajectories_draws_paths_for_recent_frames():
    frame = np.zeros((80, 80, 3), dtype=np.uint8)
    df = pd.DataFrame(
        {
            'x': [10.0, 11.0, 12.0, 13.0, 14.0, 15.0],
            'y': [10.0, 11.0, 12.0, 13.0, 14.0, 15.0],
            'particle': [0, 0, 0, 0, 0, 0],
        },
        index=[0, 0, 1, 1, 2, 2],
    )
    parameters = {
        'annotation': {
            'trajectories': {
                'x_column': 'x',
                'y_column': 'y',
                'classifier_column': None,
                'span': 2,
                'thickness': 1,
                'cmap_type': 'static',
                'colour': (255, 255, 255),
            }
        }
    }

    output = am.trajectories(df, frame.copy(), f_index=2, parameters=parameters, section='annotation', call_num=None)
    assert np.any(output != frame)
