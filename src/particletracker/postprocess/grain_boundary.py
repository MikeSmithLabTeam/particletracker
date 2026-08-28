
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def largest_filled_object(binary_img: np.ndarray, kernel_size=11) -> np.ndarray:
    """Return a binary mask containing only the largest thresholded object."""
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    binary_img = cv2.dilate(binary_img, kernel, iterations=1)

    count, labels, statistics, _ = cv2.connectedComponentsWithStats(
        binary_img, connectivity=8
    )

    largest_label = 1 + int(np.argmax(statistics[1:, cv2.CC_STAT_AREA]))
    object_mask = np.where(labels == largest_label, 255, 0).astype(np.uint8)

    contours, _ = cv2.findContours(
        object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    filled = np.zeros_like(object_mask)
    cv2.drawContours(filled, contours, -1, 255, thickness=cv2.FILLED)
    return filled

def construct_mask(
    df: pd.DataFrame,
    frame_size,
    dilate_rad
) -> np.ndarray:
    """Create individual masks for red, green, and blue crystals using explicit

    color range bounds after applying a central circular mask.
    """
    combined_mask = df["condition_1"] & df["condition_2"]
    filtered_df = df[combined_mask]
    
    # Extract coordinates into a Nx2 numpy array of integers
    points = filtered_df[["x", "y"]].to_numpy(dtype=np.int32)
    radii = filtered_df[["r"]].to_numpy(dtype=np.int32) + dilate_rad

    # Create a blank mask with the same dimensions as the original image
    mask = np.zeros(frame_size[:2], dtype=np.uint8)

    # Draw a filled white circle (255) for each particle coordinate
    for i,pt in enumerate(points):
        cv2.circle(mask, tuple(pt), radius=radii[i], color=255, thickness=-1)
    
    inverted_mask = cv2.bitwise_not(mask)
    return inverted_mask

def extract_centerlines_via_skeleton(
    mask: np.ndarray,
) -> tuple[list[tuple], list[tuple], list[tuple]]:
    """Extracts centerlines via raw skeletonization without pruning."""
    

    # Direct raw skeletonization (no pruning loop)
    raw_skeleton = cv2.ximgproc.thinning(
        mask, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN
    )

    contours, _ = cv2.findContours(
        raw_skeleton, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE
    )

    centerlines = []
    for cnt in contours:
        if len(cnt) > 15:
            pts = [(float(p[0][0]), float(p[0][1])) for p in cnt]
            centerlines.append(pts)
    
    # Sort centerlines based on the average x-coordinate of their points (furthest left first)
    centerlines.sort(key=lambda cl: sum(p[0] for p in cl) / len(cl))

    cl_r = centerlines[0] if len(centerlines) > 0 else []
    cl_g = centerlines[1] if len(centerlines) > 1 else []
    cl_b = centerlines[2] if len(centerlines) > 2 else []

    return cl_r, cl_g, cl_b

def find_grain_boundaries(cl_r, cl_g, cl_b) -> tuple[list[tuple], list[tuple], list[tuple]]:
    # Convert to sets of rounded tuples ONLY for O(1) lookup speeds
    set_r = {(round(p[0]), round(p[1])) for p in cl_r}
    set_g = {(round(p[0]), round(p[1])) for p in cl_g}
    set_b = {(round(p[0]), round(p[1])) for p in cl_b}

    # Filter original ordered lists based on set membership
    gb_rg = [p for p in cl_r if (round(p[0]), round(p[1])) in set_g]
    gb_gb = [p for p in cl_g if (round(p[0]), round(p[1])) in set_b]
    gb_br = [p for p in cl_b if (round(p[0]), round(p[1])) in set_r]

    return gb_rg, gb_gb, gb_br

def find_triple_junction(cl_r, cl_g, cl_b):
    """Fast triple junction localization via set intersections and vectorized numpy logic."""
    set_rg = set((round(p[0]), round(p[1])) for p in cl_r)
    set_gb = set((round(p[0]), round(p[1])) for p in cl_g)
    set_br = set((round(p[0]), round(p[1])) for p in cl_b)

    common_pts = set_rg.intersection(set_gb).intersection(set_br)

    #I think there must always only be one common_pt which makes rest of this bit superfluous but keep for now.

    if common_pts:
        pts_arr = np.array(list(common_pts))
        return (float(np.mean(pts_arr[:, 0])), float(np.mean(pts_arr[:, 1])))

    # Vectorized NumPy fallback for closest convergence point
    arr_r = np.array(cl_r) if cl_r else np.empty((0, 2))
    arr_g = np.array(cl_g) if cl_g else np.empty((0, 2))
    arr_b = np.array(cl_b) if cl_b else np.empty((0, 2))

    if len(arr_r) > 0 and len(arr_g) > 0 and len(arr_b) > 0:
        all_pts = np.vstack([arr_r, arr_g, arr_b])
        centroid = np.mean(all_pts, axis=0)

    candidates = []
    for cl in [arr_r, arr_g, arr_b]:
        dists_sq = np.sum((cl - centroid) ** 2, axis=1)
        mask = dists_sq < 100**2
        if np.any(mask):
            candidates.append(cl[mask])

        if candidates:
            pool = np.vstack(candidates)
            d_rg = np.min(
                np.sum((arr_r[:, None, :] - pool[None, :, :]) ** 2, axis=2), axis=0
            )
            d_gb = np.min(
                np.sum((arr_g[:, None, :] - pool[None, :, :]) ** 2, axis=2), axis=0
            )
            d_br = np.min(
                np.sum((arr_b[:, None, :] - pool[None, :, :]) ** 2, axis=2), axis=0
            )

            scores = d_rg + d_gb + d_br
            best_idx = np.argmin(scores)
            return (float(pool[best_idx, 0]), float(pool[best_idx, 1]))

    return (0.0, 0.0)
