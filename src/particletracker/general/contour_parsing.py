import numpy as np

def reconstruct_contour_pts(df_contour_values):
    """
    Reconstructs the original list of OpenCV contour arrays from a 
    DataFrame values matrix.
    
    Args:
        df_contour_values: The numpy array from `df[['contours']].values`
        
    Returns:
        A list of numpy arrays, each with shape (N, 1, 2), matching 
        the original contour_pts structure.
    """
    reconstructed_pts = []
    
    # df_contour_values is a 2D array of shape (M, 1), so we extract row[0]
    for row in df_contour_values:
        flat_list = row[0]
        
        # Convert the list back to an int32 numpy array and shape to (N, 1, 2)
        contour_array = np.array(flat_list, dtype=np.int32).reshape(-1, 1, 2)
        reconstructed_pts.append(contour_array)
        
    return reconstructed_pts

def reconstruct_box_pts(df_box_values):
    """
    Reconstructs the original list of OpenCV box corner arrays from a 
    DataFrame values matrix.
    
    Args:
        df_box_values: The numpy array from `df[['box_pts']].values`
        
    Returns:
        A list of numpy arrays, each with shape (4, 2), ready for cv2.drawContours 
        or cv2.polylines annotation.
    """
    reconstructed_boxes = []
    
    for row in df_box_values:
        flat_box = row[0]
        
        # Turn the 8-element list back into a proper (4, 2) array for OpenCV
        # Cast to int32 if you intend to pass directly to cv2.drawContours
        box_array = np.array(flat_box, dtype=np.int32).reshape(4, 2)
        reconstructed_boxes.append(box_array)
        
    return reconstructed_boxes

def reconstruct_voronoi_pts(df_voronoi_values, df_counts_values):
    """
    Reconstructs the original list of 2D Voronoi cell arrays from 
    flattened DataFrame columns.
    
    Args:
        df_voronoi_values: Matrix from df[['voronoi']].values (shape (M, 1))
        df_counts_values: Matrix from df[['voronoi_counts']].values (shape (M, 1))
        
    Returns:
        A list of numpy arrays of shape (V, 2) or None for infinite/boundary cells.
    """
    reconstructed_cells = []
    
    for row_coord, row_count in zip(df_voronoi_values, df_counts_values):
        flat_list = row_coord[0]
        v_count = row_count[0]
        
        # If count is 0, it was a boundary cell (infinite)
        if v_count == 0 or len(flat_list) == 0:
            reconstructed_cells.append(None)
        else:
            # Reshape back to (V, 2)
            # Use np.int32 if drawing with OpenCV, or float64 if doing pure math
            cell_array = np.array(flat_list, dtype=np.int32).reshape(v_count, 2)
            reconstructed_cells.append(cell_array)
            
    return reconstructed_cells