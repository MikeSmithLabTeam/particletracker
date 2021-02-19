Example 1.  Simple use of trackpy
================================

Example 1 uses the trackpy library (http://soft-matter.github.io/trackpy/v0.4.2/)

Open the gui by running:

.. code-block::python
   from ParticleTracker import track_gui
   track_gui()
code

Open the movie example1.mp4 and then load the settings file example1.param. 

1. We'll start by cropping and masking the image to get rid of the bits we don't need.

Select the crop tab. Next to crop box select the check box. On the image click, hold and drag to
select a region. Once you release you can readjust it with the handles. When happy uncheck the
check box. Since this is a 4k image we can untoggle the live_update button (circular arrow on toolbar)
to speed things up. This saves updating after every little change. 

Currently, the Methods section (top right) says mask_ellipse. Since we want to mask a
hexagon we'll change this. Right click on mask_ellipse and then select mask_polygon from the dropping
down menu. Click add method and then drag the method above the "----inactive----" and below the crop.
A new set of param adjustors called mask_polygon appears bottom right. Select the checkbox and then click
at each point inside the hexagon. Hit Enter on the keyboard if you want to adjust any of the positions
or alternatively just uncheck the checkbox if happy. 

To see the results we need to turn live_update back on so toggle the button. Inorder to see the effect
of the mask we need to look at the preprocessed image. We can view this by clicking the button below the 
main image. 







play with some of the testdata which are 3 short
mp4s in the testdata folder. Run the gui from Main.py and open the correct
movie. Then open the .param file by the same name in the project > param_files folder.
This will apply these settings to analyse that video and should work. To see
the results you will need to tick the annotate box on the tabbed checkboxes. This and postprocessor
are by default unselected.

Each step in the tracking process is only applied if the checkbox on the tab is ticked.
Once selected you need to set up the methods in that section. You can change the order of methods in each section by dragging and dropping. To
stop a method being applied you can drag it below inactive. To remove it completely
right click on it. This will still keep the same values in the dictionary. To add
it back in select the method from the drop down and click add method.
Each method has various sliders and text boxes below. To adjust the min
and max of each slider you can right click.

The image can be cropped and masked using the tools. With all these methods, toggle the button
to begin, drag a rectangle for crop or mask ellipse or click the image to select vertices for mask
polygon. Once happy toggle the button back and the crop or mask will update.

The viewer can show you the image with annotations or if you toggle the button below it
it will show you the image after preprocessing. Drag and hold the right mouse button to
zoom in on an area. Double click the right button to zoom right out.

Once you are happy save the .param file. You can then reload this later.

Some methods need data from more than one frame. This is often the case for postprocessing
and annotation. To use these methods click "process_part". When you are told the processing is finished
click the "use_part" check button. The software now uses the stored data for the postprocessing
and annotation.

When you are completely happy press "process" this processes the movie according
to all the tabs you have checked. It will produce a vidname.hdf5 file with the data in the same folder
as the video being processed. If you have annotation selected a vidname_annotated.mp4 which shows the annotations
you asked for. It will also copy the .param file renaming it vidname.param to this folder so that you have a copy
of the parameters used to process. All these processes overwrite without checking!

You may eventually find that you are simply using the same param file. It is possible to batch process all
the videos in one folder using the batchprocess.py in the utility folder. This will
take a pathname with wildcard characters and process any files that match the pattern
with the setting of the .param file supplied.
