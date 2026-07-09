import numpy as np
import pandas as pd

def flatten_contours(contours):
    """
    Converts OpenCV contours into flat, Parquet-safe formats.
    Returns two lists: one with the flattened XY coordinates,
    and one with the original point counts so we can slice them back.
    """
    flattened_data = []
    point_counts = []
    
    for cnt in contours:
        # cnt shape is (N, 1, 2) -> flatten to 1D array [x1, y1, x2, y2...]
        flat_cnt = cnt.flatten()
        flattened_data.append(flat_cnt.tolist())
        point_counts.append(len(cnt)) # Number of N points
        
    return flattened_data, point_counts


def reconstruct_contours(flattened_data, point_counts):
    """
    Rebuilds the original nested list of OpenCV (N, 1, 2) int32 arrays
    from the flattened Parquet lists. Ready for cv2.drawContours.
    """
    reconstructed = []
    
    for flat_cnt, count in zip(flattened_data, point_counts):
        # Convert back to a numpy array, shape it to (N, 1, 2), and enforce int32
        cnt_array = np.array(flat_cnt, dtype=np.int32).reshape(count, 1, 2)
        reconstructed.append(cnt_array)
        
    return reconstructed