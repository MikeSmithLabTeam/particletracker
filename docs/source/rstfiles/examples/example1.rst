.. _Example1:

Example 1 - Eye tracking
========================

In this first example we are going to do some eye tracking using the hough tracking method. We will describe 
this simple example in quite a lot of detail. Later examples will build on each other so 
it may be worth doing this even if you think you are unlikely to want to track eyes or even use the Hough Circles algorithm. 

.. figure:: /resources/eyes1.png
    :width: 400
    :align: center


If you are unsure how to start the software read the description in :ref:`How do you start?<Start>`  
Load up the video eyes.mp4 from the testdata folder and try the following steps.

1. Crop and mask the image  - we are not interested in the area outside the person's eyes.
    To do this we select the crop tab. At the bottom right hand side to the page we check
    the checbox next to crop. We then click hold and drag to create a rectangle around the eyes.
    We then uncheck the same checkbox and the image updates to the selected region. We can improve
    things a bit more by masking the image to leave only the eyes. To do this from the drop
    down list on the right select mask_rectangle and push the button "Add method" twice. Drag
    and drop the mask_rectangle and mask_rectangle*1 above the ----inactive---- place holder.
    For each tool select its checkbox and drag the the mask around each eye before unchecking each box.
    You can adjust each mask by simply rechecking the checkbox and moving the handles. Check
    the final image by pushing the button below the image labelled captured image. This
    shows you the preprocessed image upon which tracking is performed. Once happy push the button
    again.

.. figure:: /resources/eyes2.png
    :width: 400
    :align: center

2. Add a blur to the preprocessed image. 
    Select the preprocess tab. We currently have grayscale and medianblur selected. We don't
    need the medianblur so rightclick on this to remove it. Then from the drop down menu select 
    blur and "Add method". Drag to active. Then in the parameter selector section (bottom right) move the slider of the
    "kernel" to 3. It is often helpful to blur images prior to tracking
    as it helps reduce noise or gradients in the image. 

3. Select the hough tracking method
    Select the track tab. Select hough, add it. It is only possible to run a single type of tracking
    method so in this case there is no inactive status. Hough circles is a tracking method that
    looks for circles in images. It has a few different parameters most of which are obvious: min_dist is the
    minimum distance between particles, min and max_rad are the limits the circles can have in radius. p1 and p2 are 
    less intuitive. p1 should be bigger than p2 and is related to the threshold applied to finding edges. p2 
    is related to the threshold for what constitutes a circle. Low p2 results means you will
    "find" more circles but if too low they'll likely be spurious circles.

4. Display the circles found.
    Whilst adjusting the tracking parameters it is helpful to see what you are finding. Select the annotation
    tab and check the box on this tab to make it active. Initially nothing happens! Go back to the 
    track tab. To estimate roughly the size of the eyes. Move your mouse to the left hand edge of the iris of one eye and double left click.
    A green bar pops up indicating the coordinate that you clicked. Note this down and move to the right hand edge of an eye
    and double click again (The numbers are also printed to the terminal). We can use these numbers to guestimate the approximate
    radius. We don't need to be too precise but if we leave this range large it will seriously slow down the finding of circles.
    We estimate about 35 pixels. The scale for the min_rad and max_rad are not very helpful. Select the cog next to each one and in the 
    pop up boxes type 1, 50, 2 respectively. This adjusts everything to a more usable range. 
    Now we set min_rad to 31 and max_rad to 35. We can do this by dragging and dropping the sliders or typing in the spinbox and hitting
    enter on the keyboard. We could also set min_dist to be at least 200. 
    Now reduce the values of p1 and p2 considerably. We found p1 at 57 and p2 at 7 worked well. 
    Try playing with other values however as it will give you a feel for how it can take a bit of fiddling! Check the tracking
    on different frames by moving the frame_selector slider. Whilst performing
    this optimisation it is helpful to see the size of circles being found by the algorithm. In the annotation
    tab under rad_from_data select True. This now displays the radius measured with Hough circles. 

.. figure:: /resources/eyes3.png
    :width: 400
    :align: center

