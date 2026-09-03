
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def mask_polygon(frame_size, pt_list, dilation_rad):
    mask = 255*np.ones(frame_size[:2], dtype=np.uint8)

    if pt_list is not None:
        poly = np.array([[p[0], p[1]] for p in pt_list], dtype=np.int32)
        cv2.fillPoly(mask, [poly],  0)
        
        # Shrink the white polygon region
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilation_rad, dilation_rad))
        mask = cv2.dilate(mask, kernel, iterations=3)
        
    return mask

# Create mask of white crystal on black bkg
def crystal_mask(filtered_df, frame_size, dilate_rad):
    mask = np.zeros(frame_size[:2], dtype=np.uint8)
    
    points = filtered_df[["x", "y"]].to_numpy(dtype=np.int32)
    radii = filtered_df[["r"]].to_numpy(dtype=np.int32) + 3*dilate_rad
    
    for i,pt in enumerate(points):
            cv2.circle(mask, tuple(pt), radius=int(radii[i][0]), color=255, thickness=-1)
    return mask
    

def construct_mask(
    df: pd.DataFrame,
    frame_size,
    dilate_rad
) -> np.ndarray:
    """Create individual masks for red, green, and blue crystals using explicit

    color range bounds after applying a central circular mask.
    """
    filtered_df_r = df[df['crystal_id'] == 0]  
    filtered_df_g = df[df['crystal_id'] == 1] 
    filtered_df_b = df[df['crystal_id'] == 2] 
    
    # Extract coordinates into a Nx2 numpy array of integers
    mask_r = crystal_mask(filtered_df_r, frame_size, dilate_rad)
    mask_g = crystal_mask(filtered_df_g, frame_size, dilate_rad)
    mask_b = crystal_mask(filtered_df_b, frame_size, dilate_rad)
    
    rg = cv2.multiply(mask_r, mask_g)
    gb = cv2.multiply(mask_g, mask_b)
    br = cv2.multiply(mask_b, mask_r)
    
    
    return (rg, gb, br)

def extract_gb(mask):
    raw_skeleton = cv2.ximgproc.thinning(
        mask.astype(np.uint8), 
        thinningType=cv2.ximgproc.THINNING_ZHANGSUEN
    )
    
    contours, _ = cv2.findContours(
        raw_skeleton, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE
    )

    # Find the single longest contour
    longest_cnt = max(contours, key=len)
    
    # Map directly to a float coordinate list
    centerline = [(float(p[0][0]), float(p[0][1])) for p in longest_cnt]
    
    return centerline

def find_grain_boundaries(
    masks: tuple(np.ndarray, np.ndarray, np.ndarray)
) -> tuple[list[tuple], list[tuple], list[tuple]]:
    """Extracts centerlines via raw skeletonization without pruning."""
    rg, gb, br = masks

    gb_rg = extract_gb(rg)
    gb_gb = extract_gb(gb)
    gb_br = extract_gb(br)

    return (gb_rg, gb_gb, gb_br)


def find_triple_junction(gbs):
    """Finds the triple junction by locating the point that minimizes the 
    combined squared distance to all three distinct grain boundary centre lines.
    """
    gb_rg, gb_gb, gb_br = gbs

    arr_rg = np.array(gb_rg) if gb_rg else np.empty((0, 2))
    arr_gb = np.array(gb_gb) if gb_gb else np.empty((0, 2))
    arr_br = np.array(gb_br) if gb_br else np.empty((0, 2))

    if len(arr_rg) == 0 or len(arr_gb) == 0 or len(arr_br) == 0:
        return (0.0, 0.0)

    # Use the mean centroid of all lines as a robust initial search anchor
    all_pts = np.vstack([arr_rg, arr_gb, arr_br])
    anchor = np.mean(all_pts, axis=0)

    # Collect points from each boundary within a local radius of the anchor
    candidates = []
    for arr in [arr_rg, arr_gb, arr_br]:
        dists_sq = np.sum((arr - anchor) ** 2, axis=1)
        mask = dists_sq < 150**2
        if np.any(mask):
            candidates.append(arr[mask])
        else:
            candidates.append(arr)  # Fallback to full array if local mask is empty

    pool = np.vstack(candidates)

    # For every point in the local pool, compute its distance squared to each of the three legs
    d_rg = np.min(np.sum((arr_rg[:, None, :] - pool[None, :, :]) ** 2, axis=2), axis=0)
    d_gb = np.min(np.sum((arr_gb[:, None, :] - pool[None, :, :]) ** 2, axis=2), axis=0)
    d_br = np.min(np.sum((arr_br[:, None, :] - pool[None, :, :]) ** 2, axis=2), axis=0)

    # The triple junction is the candidate point that minimises the sum of squared distances to all 3 paths
    scores = d_rg + d_gb + d_br
    best_idx = np.argmin(scores)

    return (float(pool[best_idx, 0]), float(pool[best_idx, 1]))
