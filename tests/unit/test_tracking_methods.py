import cv2
import numpy as np
import pandas as pd
import pytest

from particletracker.track import tracking_methods as tm


def test_create_circular_mask_defaults_centered():
    mask = tm._create_circular_mask(7, 7)
    assert mask.shape == (7, 7)
    assert mask[3, 3]
    assert not mask[0, 0]


def test_find_contours_returns_single_contour():
    img = np.zeros((40, 40), dtype=np.uint8)
    cv2.rectangle(img, (10, 10), (30, 30), 255, -1)

    contours = tm._find_contours(img)
    assert len(contours) == 1
    assert contours[0].ndim == 3


def test_draw_contours_fills_bitmap():
    img = np.zeros((40, 40, 3), dtype=np.uint8)
    contour = np.array([[[10, 10]], [[10, 30]], [[30, 30]], [[30, 10]]])

    result = tm._draw_contours(img.copy(), contour, col=(255, 255, 255), thickness=-1)
    assert result[..., 0].sum() > 0
    assert result[..., 1].sum() > 0
    assert result[..., 2].sum() > 0


def test_contour_from_mask_rectangle_and_point_inside():
    contour = tm._contour_from_mask([(10, 10), (20, 20)], 'mask_rectangle')
    assert isinstance(contour, list)
    assert contour[0].shape == (4, 2)

    inside = tm._point_inside_mask((15, 15), [contour])
    outside = tm._point_inside_mask((5, 5), [contour])
    assert inside is True
    assert outside is False


def test_contours_finds_single_region_without_intensity():
    ppframe = np.zeros((80, 80), dtype=np.uint8)
    cv2.circle(ppframe, (40, 40), 10, 255, -1)
    frame = np.zeros((80, 80, 3), dtype=np.uint8)
    frame[40, 40] = (100, 100, 100)

    parameters = {
        'track': {
            'contours': {
                'area_min': 0,
                'area_max': 10000,
                'aspect_min': 0.1,
                'aspect_max': 10,
                'get_intensities': False,
            }
        }
    }

    df = tm.contours(ppframe, frame, parameters=parameters)
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] >= 1
    assert set(df.columns) == {'x', 'y', 'area', 'contours'}


def test_contours_can_compute_intensity_inside_contour():
    ppframe = np.zeros((80, 80), dtype=np.uint8)
    cv2.circle(ppframe, (40, 40), 10, 255, -1)
    frame = np.zeros((80, 80, 3), dtype=np.uint8)
    frame[30:51, 30:51] = (50, 50, 50)

    parameters = {
        'track': {
            'contours': {
                'area_min': 0,
                'area_max': 10000,
                'aspect_min': 0.1,
                'aspect_max': 10,
                'get_intensities': 'mean_intensity',
            }
        }
    }

    df = tm.contours(ppframe, frame, parameters=parameters)
    assert 'intensities' in df.columns
    assert df['intensities'].notna().all()


def test_hough_detects_circle():
    ppframe = np.zeros((120, 120), dtype=np.uint8)
    cv2.circle(ppframe, (60, 60), 20, 255, 2)
    frame = np.dstack([ppframe] * 3)

    parameters = {
        'track': {
            'hough': {
                'min_dist': 30,
                'p1': 50,
                'p2': 20,
                'min_rad': 15,
                'max_rad': 25,
                'remove_masked': False,
                'get_intensities': False,
            }
        },
        'crop': {'crop_method': ['crop_box']}
    }

    df = tm.hough(ppframe, frame, params=parameters)
    assert isinstance(df, pd.DataFrame)
    assert 'x' in df.columns
    assert df['x'].notna().all()


def test_hough_can_add_intensities():
    ppframe = np.zeros((120, 120), dtype=np.uint8)
    cv2.circle(ppframe, (60, 60), 20, 255, 2)
    frame = np.dstack([ppframe] * 3)

    parameters = {
        'track': {
            'hough': {
                'min_dist': 30,
                'p1': 50,
                'p2': 20,
                'min_rad': 15,
                'max_rad': 25,
                'remove_masked': False,
                'get_intensities': 'mean_intensity',
            }
        },
        'crop': {'crop_method': ['crop_box']}
    }

    df = tm.hough(ppframe, frame, params=parameters)
    assert 'intensities' in df.columns
    assert df['intensities'].shape[0] == df.shape[0]


def test_trackpy_locates_a_bright_blob():
    ppframe = np.zeros((80, 80), dtype=np.uint8)
    cv2.circle(ppframe, (40, 40), 6, 255, -1)
    frame = np.dstack([ppframe] * 3)

    parameters = {
        'track': {
            'trackpy': {
                'diameter': 13,
                'minmass': 10,
                'percentile': 1,
                'invert': False,
                'max_iterations': 10,
                'get_intensities': False,
            }
        }
    }

    df = tm.trackpy(ppframe, frame, params=parameters)
    assert isinstance(df, pd.DataFrame)
    assert 'x' in df.columns
    assert 'y' in df.columns
    assert df.shape[0] >= 1
