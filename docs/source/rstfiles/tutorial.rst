How to use Particle Tracker
===========================

Particle Tracker provides a bunch of options of tracking particles.
There are 4 main methods that are used.

1. TrackPy an existing particle tracking library (`Trackpy <http://soft-matter.github.io/trackpy/v0.4.2>`_)
2. Opencv Hough Circles
3. a. Opencv Contour finding
   b. Rotated Bounding Box finding. This is essentially the same as 3a
      However, it is useful since it retrieves the orientation of objects
      if they are not round as well as things like aspect ratio etc.

To track an object there are several steps

1. Crop and mask the image to remove any unwanted bits of images
   that might produce spurious results.
2. Preprocess the images for tracking. Different methods require
   different things. Some need binary images, others need grayscale
   it is highly likely that the software will complain a lot if you get
   this wrong!
3. Track. Use one of the above methods
4. Link the tracks together so that you know which particle is
   which in corresponding frames
5. Postprocess. Calculate results based on the tracking. For example
   you might want to know which particles are neighbours or how
   fast particles are moving.
6. Annotate. This is useful for checking your tracking is working as expected
   but also to visualise values. eg you could colour code the value of the
   order parameter on each particle to see if they are clustered.

How do you start?
-----------------

First thing to do is play with some of the testdata which are 3 short
mp4s in the testdata folder. Run the gui from Main.py and open the correct
movie. Then open the .param file by the same name in the project > param_files folder.
This will apply these settings to analyse that video and should work. To see
the results you will need to tick the annotate box on the tabbed checkboxes.

You can change the order of methods in each section by dragging and dropping. To
stop a method being applied you can drag it below inactive. To remove it completely
right click on it. This will still keep the same values in the dictionary. To add
it back in select the method from the drop down and click add method.

Each method has various sliders and text boxes below. To adjust the min
and max of each slider you can right click.

Once you are happy save the .param file. You can then reload this later.

Some methods need data from more than one frame. This is often the case for postprocessing
and annotation. To do this click "process_part" when you are told the processing is finished
click the "use_part" check button. The software now uses the stored data for the postprocessing
and annotation.

When you are completely happy press "process" this processes the movie according
to all the tabs you have checked. It will produce a vidname.hdf5 file with the data
and if you have annotation selected a vidname_annotated.mp4 which shows the annotations
you asked for.

You may eventually find that you are simply using the same param file. It is possible to batch process all
the videos in one folder using the batchprocess.py in the utility folder. This will
take a pathname with wildcard characters and process any files that match the pattern
with the setting of the .param file supplied.
