import numpy as np
import cv2

from filehandling import BatchProcess

from particletracker.crop import ReadCropVideo

def create_bkg_img(parameters=None, filename=None):
    """Create a background image based on an average of the video

    Notes
    -----

    If you want to use subtract_bkg methods with
    the  parameters['subtract bkg type'] == 'image' option, you need to
    create a bkg image first. You can create one separately but this
    function can be used if you have lots of movement of a small number
    of objects. It simply averages all the frames together. The file
    is saved as filename_bkgimg.png

    Examples
    --------
    for file in BatchProcess('Example**.mp4'):
        create_bkg_img(parameters=PARAMETERS['crop'], filename=file)



    Parameters
    ----------

    filename:
        filename of the video


    """
    readvid = ReadCropVideo(parameters=PARAMETERS, filename=filename)
    frame_init = readvid.read_next_frame()  # .astype(np.int32)
    counter = 1
    sz = np.shape(frame_init)
    frame_assemble = np.reshape(frame_init, (sz[0], sz[1] * sz[2]))

    for i in range(readvid.num_frames - 1):
        frame = readvid.read_next_frame().astype(np.int32)
        new_frame = np.reshape(frame, (sz[0], sz[1] * sz[2]))
        frame_assemble = np.sum((frame_assemble, new_frame), axis=0,
                                dtype=np.int32)
        counter = counter + 1
    frame = (frame_assemble / counter).astype(np.uint8)
    frame_assemble = np.reshape(frame, (sz[0], sz[1], sz[2]))
    cv2.imwrite(file[:-4] + '_bkgimg.png', frame_assemble)

    readvid.close()

