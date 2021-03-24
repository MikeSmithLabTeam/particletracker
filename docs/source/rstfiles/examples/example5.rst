.. _Example5:

Example 1.  Simple use of trackpy
=================================

Example 1 uses the trackpy library (http://soft-matter.github.io/trackpy/v0.4.2/)

In this first example we'll go slowly speeding up in future examples as you become more familiar 
with the tools.

Either open the gui from the executable or by running the following python code in a script:

.. code-block:: python
   
   from ParticleTracker import track_gui
   track_gui()


Open the movie example1.mp4 and then load the settings file example1.param. Both of these files
are included in the testdata folder.

1. We'll start by cropping and masking the image to get rid of the bits we don't need.

Select the crop tab. Next to crop box select the check box. On the image click, hold and drag to
select a region. Once you release you can readjust it with the handles. When happy uncheck the
check box. Since this is a 4k image we can untoggle the live_update button (circular arrow on toolbar)
to speed things up. This saves updating after every little change. 

Currently, the Methods section (top right) says mask_ellipse. Since we want to mask a
hexagon we'll change this. Right click on mask_ellipse and then select mask_polygon from the drop
down menu. Click add method and then drag the method above the "----inactive----" and below the crop.
A new set of param adjustors called mask_polygon appears bottom right. Select the checkbox and then click
at each point inside the hexagon. Uncheck the checkbox if happy. 

To see the results we need to turn live_update back on so toggle the button. Inorder to see the effect
of the mask we need to look at the preprocessed image. We can view this by clicking the button below the 
main image. The preprocessed image is the image that the tracking is being performed on. 

