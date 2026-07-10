import numpy as np

from particletracker.general import contour_parsing as cp


import numpy as np
import pandas as pd

def test_reconstruct_contour():
    # 1. Simulate exactly what subset_df[['contours']].values looks like.
    # It's a 2D matrix of shape (M, 1) containing lists.
    flat_contour_data = np.array([
        [[1, 2, 2, 3, 3, 4]]  # One particle row containing a flat list of XY pairs
    ], dtype=object)
    
    # 2. Run your reconstruction function
    new_contour_list = cp.reconstruct_contour_pts(flat_contour_data)
    
    # 3. Create the exact expected OpenCV contour structure for this particle.
    # It must be a list containing an array of shape (N, 1, 2), dtype=int32
    expected_contour = np.array([
        [[1, 2]],
        [[2, 3]],
        [[3, 4]]
    ], dtype=np.int32)
    
    # 4. Assertions
    assert len(new_contour_list) == 1
    assert new_contour_list[0].shape == (3, 1, 2)
    assert new_contour_list[0].dtype == np.int32
    
    # Use np.testing to compare element-wise safely
    assert(new_contour_list[0], expected_contour)