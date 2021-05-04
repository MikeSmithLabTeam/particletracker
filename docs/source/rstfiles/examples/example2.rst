.. _Example2:

Example 2 - Diffusing colloids with trackpy
===========================================

In this example we are going to use an existing python based particle tracking code known as trackpy. 
The details of this project can be found here (http://soft-matter.github.io/trackpy/v0.4.2/). Although
there are other feature finding (tracking) algorithms in this software the trackpy project is 
used in linking these features for all the different algorithms. You should therefore cite this project
in any publications regardless of whether you used the trackpy "track" algorithm.

This example tracks the motion of some 500nm colloids in water, viewed using a brightfield microscope.
We have set up a few of the steps in this example for you in the colloids.param file. This file
contains all the settings used. Rather than explain the mechanics of setting up the steps as we did in 
the first example, we will just describe what each method is doing.

Load the colloids.mp4 video file together with the colloids.param settings file. Upon loading
everything you should see a tracked frame like the one shown below.

.. figure:: /resources/colloids1.png
    :width: 400
    :align: center

To achieve this we have taken a number of steps. Trackpy is ideal for "blob" finding in images. Although
it can work purely on a grayscale image, we find that it is often helpful to enhance the images first
to make the tracking more reliable. We have applied the following steps in the preprocessing
of the image:

- grayscale
- blur
- absolute_diff
- threshold

Most of these steps are pretty self-explanatory. The blur softens the image and reduces the noise which
can affect tracking. The absolute_diff is a very useful method particularly for microscopy images.
It simply returns the absolute difference between a pixels intensity and a reference value set by the user.
In microscopy (as here) objects below the image plane often appear dark whilst those above it often appear 
bright. Using the absolute diff enables one to see all the objects as bright features (below left). To see the output
move the threshold method below inactive temporarily and toggle the "Capture Image" button below the viewer. Now move the threshold method back.
Having done that we take a global threshold setting all pixels brighter than a threshold value to 255 and those
dimmer to 0. If you again toggle the image you'll see white particles on a completely black background (below right).

.. figure:: /resources/colloids2.png
    :width: 500
    :align: center

Next we selected trackpy in the Track tab and adjusted the size estimate for the features to approximately the 
correct size. We also selected the circles in the annotation section so that we can immediately see how different parameters affect the tracking.
A usual workflow involves assessing iteratively how different factors in the preprocessing and tracking influence
the fidelity of the final tracking. For applications like this where we will use linking it is not a problem if one detects
the odd extra spurious particle. The reason for this is that when we come to link
the positions in different frames together those spurious particles will not consistently show up whereas real particles
should. Consequently, we can filter these spurious particles out.

Linking particles is a critical step if you are interested in the motion of particles. It enables
you to assign the same particle in different frames an id so that you can calculate things such 
as particle displacements as a function of time. Linking contains a few different parameters:

-   max_frame_displacement  :
    how far a particle can move between individual frames. Make this number too big and the software
    won't be able to choose which particle is connected to which. Make it too small and many of the 
    particle trajectories will be artificially terminated when a particle makes a genuine large displacement.
-   memory  :
    how many frames a particle can be undetected and still be considered the same particle. It is usually wise
    to keep this number small.
-   min_frame_life  :   
    this filters any really short trajectories from the data. Spurious particles might get tracked for a couple of
    frames so by setting this value to 3 you'd remove those. However, as this number gets larger you will
    also start to lose genuine particles that moved in and out of the focus fairly quickly.

With all these parameters one has to try and find a good balance. A good way to go about this
is to process small sections of the video and then observe the output to assess whether the results are
sensible. Once you are happy you can process the full video. To shorten the video we can click on the settings cog next to the frame selection tool below the viewer.
Enter min = 0, max = 30, step = 1. To enable us to see whether the trajectories are continuous we add both particle labels (this simply displays the particle id near each particle)
and the particle trajectories (which plots the historical positions of each particle). Click "Process".

Processing produces a number of files of format <moviename>_ending.extension . Navigate to the folder containing the testdata and you should find:
- colloids.hdf5 which contains all the tracking data for all the processed frames.
- colloids_temp.hdf5 this is a file that is used internally by the software. You can safely delete this file.
- colloids_annotate.mp4 is an annotated video.
- colloids_expt.param a file containing the setting used in processing

Open colloids_annotate.mp4 in a video player (eg VLC - https://www.videolan.org/vlc/download-windows.en-GB.html).
Watching this back enables us to quickly assess whether the tracking is working as expected. This is particularly
the case for assessing if linking is working properly. If the objects being tracked are 
visually not disappearing and appearing in the frame and the particle numbers are increasing quickly
then this means that your particles are not being linked successfully in each frame. A common
reason is that your max_frame_displacement is too small. It is also
possible that the software is erroneously linking different particles together. This can happen if the 
tracking of objects is not reliable in every frame and the max_frame_displacement is too large.
Apart from improving the tracking you can also improve this by increasing the memory a little.
If your particles being tracked do not link one frame to another and you just want their positions
it is important that you set min_frame_life = 1. This parameter filters out trajectories that 
are shorter than min_frame_life.

Once you are happy that everything is working as expected you can return to the gui.
To make sure you now process the entire movie click "Reset frame range". Reprocessing the video
will overwrite without warning the files described above. We often process with annotation the video
to check the tracking works well for the whole video. We also keep the colloids.hdf5 file and colloids_expt.param
file together. This leaves a permanent record of the exact way in which the data was processed.
This is useful if you ever need to check this but it also enables you to use this .param file
in future to process other data with the same settings. This can be done either by loading this 
settings file in the gui or supplying it as a keyword argument in the python track_gui.

framedata
---------

Sometimes it might be useful to add information about each frame. For example the
temperature of the sample might be changing. Whilst this is relatively simple to do using python 
we have also added the ability to upload a simplecsv file to a column. This file should have 
a single column with one row of data per frame in the video. 

Select "add_frame_data" in the postprocessing tab. Specify a column name for the new data. We use "temp". Then 
specify the filename with extension containing the data. The software assumes the file
is in the same folder as the video and sets this filepath. If you want it to look somewhere
else you can specify this in the data_path field. In the testdata we have created a file "framedata.csv"
type this in to the data_filename.

To display the temperature we need a "text label" to place static text on the image and a "var label" to represent
data that is specific to a single frame. Both of these can be added in the annotation section.
We add the following settings to the text label: text: "T=", position: (10,40), font_size: 2, font_thickness: 2, font_colour: (0,0,255). We then
add the following settings to var_label: var_column : temp, position: (80,40), font_size: 2, font_thickness: 2, font_colour: (0,0,255). 

:ref:`Example 3 <Example3>` 