5. Perform an initial check of the linking
    At this point we have simply found the position of the eyes in each image. However, and this is increasingly
    important with more particles, we need to link the positions between each frame so that we can label the tracked
    objects as eye 1 and eye 2 for example. It can be helpful to display the particle number on the image also. Do this by
    selecting particle labels from the dropdown menu in the annotate tab. At this stage the numbers are actually bogus but
    once we have linked the particles in each frame together these identify which particle is which in each frame and can be useful for example in retrieving
    the data associated with a particular particle. Select the link tab. In more complicated tracking scenarios we may well
    fail to track a particle in every frame and so these parameters enable us to compensate for this. However, for this
    setup the linking is somewhat trivial. Set min_frame_life = 1 . This is the minimum number of frames a particle can exist for before
    we count it as a transient and therefore unimportant thing. This can be useful to get rid of spurious tracking events
    or to slim the data down to just particles tracked over many frames. We also need to allow the max_frame_displacement to be large.
    If we don't adjust this then if the tracking jumps slightly the linking algorithm may assume this is a new particle. We 
    set this to 50.

6. Check the tracking and watch the output.
    To check whether the tracking and linking are working well in other frames, we could move the frame number slider below the image. But there are
    quite a few images and this might take a while. Also this method has its limitations as we'll show in later
    examples. Click "Process" on the toolbar icons. Then if you look in the testdata folder there will be a new mp4
    called eyes_annotate.mp4. Watching this video we observe a few things. Firstly, the particle numbers are 0 and 1 at both the end 
    and the beginning of the video. If they weren't that would mean our linking wasn't working well. Secondly, the tracking is generally very good, however the circles,
    particularly for the right hand eye, appear to jump around a little from frame to frame. If our framerate is high enough that we can be 
    confident this is a tracking thing rather than an actual movement of the eye we can use some averaging to reduce this.

7. Perform some smoothing using a running average
    A good way to implement smoothing is to use the rolling mean or median in postprocessing to smooth the x and y coordinates. Click on the postprocessing
    tab and select mean twice from the drop down. Set the column_name to "x" and "y" for each method respectively. Set the 
    output_column to "x_mean" and "y_mean". The number of frames used to calculate the average ("span") is currently 5. To make the selection
    active we must check the checkbox on the postprocess tab. Now in the annotation section set the "xdata_column" and "ydata_column" to "x_mean" and "y_mean". 
    A rolling mean (like many postprocessing methods) relies on the information from other frames. We can only do this therefore if we have either already run 
    "Process" or alternatively we could have used "Process Part" which does not run the postprocess or annotate sections.
    To indicate that we want to interact with this processed data we now select the "Use part processed" toggle button on the toolbar.
    Make the postprocessing active by checking the checkbox on the tab. The rolling mean averages the values over a window of "span" frames which can be adjusted.
    The first few frames will no longer display a circle since there aren't enough preceding frames to perform the calculation. However, if 
    we move the slider to a different frame we will see the circles reappear. It is hard to tell by looking
    at the isolated frames whether this has improved anything. However, if we again click "Process" and then look at the 
    eyes_annotated.mp4 video it is clear that the tracking is much less jumpy.

8. Accessing the data
    Once we are satisfied that the data is tracked properly we will probably want to calculate something
    meaningful with it. During the processing of a video the data is automatically stored in a <moviename>.hdf5 file.
    The standard approach would be to use python to interact with this data. In later examples we will explore
    the example Jupyter notebook that illustrates very simply how to extract and manipulate the data. However, some users 
    may prefer just to extract the data in a simple excel file. For simple projects where the amount of data is small 
    this is fine. We do however emphasise that as the number of particles and frames increases this will become
    almost unworkable. To extract a copy of the data using excel you must toggle on the excel icon on the toolbar. When you now 
    click "Process" or "Process part" a file named <moviename>.xlsx will also be generated in the same folder as the 
    movie.

.. figure:: /resources/eyes4.png
    :width: 400
    :align: center

9. Repeating the processing for other videos
    When you run "Process" in addition to the annotated video and the data files the software also produces a 
    <moviename>_expt.param file. This file records all the settings used in the processing of the particular video.
    You can also save the settings from any open workspace by using the "Save Settings File" and giving the file a 
    custom name. You can use these files to repeat the processes above almost instantly. Within the gui new movies can be loaded
    and these settings files also loaded using the icons on the toolbar. Alternatively, if using python 
    you can supply the path and filename of the settings filename as keyword arguments to the track_gui. These files can
    also be used with the track_batchprocess() method to process a whole folder of videos using the same settings. See :ref:`Batch Processing<Batch>`
    
    :ref:`Example 2 <Example2>` 

