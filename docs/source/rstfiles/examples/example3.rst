.. _Example3:

Example 3 - Swelling Hydrogels
==============================

Read below or watch the video:

.. raw:: html

   <iframe width="560" height="315" src="https://www.youtube.com/embed/i0CKKcwwyGY&list=PL56zLBbX0yZZw18yyMM9tD0fLrobmdbJG&index=4&ab_channel=MikeSmith" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write;      encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe> 

Open track_gui and load the movie hydrogel.mp4

.. figure:: /resources/hydrogel1.png
    :width: 400
    :align: center

This example we are going to use a movie of some hydrogel particles swelling with time.
We will use the contours method to find the outline of the hydrogel particles. This method
requires a black and white image from which the different separate objects can be 
identified.

1. Crop and mask.
    Some of this image for example the black regions down each edge is not needed. Use the crop 
    tool as we did for example 1. Check the checkbox and then drag across the image the region of interest. 
    When finished uncheck the tools checkbox.

2. Preprocess the image
    Toggle the Preprocessed Image button below the main viewer to see the changes taking affect.

    Add the following methods to the image in this order:
    - grayscale
    - medianblur
    - adaptive_threshold

    Our aim is to prepare the image so that the objects are nicely separated and in white. Since Our
    particles are darker than the image under adaptive threshold we set ad_mode to True. Play with the
    sliders and watch the changes. Try setting C to 1 and block_size to 205. This gives a really nice 
    separation. Some objects are still slightly connected but we won't worry about that. 

.. figure:: /resources/hydrogel2.png
    :width: 400
    :align: center

3. Track
    In the track tab if not already selected pick contours from the drop down list and add method. Toggle the image back to 
    "Captured Image". 

    To check that the objects are being found nicely in the image we now need annotation. Check the checkbox
    on the tab labelled annotation. The gui places a small circle over the centroid of each tracked object.
    However, since the method is finding contours change the annotation. Add a contours method from the
    annotation panel and right click on the circles method to remove it. The contours are now highlighted.

4. Refine the tracking
    Some objects which are not hydrogel particles have been highlighted. A lot of these are long and thin or
    have a small area compared to the hydrogel particles. In the tracking tab we can select the 
    bounds on the aspect ratio and area of the particles to eliminate these. We choose "area_min" = 203, "area_max" = 2000, "aspect_min"=1, "aspect_max"=2.00.
    This removes some of the spurious particles. 
    
5. Colour code the data for visualization
    Nearly all of the annotation features have two kinds of colour mapping: "static" and "dynamic". The "dynamic" colour maps enable
    you to locally colour code the annotated feature according to some property of the measured particle. This could be the velocity
    of the particles or any column which has numerical data for each particle. Here in a somewhat silly example we will use 
    the x coordinate of each particle so that the behaviour is really obvious. Select dynamic next to cmap_type. Then type x in the cmap column.
    This is just the name of the column used to define the colour of each particle. We can then define the range of the colours using
    the cmap_min (0) and cmap_max (1900.00). Another perhaps more useful property for contours is "area". 
    This is calculated automatically during tracking of contours. Type "area" into the 
    cmap_column.  Change the ranges of the colour map. To change the range since 1500 is beyond the default range we simply click the cog next
    to the slider and specify the new range. 


.. figure:: /resources/hydrogel4.png
    :width: 400
    :align: center


5. Calculate the voronoi network
    Sometimes it can be useful to compare the size of a particle to the area around it that it can move in.
    One way to do this is using a voronoi network. Right click on contours to remove this annotation and then
    add voronoi under the postprocess tab and also add voronoi under the annotate tab. This will calculate and display
    the voronoi network. In the process it will also generate a column called "voronoi_area" which contains the area
    associated with each particle. You could use this for example to calculate the local density of particles. 
    With some methods the user specifies the output column. However, there are a number of methods where the new column name is chosen automatically.
    You can find out the details for each method in the notes section in the reference for each function on the 
    readthedocs page.

.. figure:: /resources/hydrogel3.png
    :width: 400
    :align: center


6. Process the entire video.
    Click "Process" to gather the data.


:ref:`Example 4<Example4>` 






