.. _Overview:

Overview of tracking projects
=============================

In this overview we explain the basic principles.

Understanding tracking
----------------------

To build a tracking project there are several steps

1. Crop and mask the image to remove any unwanted bits of images
   that might produce spurious results.
2. Preprocess the images for tracking. Different methods require
   different things. Some need binary black and white images, others need grayscale.
   You can also perform a lot of operations to improve how easy it is to track the 
   objects you're interested in.
3. Track - which means to locate the position of objects within a frame. 
   There are 3 main methods that are currently implemented in this software:

   1. Opencv Hough Circles
   2. TrackPy an existing particle tracking library (`Trackpy <http://soft-matter.github.io/trackpy/v0.4.2>`_)
   3. Opencv Contour finding 
       

4. Link the tracks together so that you know which particle is
   which in consecutive frames
5. Postprocess. Calculate results based on the tracking. For example
   you might want to know which particles are neighbours or how
   fast particles are moving.
6. Annotate. This is useful for checking your tracking is working as expected
   but also to visualise values. eg you could colour code the value of an
   order parameter on each particle to see if they are clustered.

In general we use the track_gui to optimise all these different stages. However, once we have found
the optimum set of conditions for tracking the settings can be saved to a .param file and used to setup
all future tracking. Then if necessary you can automatically process batches of movies with the same settings.


Basic orientation for using the track_gui
-----------------------------------------
Read below or watch the video:

.. raw:: html
    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; height: auto;">
        <iframe src="https://www.youtube.com/embed/ajEp18opM-Y" frameborder="0" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
    </div>
    
    

The track_gui is divided into a few key areas:

- Toolbar / Menus
- The Viewer
- The Settings Panel

.. figure:: /resources/gui.png
   

Toolbar / Menus
---------------

The icons and file menu enable you to:

- Open a new movie.
- Load a settings .param file
- Save the current settings to a .param file 
- Choose a file to act as the default settings
- Toggle the live updates. 

If you are working with big images or the tracking method is slow for
your dataset you don't want the gui to update every time you change a single parameter. If you toggle
the live updates button this won't update until you toggle it back on. 

- Export processed results to excel

This option enables you to select if the results will also be published to an excel file.

- "Process part" 

This runs all the checked processes from experiment, crop, preprocess, track and link on the 
entire movie. It won't do any postprocessing or annotating. Its often helpful to split the process up into 
two parts. You can't run certain postprocess or annotation algorithms on the processing of a single frame. 
For example if you want to plot the trajectories of a particle you need the info from other frames. However,
you don't want to have to recalculate everything every time you try a new method in the gui. You can
therefore do the hard work of finding positions and linking (the first part) and then interact with 
that data in the gui on a frame by frame basis until you have everything the way you want it.

- "Use part"

Once you have processed the first 5 stages using "Process part" you can toggle the use_part button.
Having done this the software uses the stored data to perform calculations in postprocessing and for 
annotation. That is the software does not track objects whilst this button is on.

- "Process"

When everything is completely setup you can process the entire movie by clicking the Process button. This runs
all the stages that are selected. It will produce a <moviename>.hdf5 file and if selected an annotated version
of the movie called <moviename>_annotated.mp4. It will also produce a <moviename>_expt.param which is a copy 
of the settings file used to process the data. This gives you a permanent record of the settings used to 
process a particular movie and can also be used to process other videos with the same settings.

- Close the software.

The Viewer
----------

The viewer displays a single frame from your movie with the annotations if you have added these.
Since most tracking projects require you to preprocess the image you can also view the preprocessed
image by toggling the button "Preprocessed Image". This is particularly useful in optimising the 
parameters before tracking. It is also useful to toggle between the preprocessed image and the tracked
image with some form of annotation to assess whether the tracking could be improved by improving the 
preprocessing. There is also a slider with spinbox to allow you to scroll through the frames in the
movie. The slider auto updates when released, the spinbox updates after you hit the enter key. You can
also limit the range of frames being processed by selecting the settings wheel.

You can interact with the image:

- scroll wheel zooms on image
- right mouse button hold and drag zooms on selected region
- left mouse button hold and drag pans zoomed image
- double-click right mouse button resets zoom
- double-click left mouse button displays coordinates and image intensities at clicked point.

The Settings Panel
------------------

The settings panel consists of a series of tabs. Each tab connects to a different stage of the tracking process
outlined above. Each tab has a checkbox which indicates whether the actions on this tab are active or not.
Within each tab there are two sections: "Method Selectors" and "Parameter Adjustors" 

The Method Selectors
--------------------

Within each tab, the top half of the Settings Panel displays the methods.
A method can be added by selecting from the drop down menu and clicking "Add Method". Initially
this will appear at the bottom of the list below "----inactive----" place holder. The methods can be activated by dragging
and dropping them (left mouse button) into the list above the "----inactive----" place holder. The methods are run in the order,
from top to bottom, that they are listed in this dialogue. To remove a method temporarily move it 
below "----inactive----". To remove it more permanently you can right click on the method and it will disappear.
In some cases you may want to apply the same method more than once with different parameters. This 
is not allowed for tracking methods but can be done for other processes. This will
create a "methodname*1", "methodname*2" etc which can then be setup.

Parameter Adjustors
-------------------

Each method has a set of parameters that need to be adjusted in order for it to work. These differ
from method to method. These appear dynamically for all active methods in the bottom of the settings 
panel. There are several types of adjustor:

- Sliders with a spinbox. The limits of the sliders can be adjusted using the settings icon. This requires some care as we don't check that the new limits you put in are acceptable and hence there is a risk of crashing.
- Drop down menus with a fixed list of choices.
- Text boxes. Here the input may be quite varied. If you are unsure you can consult the reference for each method.

The crop section has a slightly different interface. One can manually enter the coordinates for a crop
or mask functon but this is not recommended. Click the check box and then on the image click and hold the left
mouse button and drag the shape and release to select the appropriate area. Afterwards the areas can be adjusted
using the handles. Once finished uncheck the check box to apply the crop or mask. This can be readjusted
at any future point by simply rechecking the check box. Finally one can remove the crop / masks by clicking
the reset button. 



