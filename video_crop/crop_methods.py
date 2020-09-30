import numpy as np
from ParticleTracker.video_crop.crop_box_gui import ROIfigure


def crop_box(frame, crop_coords=None):
    if crop_coords is None:
        crop=ROIfigure(frame, coords=crop_coords)
        crop_coords = crop.coords

    cropped_frame = frame[crop_coords[1]:crop_coords[1]+crop_coords[3], crop_coords[0]:crop_coords[0]+crop_coords[2],:]
    mask_img = np.ones(np.shape(frame))
    return cropped_frame, mask_img, crop_coords

