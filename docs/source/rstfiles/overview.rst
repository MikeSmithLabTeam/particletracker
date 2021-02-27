Overview of tracking projects
=============================

In this overview we explain the basic principles.

Understanding tracking
----------------------

To build a tracking project there are several steps

1. Crop and mask the image to remove any unwanted bits of images
   that might produce spurious results.
2. Preprocess the images for tracking. Different methods require
   different things. Some need binary images, others need grayscale
   it is highly likely that the software will complain a lot if you get
   this wrong!
3. Track - which means to locate the position of objects within a frame. 
   There are 4 main methods that are currently implemented in this software:

   1. TrackPy an existing particle tracking library (`Trackpy <http://soft-matter.github.io/trackpy/v0.4.2>`_)
   2. Opencv Hough Circles
   3. a. Opencv Contour finding
      b. Rotated Bounding Box finding. This is essentially the same as 3a
         However, it is useful since it retrieves the orientation of objects
         if they are not round as well as things like aspect ratio etc.
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
all future tracking. 


Basic orientation for using the track_gui
-----------------------------------------

The track_gui is divided into a few key areas:

- Toolbar / Menus
- The Viewer
- Process Selectors
- Method Selectors
- Parameter Adjustors

Toolbar / Menus
---------------

The icons and file menu enable you to:
.. image:: icons\icons\folder-open-film.png
  :width: 40
  :alt: Open a movie
Open a new movie.

.. image:: icons\icons\script-import.png
  :width: 40
  :alt: Load Settings
Load a settings .param file

.. image:: icons\icons\script-export.png
  :width: 40
  :alt: Save Settings
Save the current settings to a .param file 

.. image:: icons\icons\arrow-circle.png
  :width: 40
  :alt: Live Update
Toggle the live updates. If you are working with big images or the tracking method is slow for
your dataset you don't want the gui to update every time you change a single parameter. If you toggle
the live updates button this won't update until you toggle it back on. 

.. image:: icons\icons\clapperboard--minus.png
  :width: 40
  :alt: Process Part
"Process part" this runs all the checked processes from experiment, crop, preprocess, track and link on the 
entire movie. It won't do any postprocessing or annotating. Its often helpful to split the process up into 
two parts. You can't run certain postprocess or annotation algorithms on the processing of a single frame. For
example if you want to plot the trajectories of a particle you need the info from other frames. However,
you don't want to have to recalculate everything every time you try a new method in the gui. You can
therefore do the hard work of finding positions and linking (the first part) and then interact with 
that data in the gui on a frame by frame basis until you have everything the way you want it.

.. image:: icons\icons\fire--exclamation.png
  :width: 40
  :alt: Use part
In order to interact with the data for this Processed part you need to click this icon. 

.. image:: icons\icons\clapperboard--arrow.png
  :width: 40
  :alt: Process
When everything is completely setup you can process the entire thing by clicking the Process button.

.. image:: icons\icons\cross-button.png
  :width: 40
  :alt: Close
Close the software.

The Viewer
----------

The viewer displays a single frame from your movie with the annotations if you have added these.
Since most tracking projects require you to preprocess the image you can also view the preprocessed
image by toggling the button "Preprocessed Image". This is particularly useful in optimising the 
parameters before tracking. It is also useful to toggle between the preprocessed image and the tracked
image with some form of annotation to assess whether the tracking could be improved by improving the 
preprocessing. There is also a slider with spinbox to allow you to scroll through the frames in the
movie. The slider auto updates but the spinbox only updates after you hit the enter key.

To zoom in on a part of the image drag and hold the right mouse button. Click and hold the left mouse button
enables you to pan around the image. To reset the zoom double click the right mouse button. Double clicking the
left mouse button will print the coordinates and image intensities to the terminal window.

The Method Selectors
--------------------

Within any tab for each section of the tracking process the top half of the gui displays the methods.
A method can be added by selecting from the drop down menu and clicking "Add Method". Initially
this will appear at the bottom of the list as is "inactive". The methods can be activated by dragging
and dropping them into the list above the "----inactive----" place holder. The methods are run in the order
from top to bottom that they are listed in this dialogue. To remove a method temporarily move it 
below "----inactive----". To remove it more permanently you can right click on the method and it will disappear.
In some cases you may want to apply the same method more than once with different parameters. This 
is not allowed for tracking methods but can be done for other processes. Simple readd the method. This will
create a "methodname*1", "methodname*2" etc which can then be setup.

Parameter Adjustors
-------------------

Each method has a set of parameters that need to be adjusted in order for it to work. These differ
from method to method. These appear dynamically for all active methods in the bottom right hand 
side of the gui. There are two main types of adjustor:
-Sliders with a spinbox. The limits of the sliders can be adjusted using the settings icon. This requires
some care as we don't check that the new limits you put in are acceptable and hence there is a risk of crashing.
-Text boxes. Here the input may be quite varied. If you are unsure you can consult the reference for 
each method.
The crop section has a slightly different interface. One can manually enter the coordinates for a crop
or mask functon but this is not recommended. Click the check box and then on the image click and hold the left
mouse button and drag the shape and release to select the appropriate area. Afterwards the areas can be adjusted binary
adjusting the handles. Once finished uncheck the check box to apply the crop or mask. This can be readjusted
at any future point by simply rechecking the check box. Finally one can remove the crop / masks by clicking
the reset button.



