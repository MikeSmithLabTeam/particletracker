.. _Example3:
Example 3 - Swelling Hydrogels
==============================


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
    bounds on the aspect ratio and area of the particles. 









