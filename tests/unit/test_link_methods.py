import numpy as np
import pandas as pd

from particletracker.link import link_methods as lm


def test_no_linking_assigns_sequential_particle_ids():
    df = pd.DataFrame({'x': [10, 20, 30], 'y': [10, 20, 30]})

    output = lm.no_linking(df.copy())

    assert 'particle' in output.columns
    assert list(output['particle']) == [0, 1, 2]
    assert output.shape[0] == 3


def test_default_links_sequences_and_drops_frame_column():
    df = pd.DataFrame({'frame': [0, 0, 1, 1], 'x': [10, 12, 10, 12], 'y': [10, 10, 12, 12]})
    parameters = {
        'max_frame_displacement': [15],
        'memory': [0],
        'min_frame_life': [1]
    }

    output = lm.default(df.copy(), parameters)

    assert 'frame' not in output.columns
    assert 'particle' in output.columns
    assert output['particle'].nunique() == 2
    assert output.shape[0] == 4


def test_default_handles_scalar_parameters():
    df = pd.DataFrame({'frame': [0, 1], 'x': [10, 10], 'y': [10, 11]})
    parameters = {
        'max_frame_displacement': 5,
        'memory': 0,
        'min_frame_life': 1
    }

    output = lm.default(df.copy(), parameters)

    assert output.shape[0] == 2
    assert 'particle' in output.columns


def test_no_linking_preserves_other_columns():
    df = pd.DataFrame({'x': [5, 6], 'y': [7, 8], 'mass': [1.2, 2.3]})

    output = lm.no_linking(df.copy())

    assert 'mass' in output.columns
    assert list(output['particle']) == [0, 1]
