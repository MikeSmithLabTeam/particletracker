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

   1. `Opencv Hough Circles <https://docs.opencv.org/4.x/da/d53/tutorial_py_houghcircles.html>`_ 
   2. `Trackpy <http://soft-matter.github.io/trackpy/stable>`_ an existing particle tracking library for tracking "blobs"
   3. `Opencv Contour finding <https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html#gadf1ad6a0b82947fa1fe3c3d497f260e0>`_
       

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

Watch the video

.. raw:: html

   <iframe width="560" height="315" src="https://www.youtube.com/embed/ajEp18opM-Y" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write;      encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe> 
    

The track_gui is divided into a few key areas: Toolbar / Menus, the Viewer, the Settings Panel

.. figure:: /resources/gui.png
   
Toolbar / Menus
---------------

The icons and file menu enable you to: Open a new movie, load a settings .param file, save the current settings to a .param file, choose a file to act as the default settings, toggle the live updates, view data, export processed results to excel
This option enables you to select if the results will also be published to an excel file.

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

* scroll wheel zooms on image
* right mouse button hold and drag zooms on selected region
* left mouse button hold and drag pans zoomed image
* double-click right mouse button resets zoom
* double-click left mouse button displays coordinates and image intensities at clicked point.

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

* Sliders with a spinbox. The limits of the sliders can be adjusted using the settings icon. This requires some care as we don't check that the new limits you put in are acceptable and hence there is a risk of crashing.
* Drop down menus with a fixed list of choices.
* Text boxes. Here the input may be quite varied. If you are unsure you can consult the reference for each method.

The crop section has a slightly different interface. One can manually enter the coordinates for a crop
or mask functon but this is not recommended. Click the check box and then on the image click and hold the left
mouse button and drag the shape and release to select the appropriate area. Afterwards the areas can be adjusted
using the handles. Once finished uncheck the check box to apply the crop or mask. This can be readjusted
at any future point by simply rechecking the check box. Finally one can remove the crop / masks by clicking
the reset button. 



